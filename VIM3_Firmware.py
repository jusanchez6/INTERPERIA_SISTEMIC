# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 11:00:45 2024

@author: felip
"""

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
# Import local functions
from audio_model.audio_processing import prepare_audio, extract_features
from storage_manager import ensure_storage_space, delete_old_files, save_audio
from image_processing import split_image, calculate_entropy, calculate_complexity, discard_images
from test_model import test_model
from vgg_model import ModifiedVGG16Model, FusionVGG16Model
from flask import Flask, render_template , jsonify
import datetime

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


#Load parametrers for weapons CNN

images_directory = "./images_cropped"
output_directory = "./output_images"
split_width = 256
overlap_percentage = 0.6
classes = ["arma de fuego", "no arma de fuego"]
path_model = "model_Vgg16_60_weapons"
q = queue.Queue()


app = Flask(__name__, static_folder='/home/khadas/Desktop/AI_cities/VIM3_Scripts/static')

flag1=True
flag2=True
comienzo=True

class CommandRunner:
    def __init__(self):
        self.process = None
        self.thread = None

    def run_command(self, command):
        def target():
            os.setpgrp()  # Crea un nuevo grupo de procesos
            self.process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
            self.process.wait()

        self.thread = threading.Thread(target=target)
        self.thread.start()

    def stop_command(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)  # Espera hasta 5 segundos para que el proceso termine
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            
            self.process.wait()
            self.thread.join()  # Espera a que el hilo termine
            self.process = None
            self.thread = None


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

def extract_and_save_frame(video_path, output_image_path):
    """
    Extrae el primer frame de un video .mp4 y lo guarda como un archivo .png.

    Args:
        video_path (str): Ruta del archivo de video .mp4.
        output_image_path (str): Ruta donde se guardará el frame extraído como archivo .png.
    """
    # Leer el video
    reader = imageio.get_reader(video_path, 'ffmpeg')
    
    try:
        # Extraer el primer frame
        frame = reader.get_data(0)
        
        # Convertir el frame a una imagen PIL
        image = Image.fromarray(frame)
        
        # Guardar la imagen
        image.save(output_image_path)
        
        #print(f"Frame guardado exitosamente en {output_image_path}")
    except Exception as e:
        print(f"Error al extraer el frame: {e}")
    finally:
        # Cerrar el lector
        reader.close()


def ind_predict_ARQ4_TL(path, inputM, outputM, interpreterM):
    #print(f"Predicting for {path}")
    pre=[0,0,0,0,0,0]
    
    samplerate = 22050
    longitudMaxAudio = 4
    Nmfcc = 45
    Nfft = 4096
    NwinL = 4096
    iterableNhopL = 1.0
    NhopL = 4096       #int(iterableNhopL*NwinL)
    k_size = 5
    num_rows = Nmfcc
    num_columns = int(samplerate * longitudMaxAudio / NhopL) + int(samplerate * longitudMaxAudio / NhopL * 0.05)  # Calculo longitud de salida de mfcc con 5% de tolerancia para longitud de audios
    num_channels = 1

    audio = extract_features(path, Nmfcc, Nfft, NhopL, NwinL)
    audioP = audio.reshape(1, num_rows, num_columns, num_channels)
    input_data = audioP
    #print("INPUT DATA SHAPE", input_data.shape)
    
    interpreter3.set_tensor(inputM['index'], input_data)
    interpreter3.invoke()
    output_data_3 = interpreterM.get_tensor(outputM['index'])
    #print(f"Model 3: {output_data_3[0]}")

    # # Run inference on Gun model
    # interpreterGun.set_tensor(inputGun['index'], input_data)
    # interpreterGun.invoke()
    # output_data_gun = interpreterGun.get_tensor(outputGun['index'])[0]  # Doble indexación
    # print(f"Gun Model Output: {output_data_gun}")

    # # Run inference on Siren model
    # interpreterSiren.set_tensor(inputSiren['index'], input_data)
    # interpreterSiren.invoke()
    # output_data_siren = interpreterSiren.get_tensor(outputSiren['index'])[0]  # Doble indexación
    # print(f"Siren Model Output: {output_data_siren}")

    # # Run inference on Scream model
    # interpreterScream.set_tensor(inputScream['index'], input_data)
    # interpreterScream.invoke()
    # output_data_scream = interpreterScream.get_tensor(outputScream['index'])[0]  # Doble indexación
    # print(f"Scream Model Output: {output_data_scream}")

    # # Perform action based on confidence
    if output_data_3[0][1] >= 0.70:
        pre[0]=1
        pre[3]=output_data_3[0][1]
        #print(f"Event Gunshot detected with confidence {output_data_3[0][1]}")
    if output_data_3[0][2] >= 0.55:
        pre[1]=1
        pre[4]=output_data_3[0][2]
        #print(f"Event Siren detected with confidence {output_data_3[0][2]}")
    if output_data_3[0][3] >= 0.70:
        pre[2]=1
        pre[5]=output_data_3[0][3]
        #print(f"Event Scream detected with confidence {output_data_3[0][3]}")
    return pre

def main_thread(q):
    try:
        print(f"\n\n----------------------Processing {audio_file} ---------------------")
        
        # Prepare audio file
        prepare_audio(audio_file)
        
        print("----------------------Predicción Con Audio Guardado... ---------------------")
        a=ind_predict_ARQ4_TL(audio_file, input3, output3, interpreter3)
        #print("a: ",a)
        q.put(a)
    except KeyboardInterrupt:
        # Manejar la interrupción del teclado (Ctrl + C)
        pass

    finally:
        # No hay configuración de GPIO para limpiar
        pass

def second_thread(q):
    command = "./mipi /dev/video50"
    # Ejecutar el comando de terminal
    #run_terminal_command(command)
    video_path = 'output_test.mp4'
    output_image_path = 'image_test.png'
    extract_and_save_frame(video_path, output_image_path)
    
    file = "image_test2.png"
    split_image(file, images_directory, split_width, overlap_percentage)
    discard_images(images_directory, 7.0, 0.40)
    # Ejemplo de uso



    ## CAMBIAR POR OPENCV y YOLOv8 
    ## PREGUNTAR A RICARDO
    ## -----------------------------

    #waiting for model files to test
    model = torch.load(path_model, map_location=torch.device('cpu'))
    r=test_model(model, images_directory, file, output_directory, split_width, classes)
    #print("r: ",r)

    q.put(r)

def REDN():
    global flag1
    global flag2
    while flag2==True:
        while flag1==True:
            print(flag1)
            
            start_time = time.time()
            # Crear hilos
            thread1 = threading.Thread(target=main_thread, args=(q,))
            thread2 = threading.Thread(target=second_thread,  args=(q,))

            # Iniciar hilos
            thread1.start()
            thread2.start()

            # Esperar a que los hilos terminen
            thread1.join()
            thread2.join()

            sonido=q.get()
            armas=q.get()
            # Obtén la hora actual
            hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Define el archivo de texto donde escribirás los datos
            ruta_archivo = "eventos.txt"

            # Lee el contenido existente del archivo
            with open(ruta_archivo, 'r') as archivo:
                contenido_existente = archivo.readlines()

            # Escribe los nuevos datos seguidos por el contenido existente
            with open(ruta_archivo, 'w') as archivo:
                archivo.write(f"{hora_actual}, {sonido}, {armas}\n")
                archivo.writelines(contenido_existente)

            # print(f"Evento del hilo sonidos: {sonido}")
            # print(f"Evento del hilo de armas: {armas}")
            end_time = time.time()

            # Calcular el tiempo de ejecución
            execution_time = end_time - start_time
            print(f"Tiempo de ejecución: {execution_time} segundos")
        while flag1==False:
            print("espera")
            time.sleep(2)


@app.route('/')
def index():
    global flag1
    flag1=True
    if comienzo==False:
        runner2.stop_command()
        runner3.stop_command()
        run_terminal_command(command0)

    return render_template('main-page-html.html')

@app.route('/video')
def video():
    global flag1
    flag1=False
    
    runner2.run_command(command2)
    time.sleep(10)
    runner3.run_command(command3)
    time.sleep(30)
    print("Funcion")
    return render_template('video.html')

@app.route('/get_messages')
def get_messages():
    messages = []
    try:
        # Asumimos que eventos.txt está en el mismo directorio que el script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'eventos.txt')
        
        with open(file_path, 'r') as file:
            messages = [line.strip() for line in file if line.strip()]
        
        # Si no hay mensajes, agregar un mensaje por defecto
        if not messages:
            messages = ["No hay nuevos eventos."]
    
    except FileNotFoundError:
        messages = ["Error: Archivo eventos.txt no encontrado."]
    except Exception as e:
        messages = [f"Error al leer los eventos: {str(e)}"]
    
    return jsonify({"messages": messages})

if __name__ == '__main__':
    if comienzo==True:
        red_N=threading.Thread(target=REDN)
        red_N.start()
        comienzo=False
        
        command0="rm -rf /home/khadas/Desktop/AI_cities/VIM3_Scripts/static/mystream/*"
        run_terminal_command(command0)

        command1 = "./mediamtx"
        runner1 = CommandRunner()

        command2 = "gst-launch-1.0 -v v4l2src device=/dev/video50 ! video/x-raw,width=1920,height=1080,framerate=30/1 ! videoconvert ! x264enc speed-preset=veryfast tune=zerolatency bitrate=800 ! rtspclientsink location=rtsp://localhost:8554/mystream "
        runner2 = CommandRunner()

        command3 = "ffmpeg -i rtsp://192.168.137.25:8554/mystream -c:v copy -hls_time 2 -hls_list_size 10 -hls_flags delete_segments -start_number 1 /home/khadas/Desktop/AI_cities/VIM3_Scripts/static/mystream/index.m3u8"
        runner3 = CommandRunner()
        

        print("en comienzo....")
    app.run(host='0.0.0.0', port=5000)
    print("despues")
    flag1=False
    flag2=False
    red_N.join()

    


