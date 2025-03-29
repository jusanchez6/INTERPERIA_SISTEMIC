##
# @file audio_processing.py
# 
# @brief Este script contiene funciones para el manejo de archivos de audio.
# 
# @section funcs Funciones:
# - prepare_audio: Prepara el audio para el procesamiento
# - extract_features: Extrae características de un archivo de audio usando la librería de librosa.
# - grabar_audio: Graba audio del dispositivo conectado
# - ind_predict_ARQ4_TL:  Hace la predicción del audio para el evento adecuado.
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

# -*- coding: utf-8 -*-
import os
import librosa
import numpy as np
import tensorflow as tf
from scipy.io.wavfile import read, write
from scipy.signal import resample
from datetime import datetime
import json
from datetime import datetime
import sounddevice as sd
import soundfile as sf
import pytz

def prepare_audio(path):
    """
    Prepara el audio para el procesamiento.
    
    Args:
    - path (str): ruta del audio.
    """
    # Leer el archivo de audio original
    original_sample_rate, audio_data = read(path)

    # Definir la nueva tasa de muestreo deseada
    nueva_tasa_muestreo = 22050  #22.05 kHz
    # Calcular el factor de resampleo
    factor_resampleo = nueva_tasa_muestreo / original_sample_rate
    # Aplicar resampleo
    audio_resampleado = resample(audio_data, int(len(audio_data) * factor_resampleo))
    # Factor de amplificación (1.5 aumentará el nivel de sonido en un 50%)
    factor_amplificacion = 10.0
    # Escalar las muestras del audio para aumentar el nivel de sonido
    audio_amplificado = audio_resampleado * factor_amplificacion
    # Asegúrate de que los valores estén dentro del rango [-32768, 32767] para audio de 16 bits
    audio_amplificado = np.clip(audio_amplificado, -1.0, 1.0)
    # Guardar el archivo de audio resampleado
    #write(path, nueva_tasa_muestreo, audio_resampleado)
    write(path, nueva_tasa_muestreo, audio_amplificado)
    #return 

def extract_features(file_name, Nmfcc, Nfft, NhopL, NwinL):
    """
    Extraer características de un archivo de audio usando la libreria de librosa.
    
    Args:
    - file_name (str): Path to the audio file.
    - Nmfcc (int): Number of MFCC coefficients.
    - Nfft (int): FFT window size.
    - NhopL (int): Hop length.
    - NwinL (int): Window length.
    
    Returns:
    - ndarray: Extracted features.
    """
    samplerate = 22050
    longitudMaxAudio = 4
    max_pad_len = int(samplerate*longitudMaxAudio/NhopL) + int(samplerate*longitudMaxAudio/NhopL*0.05)  #Calculo longitud de salida de mfcc con 5% de tolerancia para longitud de audios

    try:
      audio, sample_rate = librosa.load(file_name, res_type='soxr_hq')
      #print(sample_rate)
      #print(audio)
      mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=Nmfcc, n_fft=Nfft, hop_length=NhopL, win_length=NwinL)
      #print(max_pad_len)
      #print(mfccs.shape[1])
      pad_width = max_pad_len - mfccs.shape[1]
      mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')

    except Exception as e:
      print("Error encountered while parsing file: ", file_name)
      return None
    #print(mfccs.shape)
    return mfccs

def grabar_audio(duracion=4, nombre_archivo="grabacion.wav", tasa_muestreo=44100, canales=1):
    """
    Graba audio de 4 segunfos y lo guarda en un archivo WAV

    Args:
        duracion (float): Duración de la grabación en segundos
        nombre_archivo (str): Nombre del archivo con terminación .WAV
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
            "deteccion": deteccion,
            "fecha": fecha_actual,  # Fecha y hora en zona horaria de Bogotá
            "nivel_confianza": nivel_confianza
        }
        
        return json.dumps(result, indent=4)

    # Si no hay detección
    return None