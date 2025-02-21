##
# @file test_model_audio.py
# 
# @brief Este script contiene un test del funcionamiento del modelo de audio,
# dando la opción de usar los audios de prueba o grabar uno con el micrófono que esté
# conectado.
# 
# @author : Felipe Ayala
# @author : Julian Sanchez
# @author : Maria del Mar Arbelaez
# 
# @date: 2024-10-24
# 
# @version: 1.0
# 
# @copyright SISTEMIC 2024
##

#esto es para medir el tiempo de ejecución
import time

# Importar libreria de manejo de audio
#from audio_model.audio_processing import *
#import tensorflow as tf

#
# Librerias para el uso del tflite 
#
import numpy as np
import tflite_runtime.interpreter as tflite
import sounddevice as sd
import librosa
import sys

import subprocess

sys.path.append("../../.lib/audio_model")  # Agregar la ruta a `sys.path`
from audio_processing import *  # Ahora Python puede encontrar el módulo

# Set the path to the TFLite delegate:
#DELEGATE_PATH = "./libarmnn_delegate.so.29"

# Model Pat:




# # @section Configure Parameters
# - conf1 = 0.97  
# - conf2 = 0.97
# - conf3 = 0.80

## @section Define model paths
#  + "models/saved_gunshot_TL_4.tflite"
#  + "models/saved_siren_TL_4.tflite"
#  + "models/saved_scream_TL_4.tflite"
path_3="../../.lib/audio_model/models/saved_gun_scream_siren_TL_4.tflite"


command0 = "wget -O ArmNN-aarch64.tgz https://github.com/ARM-software/armnn/releases/download/v24.11/ArmNN-linux-aarch64.tar.gz"
command1 = "mkdir libs"
command2 = "tar -xvf ArmNN-aarch64.tgz -C libs"
command3 = "sudo ln ./libs/delegate/libarmnnDelegate.so.29.1 libarmnnDelegate.so.29"
command4 = "sudo ln ./libs/libarmnn.so.34.0 libarmnn.so.34"



def run_terminal_command(command):
    """
    Ejecuta un comando en la terminal y espera a que termine.

    Args:
        command (str): Comando a ejecutar.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e.stderr.decode()}")

run_terminal_command(command0)
run_terminal_command(command1)
run_terminal_command(command2)
run_terminal_command(command3)
run_terminal_command(command4)


# Preferencias de backend
BACKENDS = "GpuAcc"


MODEL_PATH = "../../.lib/audio_model/models/saved_gun_scream_siren_TL_4.tflite"

# Delegate Path (asegúrate de que el archivo está en la ubicación correcta)
DELEGATE_PATH = "./libarmnnDelegate.so.29"  # Cambia esto si es necesario

# Configuración de valores por defecto
filePathSave = "sample_sounds/mi_grabacion.wav"
AUDIO_PATH = "sample_sounds/siren_test.wav"

# Cargar el modelo con el Delegate ArmNN
armnn_delegate = tflite.load_delegate(
    library = DELEGATE_PATH,
    options = {
        "backends":BACKENDS,
        "logging-severity": "info",
    }
)

interpreter3 = tflite.Interpreter(
    model_path=MODEL_PATH,
    experimental_delegates=[armnn_delegate]
)

interpreter3.allocate_tensors()  # Necesario antes de la ejecución

input3 = interpreter3.get_input_details()[0]  # Modelo con una sola entrada
output3 = interpreter3.get_output_details()[0]  # Modelo con una sola salida

# Preguntar si se quiere grabar audio o usar archivo de prueba
enter = input(f"\nUse sample audios? y/n ")
if enter != "y":
    print(f"\n\n----------------------Processing  ---------------------")
    grabar_audio(duracion=4, nombre_archivo=filePathSave)  # Grabar nuevo audio
    AUDIO_PATH = filePathSave  # Usar el audio grabado

start = time.time()
prepare_audio(AUDIO_PATH)

print("----------------------Predicción Con Audio de prueba---------------------")
a = ind_predict_ARQ4_TL(AUDIO_PATH, input3, output3, interpreter3)
end = time.time()

print("a: ", a)
print("Tiempo de preparación y predicción: ", end - start)



# gunshot test -> 4.07s 4.04s 4.05s
# scream test -> 3.88s 3.91s 3.96s
# siren test -> 3.97s 3.96s 3.97s 

#En general, parece que se demora siempre 4s, mirar si con la NPU esto disminuye, pero lo dudo


# gunshot test -> 3.96s 3.91s 3.88s
# scream test ->  3.81s 3.78s 3.76s
# siren test ->   3.79s 3.84s 3.82s 

# Con la GPU disminuyo ajsdjasdja