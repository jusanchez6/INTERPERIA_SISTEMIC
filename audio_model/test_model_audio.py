##
# @file test_model_audio.py
# 
# @brief Este script contiene un test del funcionamiento del modelo de audio.
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

# Importar libreria de manejo de audio
from audio_processing import *
import tensorflow as tf

# Configuración de valores por defecto
filePathSave = "sample_sounds/mi_grabacion.wav"
audio_file = "sample_sounds/gunshot_test.wav"

# # @section Configure Parameters
# - conf1 = 0.97  
# - conf2 = 0.97
# - conf3 = 0.80

## @section Define model paths
#  + "models/saved_gunshot_TL_4.tflite"
#  + "models/saved_siren_TL_4.tflite"
#  + "models/saved_scream_TL_4.tflite"
path_3="models/saved_gun_scream_siren_TL_4.tflite"


# # Load TFLite models
interpreter3=tf.lite.Interpreter(model_path=path_3)

interpreter3.allocate_tensors() #Needed before execution!

input3=interpreter3.get_input_details()[0] #Model has single input.
output3=interpreter3.get_output_details()[0] #Model has single output.


print(f"\n\n----------------------Processing  ---------------------")

# Prepare audio file
grabar_audio(duracion=4, nombre_archivo=filePathSave)

#Comentar si se quiere probar con el archivo de prueba
audio_file=filePathSave

prepare_audio(audio_file)

print("----------------------Predicción Con Audio de prueba---------------------")
a=ind_predict_ARQ4_TL(audio_file, input3, output3, interpreter3)
print("a: ",a)