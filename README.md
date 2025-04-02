# GUIA Y TUTORIAL PARA LA INSTALACION Y USO DEL SISTEMA DE DETECCION DE SONIDO E IMAGEN DEL PROYECTO SMART-CITIES

Este tutorial tiene como intención el guiar en la preparación del ambiente virtual y puesta en marcha de los diferente modelos implementados en el proyecto desde cero, asi como la actualización del firmware y posibles mejoras realizadas. 

Para tutoriales o problemas que puede surgir durante la instalción y uso de este sistema dirijase a la documentación extra proporcionada.

## Tabla de Contenidos
- [GUIA Y TUTORIAL PARA LA INSTALACION Y USO DEL SISTEMA DE DETECCION DE SONIDO E IMAGEN DEL PROYECTO SMART-CITIES](#guia-y-tutorial-para-la-instalacion-y-uso-del-sistema-de-deteccion-de-sonido-e-imagen-del-proyecto-smart-cities)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Instalación de la imagen de Ubuntu](#instalación-de-la-imagen-de-ubuntu)
  - [Clonación del repositorio](#clonación-del-repositorio)
  - [Ambiente virtual](#ambiente-virtual)
  - [Uso de los modelos de imagen y audio.](#uso-de-los-modelos-de-imagen-y-audio)
    - [Modelo de audio](#modelo-de-audio)
    - [Modelo de imagen](#modelo-de-imagen)
  - [I2C](#i2c)
    
   
      



## Instalación de la imagen de Ubuntu
Para la instalación del sistema operativo en la **Khadas Vim3** lo primero es tener a la mano una memoria SD, un adaptador USB y dirigirse a la siguiente página: https://dl.khadas.com/products/vim3/firmware/oowow/. Aquí encontrará la imagen del asistente para la instalación del sistema operativo, una vez descargado el archivo, copielo en la memoria SD e introduzca esta memoria en la Vim3.

No siempre es necesario, pero si se inserta la memoria SD y no va directamente al asistente de instalación, se debe poner en Upgrade mode, para esto es necesario mantener presionado el botón de POWER en la VIM3 mientras se presiona de manera corta el botón de Reset y se suelta, se debe mantener el botón de POWER presionado otros 2-3 segundos.

Al encender la Vim3, verá como se encuentra en un asistente para la instalación del sistema operativo, siga los pasos de conectividad a internet y una vez tenga que elegir la imagen del sistema operativo que desea instalar, baje en el menú y elija `vim3-ubuntu-24.04-gnome-linux-5.15-fenix-1.6.9-240618.img.xz` Esta imagen corresponde a la versión 24.04 LTS de Ubuntu, y por el momento funciona de manera correcta con el hardware y software implementado. Para mas información sobre las imagenes de los sistemas operativos revise: https://docs.khadas.com/products/sbc/vim3/os-images/start

Siga los pasos que le indique el asistente de instalación y una vez concluya extraiga la SD de la Vim3 y reinicie la tarjeta.

## Clonación del repositorio. 

En el directorio raiz de su equipo abra una terminal y ejecute el sigiente comando 
```bash
git clone https://github.com/jusanchez6/INTERPERIA_SISTEMIC.git
cd INTERPERIA_SISTEMIC/
```

Para ir a la carpeta deseada y continuar con el tutorial.


## Ambiente Virtual
Se va a trabajar el ambiente virtual de Python en la carpeta de INTERPERIA SISTEMIC que se puede acceder por Github, para configurar esto, seguir lo descrito en la [documentación extra](./extras/extra_documentation.md#repositorio-de-github). Para el uso del firmware es necesario de la versión de Python 3.10.12. Para instalar Python 3.10.12 en Ubuntu, puedes utilizar el PPA de `deadsnakes`. Sigue estos pasos y recuerda estar conectado a internet:

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10

python3.10 --version
```
**Es importante que si en esta parte no se muestra la versión 3.10.12, se siga lo explicado en la [documentación extra](./extras/extra_documentation.md#instalación-de-python-31012) para así tener la versión correcta.**


Luego de la instalación de Python3.10.12 es necesario crear el ambiente virtual:

```bash
sudo apt install python3.10-venv
python3.10 -m venv [myenv]
source [myenv]/bin/activate
```

Ahora para instalar las dependencias necesarias:

```
sudo apt-get install -y python3-dev python3-pip build-essential libhdf5-dev libffi-dev pkg-config
sudo apt-get install -y gcc-aarch64-linux-gnu g++
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Si encuentra algún problema en la instalación de los pquetes ejecute:**
```bash
sudo apt-get update
pip install --no-cache-dir -r requirements.txt
```

Finalmente para configurar las librerias locales, escriba lo siguiente en el archivo ```[myenv]/bin/activate```

```bash
export PYTHONPATH="/home/khadas/INTERPERIA_SISTEMIC/.lib"
```
**Sin esto no se encontrarán algunas librerías de manera correcta.**

## USO DE LOS MODELOS DE IMAGEN Y AUDIO
A continuación se muestra tutorial corto de su instalación en la [documentación extra](./extras/extra_documentation.md#vs-code-para-vim3).

### MODELO DE AUDIO
Para la red de Audio, en la carpeta se encuentra el archivo ```test_model_audio.py``` el cual contiene un ejemplo de uso de la red que usa un archivo de funciones llamado ```audio_processing.py```. Entre las funciones principales se encuentran:
+ ```grabar_audio```: Obtiene un audio de 4 segundos y lo guarda como "mi_grabacion.wav"
+ ```ind_predict_ARQ4_TL```: Realiza la inferencia de un modelo de detección de eventos de audio
+ ```prepare_audio```: Prepara el audio para el procesamiento
+ ```extract_features```: Extrae características de un archivo de audio usando la librería de librosa.

Para probarlo se puede hacer uso de un [micrófono USB](./extras/extra_documentation.md#configurar-micrófono-usb-para-la-lectura) y ejecute desde la carpeta de ```examples/audio_model ```:

```bash
python3.10 test_model_audio.py
```

### Modelo de Imagen

Para el modelo de imagen la camara requiere de una configuración previa, con el entorno virtual activado, lo primero será ejecutar los siguientes dos comandos:

```bash
sudo apt update
sudo apt install gstreamer-aml
sudo apt install libopencv-dev python3-opencv
```

El gstreamer es el programa encargado de crear el pipeline necesario para la captura de imágenes, aunque hay documentación del uso de python con openCV **la implementación no fue posible.** Dentro de los archivos presentes en este repositorio se encontrará con los siguientes archivos: ```mipi.c```, ```mipi_stream.c``` y sus respectivos ejecutables. 

Estos archivos corresponden a los scripts que permiten el control de la cámara. Para la compilación de los archivos en C, se ejecuta el siguiente comando desde la carpeta de `.lib/mipi_camera`:

```bash
gcc -o mipi mipi-camera.cpp -lopencv_imgproc -lopencv_core -lopencv_videoio -
lopencv_imgcodecs -lopencv_highgui -std=c++11 -std=gnu++11 -Wall -std=c++11 -
lstdc++ -I/usr/include/opencv4
```
Una vez obtenidos los ejecutables, desde el terminal se puede ejecutar el siguiente comando, el cual mostrará el funcionamiento de la cámara:

```bash
./mipi "/dev/video50"
```

En el archivo `test_model.py` dentro de la carpeta de ejemplos se encuentra un script el cual prueba el modelo de inferencia de imagen de manera separada tal como se realizó con el modelo de audio. Para su ejecución es de vital importancia que el incluya las dos funciones del archivo `vgg_model.py` las cuales se incluyen mediante la línea de código:
```python
from vgg_model import ModifiedVGG16Model, FusionVGG16Model
``` 
Estas funciones son las encargadas de darle el atributo de clase al modelo de inferencia `model_Vgg16_60_weapons` el cual se encuentra en el siguiente link y debe ser descargado por aparte debido a las limitaciones de github para la gestión de archivos de grandes tamaños: https://drive.google.com/drive/folders/1UnFmhoa4pKH0X_dmDjfiNESFYX2bcNOL 

Si se busca hacer la descarga de este archivo mediante el terminal revisar la [documentación extra](./extras/headless_setup.md#descarga-del-modelo-de-imagen).

Para más información sobre el acceso al drive escriba al correo: fabian.duque@udea.edu.co

Para el uso de este ejemplo ejecute en la carpeta ```examples/image_model ```
```bash
python3.10 test_model.py
```
## I2C
Dentro de la documentación incluida, también se agrega documentos utilies para la instalación y uso del I2C, asi como esquemas de conexión y programación de la raspberry pi pico w. Refierase a estos archivos para la puesta en marcha de la comunicación serial con la raspberry pi pico W.




 

