from pathlib import Path

main_path = Path("priiloader/src/Installer/source/main.cpp")
make_path = Path("priiloader/src/Installer/Makefile")

src = main_path.read_text()

def replace_once(old, new, label):
    global src
    if old not in src:
        raise SystemExit(f"Could not find expected source block: {label}")
    src = src.replace(old, new, 1)

replace_once(
    "#include <wiiuse/wpad.h>\n",
    "#include <wiiuse/wpad.h>\n#include <ogc/usb.h>\n#include <wiikeyboard/usbkeyboard.h>\n",
    "wpad include",
)

keyboard_code = r'''
/*
 * USB keyboard support added to the Priiloader 0.10.0 installer.
 * ENTER / keypad ENTER = install/update/confirm
 * ESC / SPACE          = cancel/back
 *
 * Removal is deliberately not mapped to the keyboard.
 */
enum
{
    KBD_INSTALL = (1 << 0),
    KBD_CANCEL  = (1 << 1)
};

static volatile u32 _kbd_pressed = 0;
static bool _kbd_initialized = false;
static lwp_t _kbd_thread_handle = LWP_THREAD_NULL;
static volatile bool _kbd_should_quit = false;

static void KBEventHandler(USBKeyboard_event event)
{
    if(event.type != USBKEYBOARD_PRESSED && event.type != USBKEYBOARD_RELEASED)
        return;

    u32 button = 0;
    switch(event.keyCode)
    {
        case 0x28: // Enter
        case 0x58: // Keypad Enter
            button = KBD_INSTALL;
            break;
        case 0x29: // Escape
        case 0x2C: // Space
            button = KBD_CANCEL;
            break;
        default:
            break;
    }

    if(event.type == USBKEYBOARD_PRESSED)
        _kbd_pressed |= button;
    else
        _kbd_pressed &= ~button;
}

static void *KeyboardThread(void *arg)
{
    while(!_kbd_should_quit)
    {
        if(!USBKeyboard_IsConnected() && USBKeyboard_Open(KBEventHandler) >= 0)
        {
            // Wake keyboards that need an initial output report.
            USBKeyboard_SetLed(USBKEYBOARD_LEDCAPS, false);
        }

        USBKeyboard_Scan();
        usleep(400);
    }
    return NULL;
}

static void KeyboardInit()
{
    if(_kbd_initialized)
        return;

    USB_Initialize();
    USBKeyboard_Initialize();
    _kbd_should_quit = false;

    LWP_CreateThread(
        &_kbd_thread_handle,
        KeyboardThread,
        NULL,
        NULL,
        16 * 1024,
        50
    );

    _kbd_initialized = true;
}

static u32 KeyboardButtonsDown()
{
    KeyboardInit();
    usleep(800);
    u32 pressed = _kbd_pressed;
    _kbd_pressed = 0;
    return pressed;
}

'''

replace_once(
    "void sleepx (int seconds)\n",
    keyboard_code + "void sleepx (int seconds)\n",
    "sleepx insertion point",
)

replace_once(
    "\t\tWPAD_ScanPads();\n\t\tPAD_ScanPads();\n\t\tpDown = WPAD_ButtonsDown(0);\n\t\tGCpDown = PAD_ButtonsDown(0);\n\t\tif (pDown & WPAD_BUTTON_A || GCpDown & PAD_BUTTON_A)\n",
    "\t\tWPAD_ScanPads();\n\t\tPAD_ScanPads();\n\t\tu32 kDown = KeyboardButtonsDown();\n\t\tpDown = WPAD_ButtonsDown(0);\n\t\tGCpDown = PAD_ButtonsDown(0);\n\t\tif (pDown & WPAD_BUTTON_A || GCpDown & PAD_BUTTON_A || (kDown & KBD_INSTALL))\n",
    "UserYesNoStop confirm",
)

replace_once(
    "\t\tif (pDown & WPAD_BUTTON_B || GCpDown & PAD_BUTTON_B)\n",
    "\t\tif (pDown & WPAD_BUTTON_B || GCpDown & PAD_BUTTON_B || (kDown & KBD_CANCEL))\n",
    "UserYesNoStop cancel",
)

replace_once(
    "\tWPAD_Init();\n\tPAD_Init();\n\tsleepx(5);\n",
    "\tWPAD_Init();\n\tPAD_Init();\n\tKeyboardInit();\n\tsleepx(5);\n",
    "main input init",
)

replace_once(
    'printf("\\r\\t         Press (+/A) to install or update Priiloader\\r\\n");',
    'printf("\\r\\t   Press (+/A/ENTER) to install or update Priiloader\\r\\n");',
    "install prompt",
)

replace_once(
    'printf("\\t    Press (HOME/Start) to chicken out and quit the installer!\\r\\n\\r\\n");',
    'printf("\\t Press (HOME/Start/ESC) to chicken out and quit the installer!\\r\\n");\n\tprintf("\\t        USB keyboard: ENTER=install, ESC/SPACE=cancel\\r\\n\\r\\n");',
    "cancel prompt",
)

