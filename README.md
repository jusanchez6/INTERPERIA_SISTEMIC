# GUIA Y TUTORIAL PARA LA INSTALACION Y USO DEL SISTEMA DE DETECCION DE SONIDO E IMAGEN DEL PROYECTO SMART-CITIES

Este tutorial tiene como intención el guiar en la preparación del ambiente virtual y puesta en marcha de los diferente modelos implementados en el proyecto desde cero, asi como la actualización del firmware y posibles mejoras realizadas. 

## Tabla de Contenidos
1. [Instalación de la imagen de Ubuntu](#instalación-de-la-imagen-de-ubuntu)
2. [Ambiente virtual de Python](#ambiente-virtual)
3. [Modelos de imagen y audio](#modelos-de-imagen-y-audio)
    - [Modelo de Audio](#modelo-de-audio)
    - [Modelo de Imagen](#modelo-de-imagen)


## Instalación de la imagen de Ubuntu
Para la instalación del sistema operativo en la **Khadas Vim3** lo primero es tener a la mano una memoria SD, un adaptador USB y dirigirse a la siguiente página: https://dl.khadas.com/products/vim3/firmware/oowow/. Aquí encontrará la imagen del asistente para la instalación del sistema operativo, una vez descargado el archivo, copielo en la memoria SD e introduzca esta memoria en la Vim3.

No siempre es necesario, pero si se inserta la memoria SD y no va directamente al asistente de instalación, se debe poner en Upgrade mode, para esto es necesario mantener presionado el botón de POWER en la VIM3 mientras se presiona de manera corta el botón de Reset y se suelta, se debe mantener el botón de POWER presionado otros 2-3 segundos.

Al encender la Vim3, verá como se encuentra en un asistente para la instalación del sistema operativo, siga los pasos de conectividad a internet y una vez tenga que elegir la imagen del sistema operativo que desea instalar, baje en el menú y elija `vim3-ubuntu-24.04-gnome-linux-5.15-fenix-1.6.9-240618.img.xz` Esta imagen corresponde a la versión 24.04 LTS de Ubuntu, y por el momento funciona de manera correcta con el hardware y software implementado. Para mas información sobre las imagenes de los sistemas operativos revise: https://docs.khadas.com/products/sbc/vim3/os-images/start

Siga los pasos que le indique el asistente de instalación y una vez concluya extraiga la SD de la Vim3 y reinicie la tarjeta.


## Ambiente Virtual
Se va a trabajar el ambiente virtual de Python en la carpeta de INTERPERIA SISTEMIC que se puede acceder por Github, para configurar esto, seguir lo descrito en la [documentación extra](./extras/extra_documentation.md#repositorio-de-github). Para el uso del firmware es necesario de la versión de Python 3.10.12. Para instalar Python 3.10.12 en Ubuntu, puedes utilizar el PPA de `deadsnakes`. Sigue estos pasos y recuerda estar conectado a internet:

```bash
sudo apt update
```

**Instalar las dependencias necesarias:**
```bash
sudo apt install software-properties-common
```

**Agregar el PPA de `deadsnakes`:**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```

**Actualizar la lista de paquetes nuevamente:**
```bash
sudo apt update
```
**Instalación de Python 3.10:**
```bash
sudo apt install python3.10
```

**Finaliza la instalación verificando la versión con el siguiente comando:** 
```bash
python3.10 --version
```
Es importante que si en esta parte no se muestra la versión 3.10.12, se siga lo explicado en la [documentación extra](./extras/extra_documentation.md#instalación-de-python-31012) para así tener la versión correcta.

Luego de la instalación de Python3.10.12 es necesario crear el ambiente virtual, mediante el comando:

**En primer lugar se debe instalar el paquete de entorno virtual de python3.10**
```bash
sudo apt install python3.10-venv
```

**Luego de la instalación se puede ejecutar el comando:**
```bash
python3.10 -m venv [myenv]
```

`[myenv]` puede ser reemplazado por el nombre del entorno virtual que se elija. 

Para finalizar la preparación del ambiente virtual es necesario instalar las librerias mediante el uso de los siguientes comandos

```bash
source [myenv]/bin/activate
sudo apt-get install build-essential python3-dev pkg-config libhdf5-dev
```
Si este segundo comando genera problemas, hacer un `sudo apt-get update` o un `sudo apt --fix-missing`. Se acaba el proceso con:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## MODELOS DE IMAGEN Y AUDIO
Si se desea y su editor preferido es VS Code, se anexa un tutorial corto de su instalación en la [documentación extra](./extras/extra_documentation.md#vs-code-para-vim3).
### MODELO DE AUDIO
Para la red de Audio, en la carpeta se encuentra el archivo ```test_model_audio.py``` el cual contiene un ejemplo de uso de la red. Entre las funciones principales se encuentran:
+ ```grabar_audio```: Obtiene un audio de 4 seunfos y lo guarda como "mi_grabacion.wav"
+ ```ind_predict_ARQ4_TL```: Realiza la inferencia de un modelo de detección de eventos de audio

El ejemplo de uso presentado en el archivo se muestra a continuación:
```bash

print(f"\n\n----------------------Processing  ---------------------")

# Prepare audio file
grabar_audio(duracion=4, nombre_archivo="mi_grabacion.wav")
audio_file="scream_test.wav"
prepare_audio(audio_file)

print("----------------------Predicción Con Audio de prueba---------------------")
a=ind_predict_ARQ4_TL(audio_file, input3, output3, interpreter3)

print("a: ",a)


```
Por Algún motivo Felipe, puso funciones que también se utilizan para el procesamiento del audio (y más adelante verás que también para el procesamiento de imagene) en archivos separados, lo que dificulta el entendimiento del codigo, pues hay que estar moviendose entre archivos, la función de grabar audio puede incluirse ahi, pero es mejor echarle un ojo antes a que las librerias que se usen sean las mismas. 

Al ejecutar el siguiente comando, se podrá ver el funcionamiento del script de prueba:
```bash
python3.10 test_model_audio.py
```

### Modelo de Imagen



Para el modelo de imagen la camara requiere de una configuración previa, con el entorno virtual activado, lo primero será ejecutar los siguientes dos comandos:

```bash
sudo apt update
sudo apt install gstreamer-aml
```

El gstreamer es el programa encargado de crear el pipeline necesario para la captura de imahgenes, aunque hay documentación del uso de python con open CV **la implementación no fue posible.** Dentro de los archivos presentes en este repositorio se encontrara con los siguientes archivos: ```mipi.c```, ```mipi_stream.c``` y sus respectivos ejecutables. 

Estos archivos corresponden a los scripts que permiten el control de la cámara. Para la compilación de los archivos en C, se ejecuta el siguiente comando:

```bash
gcc -o mipi mipi-camera.cpp -lopencv_imgproc -lopencv_core -lopencv_videoio -
lopencv_imgcodecs -lopencv_highgui -std=c++11 -std=gnu++11 -Wall -std=c++11 -
lstdc++ -I/usr/include/opencv4
```

*Aunque en el repositorio se adjuntan los archivos compilados, se recomienda compilarlos para la verificación de las librerias instaladas y del correcto funcionamiento del script, ademas de la selección del modo de toma (multitoma, toma única)*

Una vez obtenidos los ejecutables, desde el terminal se puede ejecutar el siguiente comando, el cual mostrará el funcionamiento de la cámara:

```bash
./mipi /dev/video50"
```

Este comando dependiendo del modo de funcionamiento seleccionado puede tomar varias imagenes a una tasa de 23 fps o podrá tomar una sola imagen y guardarla, a continuación se muestra los dos codigos:


1. **MODO MULTITOMA**
```c
const int FRAME_RATE = 23; // Tasa de fotogramas deseada

int main(int argc, char** argv)
{
    if (argc != 2) {
        cerr << "Uso: " << argv[0] << " <dispositivo>" << endl;
        cerr << "Ejemplo: " << argv[0] << " /dev/video0" << endl;
        return -1;
    }

    string str = argv[1];

    string gstformat = "NV12";
    string gstfile = "v4l2src device=" + str + " ! video/x-raw,format=" + gstformat + ",width=1920,height=1080,framerate=30/1 ! videoconvert ! appsink";
    VideoCapture capture(gstfile);

    if (!capture.isOpened()) {
        cerr << "Error al abrir la c�mara." << endl;
        return -1;
    }

    cout << "Iniciando captura a " << FRAME_RATE << " FPS. Presione Ctrl+C para detener." << endl;

    int frame_count = 0;
    auto frame_duration = std::chrono::milliseconds(1000 / FRAME_RATE);

    while (true) {
        auto start_time = std::chrono::high_resolution_clock::now();
        
        Mat frame;
        capture >> frame;

        if (frame.empty()) {
            cerr << "No se pudo capturar el frame." << endl;
            continue;
        }

        string filename = "current_frame.jpg";
        bool success = imwrite(filename, frame);

        if (success) {
            cout << "Frame guardado como " << filename << endl;
            frame_count++;
        } else {
            cerr << "Error al guardar el frame." << endl;
            break;
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        auto elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        
        // Esperar el tiempo restante para alcanzar la tasa de fotogramas deseada
        if (elapsed_time < frame_duration) {
            std::this_thread::sleep_for(frame_duration - elapsed_time);
        }
    }

    capture.release();
    return 0;
}
```

2. **MODO TOMA UNICA**
```c
int main(int argc, char** argv)
{
    if (argc != 2) {
        cerr << "Uso: " << argv[0] << " <dispositivo>" << endl;
        cerr << "Ejemplo: " << argv[0] << " /dev/video0" << endl;
        return -1;
    }

    string str = argv[1];

    // Configuración de GStreamer
    string gstformat = "NV12";
    string gstfile = "v4l2src device=" + str + " ! video/x-raw,format=" + gstformat + ",width=1920,height=1080,framerate=30/1 ! videoconvert ! appsink";
    VideoCapture capture(gstfile);

    if (!capture.isOpened()) {
        cerr << "Error al abrir la cámara." << endl;
        return -1;
    }

    cout << "Capturando un frame. Presione Ctrl+C para detener." << endl;

    Mat frame;
    capture >> frame;  // Captura un único frame

    if (frame.empty()) {
        cerr << "No se pudo capturar el frame." << endl;
        return -1;
    }

    string filename = "single_frame.jpg";
    bool success = imwrite(filename, frame);  // Guarda el frame

    if (success) {
        cout << "Frame guardado como " << filename << endl;
    } else {
        cerr << "Error al guardar el frame." << endl;
    }

    capture.release();  // Libera la captura
    return 0;
}
```
Para utilzar un modo o el otro basta con comentar el código no deseado y ejecutar el comando de compilación y ejecución mostrados previamente. 

**EL TUTORIAL LLEGA HASTA ACA DADO QUE NO SE ENCUENTRA EL MODELO DE INFERENCIA DE LAS IMAGENES**

## TAREAS PENDIENTES 
- [ ] Organizar librerias en la carpeta .lib (crear la carpeta)
- [ ] Encontrar el modelo para la inferencia de las imagenes, debe ser `.pt` o `.pth`
- [ ] Organizar la documentacion de los docstrings para que la reconozca dpoxygen
- [ ] Conectar el quectel 4G


