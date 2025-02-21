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

# PATH DEL MODELO
MODEL_PATH = "../../.lib/audio_model/models/saved_gun_scream_siren_TL_4.tflite"

# PATH DEL DELEGATE
DELEGATE_PATH = "./libarmnnDelegate.so.29"

# Configuración de valores por defecto
filePathSave = "sample_sounds/mi_grabacion.wav"
AUDIO_PATH = "sample_sounds/siren_test.wav"

# Map the tag output to the appropriate string
TAGS = {
        0:'scream',
        1:'gunshot',
        2:'siren',

}


DURATION = 4
SR = 22050

armnn_delegate = tflite.load_delegate(
    library = DELEGATE_PATH,
    options = {
        "backends":BACKENDS,
        "logging-severity": "info",
    }
)

interpreter = tflite.Interpreter(
    model_path = MODEL_PATH,
    experimental_delegates = [armnn_delegate]
)

interpreter.allocate_tensors()


input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# gunshot test -> 4.07s 4.04s 4.05s
# scream test -> 3.88s 3.91s 3.96s
# siren test -> 3.97s 3.96s 3.97s 

#En general, parece que se demora siempre 4s, mirar si con la NPU esto disminuye, pero lo dudo