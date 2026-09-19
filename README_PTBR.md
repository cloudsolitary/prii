# Priiloader 0.10.0 Installer com teclado USB

Este pacote NÃO contém arquivos proprietários do Wii e NÃO contém um boot.dol pré-compilado.
Ele contém um patch pequeno sobre o código-fonte oficial do Priiloader 0.10.0 e um workflow
do GitHub Actions que compila o instalador usando a imagem oficial devkitPro/devkitPPC.

## O que muda

No instalador:
- ENTER (ou Enter do teclado numérico) = instalar/atualizar / confirmar
- ESC ou ESPAÇO = cancelar / voltar
- Remoção do Priiloader NÃO foi mapeada para o teclado, para evitar remoção acidental.

O Priiloader instalado continua sendo o Priiloader oficial 0.10.0. A alteração é apenas
na interface de entrada do INSTALADOR.

## Como compilar sem instalar ferramentas no Windows

1. Crie um repositório vazio no GitHub.
2. Extraia este ZIP e envie para a raiz do repositório:
   - priiloader_keyboard.patch
   - .github/workflows/build.yml
3. Abra a aba Actions do repositório.
4. Escolha "Build Priiloader 0.10.0 Keyboard Installer".
5. Clique em "Run workflow".
6. Quando terminar, abra a execução e baixe o artifact:
   priiloader-0.10.0-keyboard-installer
7. Extraia o artifact no pendrive:
   USB:/apps/priiloader-keyboard/
      boot.dol
      meta.xml
      icon.png

## No Wii

1. Conecte o teclado USB.
2. Abra o Homebrew Channel.
3. Execute "Priiloader".
4. Espere a tela terminar de inicializar.
5. Pressione ENTER para instalar/atualizar.
6. Ao final, pressione ENTER novamente para sair.

IMPORTANTE:
- Você já possui Priiloader 0.8.2. O instalador deve detectar a instalação e fazer UPDATE.
- Não desligue o Wii durante a escrita/atualização.
- Não escolha remoção.
- Depois de atualizar, entre no Priiloader segurando RESET ao ligar.
- No Priiloader 0.10.0, o teclado USB funciona no menu.

Depois de entrar no Priiloader, para o Fakemote:
Settings -> Use System Menu IOS = OFF
IOS to use for SM = 252
Save Settings

Se o System Menu não iniciar pelo IOS252, volte ao Priiloader segurando RESET e restaure
a configuração anterior.
