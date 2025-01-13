# DOCUMENTACIÓN EXTRA PARA LA VIM3
En este archivo se guarda toda la información para configurar aspectos extra del ambiente de la VIM3 para el modelamiento de imágenes y sonidos.

## Tabla de Contenidos

- [DOCUMENTACIÓN EXTRA PARA LA VIM3](#documentación-extra-para-la-vim3)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Repositorio de Github](#repositorio-de-github)
    - [Access Token](#access-token)
    - [SSH](#ssh)
  - [Instalación de Python 3.10.12](#instalación-de-python-31012)
  - [VS Code para VIM3](#vs-code-para-vim3)
  - [Configurar micrófono USB para la lectura](#configurar-micrófono-usb-para-la-lectura)

## Repositorio de Github
En primer lugar, es necesario descargar el repositorio de Github, sin embargo clonarlo no es suficiente, sino que se debe poder hacer pushs y pulls desde la Vim3, por lo que se configurará también para poder hacer esto.

Para que todo esté actualizado:
```bash
sudo apt-get update
```

**Se revisa si ya se tiene `Github` instalado:**
```bash
git --version
```
**Si no se tiene instalado:**
```bash
sudo apt-get install git-all
```
**Para configurar el acceso se requiere acceder a la página de Github por lo que se puede descargar:**
```bash
sudo snap install firefox
```

**Como el repositorio es privado, se requiere primero conectarse a su cuenta de Github:**
```bash
git config --global user.name "Your Username"
git config --global user.email "your_email@example.com"
```

**Para validarse en Github hay dos métodos, por ssh o por Access token, se listan los dos para que cada quien elija.**

### Access Token
- En la parte superior derecha de la página de Github, presionar su foto de perfil y presionar Settings.
- De ahí, en el sidebar de la izquierda, ir a Developer Settings.
- De nuevo, en el sidebar de la izquierda, presionar Tokens (Classic).
- En la esquina derecha de la página, presionar Generate New Token.
- Del listado, escoger Generate New Token (Classic), en Note escribir para qué se usa el token, escoger la fecha de vencimiento del token (Puede ser de 7 días) y escoger el scope del token, en este caso, sería repo.
- Este debe generar un código que se copiará (si no se copia en ese momento es necesario eliminar el token y volver a intentar, ya que solo se muestra una vez) cuando se pida la contraseña al clonar el proyecto:
```bash
git clone https://github.com/jusanchez6/INTERPERIA_SISTEMIC.git
```
Si no se pide en este momento, lo pedirá cuando se haga el primer push, por lo que es bueno no perder el token.

### SSH
**Generar clave ssh:**
```bash
ssh-keygen -o -t rsa -C “ssh@github.com”
```
Cuando se genera, este pide un passphrase que se debe recordar para el final de la operación.
**Verificar nombre del archivo y ubicación correcta:**
```bash
khadas@Khadas cd ~/.ssh
khadas@Khadas ls
id_rsa id_rsa.pub
```
Puede aparecer con otro nombre, pero es bueno verificar, si esto no funciona, volver a intentar el primer paso.

**Copiar la clave generada:**
```bash
cat id_rsa.pub
```
Copiar lo que saque el bash.

**Crear clave en github:**
- En la parte superior derecha de la página de Github, presionar su foto de perfil y presionar Settings.
- De ahí, en el sidebar de la izquierda, ir a SSH and GPG keys.
- En la esquina derecha de la página, presionar New SSH key.
- Agregar un título, dejar el Key Type en Authentication Key y copiar la llave en Key.

**Clonar con el ssh del repositorio:**
```bash
git clone git@github.com:jusanchez6/INTERPERIA_SISTEMIC.git
```
Aquí se pide el passphrase con el que se creó la llave ssh.

Finalmente, así queda el repositorio listo para utilizar.


## Instalación de Python 3.10.12
Para esto, se va a utilizar `pyenv`.

**En primer lugar, se instalan dependencias:**
```bash
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
**Se instala Pyenv:**
```bash
curl https://pyenv.run | bash
```
**Se configuran las variables del ambiente**
```bash
echo -e 'export PYENV_ROOT="$HOME/.pyenv"\nexport PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'eval "$(pyenv init --path)"\neval "$(pyenv init -)"' >> ~/.bashrc
```
**Se refresca el Shell y se confirma que está instalado**
```bash
exec "$SHELL"
pyenv --version
```
**Se instala la versión deseada (3.10.12) y se configura como global:**
```bash
pyenv install 3.10.12
pyenv global 3.10.12
```
También se puede configurar como local, no es necesario en este caso.

## VS Code para VIM3
Se descarga el `.deb` para ARM64 de la siguiente [página](https://code.visualstudio.com/download).

**Instalar desde la carpeta donde se descargó el .deb:**
```bash
sudo dpkg -i ./nombre_del_archivo_descargado.deb
```
Si dice que no se tienen los `xdf-utils`:
```bash
sudo apt-get install xdf-utils
sudo apt-get install -f
```
Configurar VScode como se desee.

## Configurar micrófono USB para la lectura
Es posible que se tenga el "micrófono" del sistema como default para la recepción, por lo que si se conecta algún micrófono USB es bueno ponerlo como default.
**Revisar conexión**
```bash
lsusb
```
Entre los puertos que se muestren tiene que estar el micrófono conectado, si no es así, revisar drivers o conexión física.
Luego se selecciona como `default` abriendo la aplicación de `Settings` y expandiendo la opción de `Sound`, aquí, en la parte de `Input`, seleccionar en la lista expandible el micrófono que se conectó. Así, ya está listo para probar el código de Python.