replace_once(
    "\t\tu16 pHeld = WPAD_ButtonsHeld(0);\n\t\tu16 GCpHeld = PAD_ButtonsHeld(0);\n",
    "\t\tu16 pHeld = WPAD_ButtonsHeld(0);\n\t\tu16 GCpHeld = PAD_ButtonsHeld(0);\n\t\tu32 kDown = KeyboardButtonsDown();\n",
    "main keyboard scan",
)

replace_once(
    "\t\tif (pDown & WPAD_BUTTON_PLUS || GCpDown & PAD_BUTTON_A)\n",
    "\t\tif (pDown & WPAD_BUTTON_PLUS || GCpDown & PAD_BUTTON_A || (kDown & KBD_INSTALL))\n",
    "install condition",
)

replace_once(
    "\t\telse if ( GCpDown & PAD_BUTTON_START || pDown & WPAD_BUTTON_HOME) \n",
    "\t\telse if ( GCpDown & PAD_BUTTON_START || pDown & WPAD_BUTTON_HOME || (kDown & KBD_CANCEL)) \n",
    "cancel condition",
)

main_path.write_text(src)

mk = make_path.read_text()
old_libs = "LIBS\t:=\t-ldb -lwiiuse -lbte -logc -lfat"
new_libs = "LIBS\t:=\t-lwiikeyboard -ldb -lwiiuse -lbte -logc -lfat"
if old_libs not in mk:
    raise SystemExit("Could not find expected LIBS line in Installer Makefile")
mk = mk.replace(old_libs, new_libs, 1)
make_path.write_text(mk)

print("Keyboard support injected successfully.")


# Priiloader 0.10.0's loader Makefile predates newer devkitPPC/libogc
# platform selection. Current wii_rules exposes the Wii target flags in
# $(MACHDEP), so make sure the tiny loader is compiled with them too.
loader_make_path = Path("priiloader/src/loader/Makefile")
loader_mk = loader_make_path.read_text()
old_loader_flags = "CFLAGS\t\t=\t-Os $(INCLUDE) -save-temps -fno-asynchronous-unwind-tables -fno-builtin"
new_loader_flags = "CFLAGS\t\t=\t-Os $(MACHDEP) $(INCLUDE) -save-temps -fno-asynchronous-unwind-tables -fno-builtin"
if old_loader_flags not in loader_mk:
    raise SystemExit("Could not find expected CFLAGS line in loader Makefile")
loader_mk = loader_mk.replace(old_loader_flags, new_loader_flags, 1)
loader_make_path.write_text(loader_mk)
print("Modern devkitPPC Wii target flags added to loader.")


# Compatibility fixes for libogc versions current in 2026.
system_menu_path = Path("priiloader/src/priiloader/source/SystemMenu.cpp")
system_menu = system_menu_path.read_text()

old_tmd_call = "ES_GetTMDView(TitleID, (u8*)rTMD, tmd_size)"
if system_menu.count(old_tmd_call) != 2:
    raise SystemExit("Unexpected number of legacy ES_GetTMDView calls")
system_menu = system_menu.replace(old_tmd_call, "ES_GetTMDView(TitleID, rTMD, tmd_size)")

old_iv = "static const u8 vwii_ancast_iv[0x10]"
if old_iv not in system_menu:
    raise SystemExit("Could not find legacy vWii AES IV declaration")
system_menu = system_menu.replace(old_iv, "static u8 vwii_ancast_iv[0x10]", 1)

system_menu_path.write_text(system_menu)
print("Modern libogc SystemMenu compatibility fixes applied.")


titles_path = Path("priiloader/src/priiloader/source/titles.cpp")
titles_src = titles_path.read_text()
old_titles_call = "ES_GetTMDView(title_list[i], (u8*)rTMD, tmd_size)"
if old_titles_call not in titles_src:
    raise SystemExit("Could not find legacy ES_GetTMDView call in titles.cpp")
titles_src = titles_src.replace(old_titles_call, "ES_GetTMDView(title_list[i], rTMD, tmd_size)", 1)
titles_path.write_text(titles_src)
print("Modern libogc titles compatibility fix applied.")


ios_path = Path("priiloader/src/Shared/IOS.cpp")
ios_src = ios_path.read_text()
old_ios_call = "ES_GetTMDView(0x0000000100000000ULL | ios_number, (u8*)ios_tmd, tmd_size)"
if old_ios_call not in ios_src:
    raise SystemExit("Could not find legacy ES_GetTMDView call in Shared/IOS.cpp")
ios_src = ios_src.replace(
    old_ios_call,
    "ES_GetTMDView(0x0000000100000000ULL | ios_number, ios_tmd, tmd_size)",
    1
)
ios_path.write_text(ios_src)
print("Modern libogc Shared/IOS compatibility fix applied.")
