# -*- coding: utf-8 -*-
import os
import librosa
import numpy as np
import torch
import tensorflow as tf
from scipy.io.wavfile import read, write
from datetime import datetime, timedelta
import time
import threading
from PIL import Image
import imageio
import subprocess
import queue
import signal
import json
from datetime import datetime
import sounddevice as sd
import soundfile as sf
import wave
import pytz
# Import local functions
from audio_processing import prepare_audio, extract_features
from storage_manager import ensure_storage_space, delete_old_files, save_audio
from image_processing import split_image, calculate_entropy, calculate_complexity, discard_images
from test_model import test_model
from vgg_model import ModifiedVGG16Model, FusionVGG16Model




def ind_predict_ARQ4_TL(path, inputM, outputM, interpreterM):
    """
    Realiza la inferencia de un modelo de detección de eventos de audio

    Args:   
        path (str): Ruta del archivo de audio a procesar
        inputM (dict): Información del input del modelo
        outputM (dict): Información del output del modelo
        interpreterM (tf.lite.Interpreter): Modelo de TensorFlow Lite

    returns: 
        JSON con la detección del evento
    """


    # Parámetros del procesamiento de audio
    samplerate = 22050
    longitudMaxAudio = 4
    Nmfcc = 45
    Nfft = 4096
    NwinL = 4096
    NhopL = 4096  # int(iterableNhopL * NwinL)
    num_rows = Nmfcc
    num_columns = int(samplerate * longitudMaxAudio / NhopL) + int(samplerate * longitudMaxAudio / NhopL * 0.05)
    num_channels = 1

    # Extracción de características
    audio = extract_features(path, Nmfcc, Nfft, NhopL, NwinL)
    audioP = audio.reshape(1, num_rows, num_columns, num_channels)
    input_data = audioP
    
    # Inferencia con el modelo
    interpreterM.set_tensor(inputM['index'], input_data)
    interpreterM.invoke()
    output_data_3 = interpreterM.get_tensor(outputM['index'])

    # Inicialización de variables de detección
    tipo = "Audio"
    deteccion = None
    nivel_confianza = None
    
    # Condiciones de detección
    if output_data_3[0][1] >= 0.70:
        deteccion = "disparo"
        nivel_confianza = output_data_3[0][1]
    elif output_data_3[0][2] >= 0.55:
        deteccion = "sirena"
        nivel_confianza = output_data_3[0][2]
    elif output_data_3[0][3] >= 0.70:
        deteccion = "grito"
        nivel_confianza = output_data_3[0][3]

    # Si se detectó algún evento, retornar el JSON
    if deteccion is not None:
        # Obtén la hora actual en la zona horaria de Bogotá
        timezone_bogota = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(timezone_bogota).isoformat()

        #convertir a float- Julian 10 de octubre 2024
        nivel_confianza = float(nivel_confianza) if isinstance(nivel_confianza, np.float32) else nivel


        result = {
            "tipo": tipo,
            "detección": deteccion,
            "fecha": fecha_actual,  # Fecha y hora en zona horaria de Bogotá
            "nivel_confianza": nivel_confianza
        }



        return json.dumps(result, indent=4)

    # Si no hay detección
    return None



def grabar_audio(duracion=4, nombre_archivo="grabacion.wav", tasa_muestreo=44100, canales=1):
    """
    Graba audio de 4 segunfos y lo guarda en un archivo WAV

    Args:
        duracion (float): Duración de la grabación en segundos
        nombre_archivo (str): Nombre del archivo WAV
        tasa_muestreo (int): Tasa de muestreo en Hz
        canales (int): Número de canales

    Returns:
        None
    """
    print(f"Grabando {duracion} segundos...")
    myrecording = sd.rec(int(duracion * tasa_muestreo), samplerate=tasa_muestreo, channels=canales)
    sd.wait()  # Esperar hasta que la grabación se complete
    sf.write(nombre_archivo, myrecording, tasa_muestreo)
    print(f"Archivo guardado como {nombre_archivo}")
#
# Configuración de valores por defecto
filePathSave = "/mnt/sdcard/tempAudio.wav"
max_segments_size_gb = 2.0
max_events_size_gb = 1.0
days_to_keep_storage = 0
audio_file = "gunshot_test.wav"
# Especifica la ruta de tu archivo de audio aquí

# # Configuration Parameters
# conf1 = 0.97  
# conf2 = 0.97
# conf3 = 0.80

# # Define model paths
# fusedModelSavePathGun_TL_4_tflite = "models/saved_gunshot_TL_4.tflite"
# fusedModelSavePathSiren_TL_4_tflite = "models/saved_siren_TL_4.tflite"
# fusedModelSavePathScream_TL_4_tflite = "models/saved_scream_TL_4.tflite"
path_3="models/saved_gun_scream_siren_TL_4.tflite"


# # Load TFLite models
# interpreterGun = tf.lite.Interpreter(model_path=fusedModelSavePathGun_TL_4_tflite)
# interpreterSiren = tf.lite.Interpreter(model_path=fusedModelSavePathSiren_TL_4_tflite)
# interpreterScream = tf.lite.Interpreter(model_path=fusedModelSavePathScream_TL_4_tflite)
interpreter3=tf.lite.Interpreter(model_path=path_3)


# interpreterGun.allocate_tensors()  # Needed before execution!
# interpreterSiren.allocate_tensors()  # Needed before execution!
# interpreterScream.allocate_tensors()  # Needed before execution!
interpreter3.allocate_tensors()



input3=interpreter3.get_input_details()[0]
output3=interpreter3.get_output_details()[0]


# inputGun = interpreterGun.get_input_details()[0]  # Model has single input.
# outputGun = interpreterGun.get_output_details()[0]  # Model has double output.

# inputSiren = interpreterSiren.get_input_details()[0]  # Model has single input.
# outputSiren = interpreterSiren.get_output_details()[0]  # Model has double output.

# inputScream = interpreterScream.get_input_details()[0]  # Model has single input.
# outputScream = interpreterScream.get_output_details()[0]  # Model has double output.

print(f"\n\n----------------------Processing  ---------------------")

# Prepare audio file
grabar_audio(duracion=4, nombre_archivo="mi_grabacion.wav")
audio_file="scream_test.wav"
prepare_audio(audio_file)

print("----------------------Predicción Con Audio de prueba---------------------")
a=ind_predict_ARQ4_TL(audio_file, input3, output3, interpreter3)

print("a: ",a)
