# GUIA Y TUTORIAL PARA LA INSTALACION Y USO DEL SISTEMA DE DETECCION DE SONIDO E IMAGEN DEL PROYECTO SMART-CITIES

Este tutorial tiene como intención el guiar en la preparación del ambiente virtual y puesta en marcha de los diferente modelos implementados en el proyecto desde cero, asi como la actualización del firmware y posibles mejoras realizadas. 

## AMBIENTE VIRTUAL.
Para el uso del firmware es necesario de la versión de pyhton 3.10.12. Para instalar Python 3.10 en Ubuntu, puedes utilizar el PPA de `deadsnakes`. Sigue estos pasos:

```bash
sudo apt update
```

**Instalar las dependencias necesarias:**
```bash
sudo apt install software-properties-common
```

**Agregar el PPA de `deadsnakes`:**
```bash
sudo add-repository ppa:deadsnakes/ppa
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

Luego de la instalación de Python3.10 es necesario crear el ambiente virtual, mediante el comando:

**En primer lugar se debe instalar el paquete de entorno virtual de python3.10** (si no está instalado)
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

pip install -r requirements.txt
```

## MODELOS DE IMAGEN Y AUDIO. 



