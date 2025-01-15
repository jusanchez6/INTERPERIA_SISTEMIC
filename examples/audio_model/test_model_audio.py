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
from audio_model.audio_processing import *
import tensorflow as tf

# Configuración de valores por defecto
filePathSave = "sample_sounds/mi_grabacion.wav"
audio_file = "sample_sounds/siren_test.wav"

# # @section Configure Parameters
# - conf1 = 0.97  
# - conf2 = 0.97
# - conf3 = 0.80

## @section Define model paths
#  + "models/saved_gunshot_TL_4.tflite"
#  + "models/saved_siren_TL_4.tflite"
#  + "models/saved_scream_TL_4.tflite"
path_3="../../.lib/audio_model/models/saved_gun_scream_siren_TL_4.tflite"


# # Load TFLite models
interpreter3=tf.lite.Interpreter(model_path=path_3)

interpreter3.allocate_tensors() #Needed before execution!

input3=interpreter3.get_input_details()[0] #Model has single input.
output3=interpreter3.get_output_details()[0] #Model has single output.

enter=input(f"\nUse sample audios? y/n ")
if(enter != "y"):
    print(f"\n\n----------------------Processing  ---------------------")
    # Prepare audio file
    grabar_audio(duracion=4, nombre_archivo=filePathSave)

    #Comentar si se quiere probar con el archivo de prueba
    audio_file=filePathSave

start = time.time()
prepare_audio(audio_file)

print("----------------------Predicción Con Audio de prueba---------------------")
a=ind_predict_ARQ4_TL(audio_file, input3, output3, interpreter3)
end = time.time()
print("a: ",a)
print("Tiempo de preparación y predicción: ",end - start)


# gunshot test -> 4.07s 4.04s 4.05s
# scream test -> 3.88s 3.91s 3.96s
# siren test -> 3.97s 3.96s 3.97s 

#En general, parece que se demora siempre 4s, mirar si con la NPU esto disminuye, pero lo dudo