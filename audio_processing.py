"""
Este script contiene funciones para procesar archivos de audio.

Funciones:
- prepare_audio: Prepara el audio para el procesamiento.
- extract_features: Extrae características de un archivo de audio usando la librería de librosa.


authosr: Felipe Ayala
        Julian Sanchez

date: 2024-10-24

version: 1.0

SISTEMIC 2024
"""

import os
import numpy as np
from scipy.io.wavfile import read, write
from scipy.signal import resample
import librosa

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
    Extrer características de un archivo de audio usando la libreria de librosa.
    
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