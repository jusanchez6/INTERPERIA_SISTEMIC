# -*- coding: utf-8 -*-
from flask import Flask, render_template, Response
import os
import subprocess
from PIL import Image
import imageio
import cv2
import threading

app = Flask(__name__)

def run_terminal_command(command):
    """
    Ejecuta un comando en la terminal y espera a que termine.

    Args:
        command (str): Comando a ejecutar.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e.stderr.decode()}")

def extract_and_save_frame(video_path, output_image_path):
    reader = imageio.get_reader(video_path, 'ffmpeg')
    
    try:
        frame = reader.get_data(0)
        image = Image.fromarray(frame)
        image.save(output_image_path)
        print(f"Frame guardado exitosamente en {output_image_path}")
    except Exception as e:
        print(f"Error al extraer el frame: {e}")
    finally:
        reader.close()

def gen_frames():
    command = "./frameC /dev/video50"
    threading.Thread(target=run_terminal_command, args=(command,)).start()  # Ejecuta el comando en paralelo
    while True:
        output_image_path = 'current_frame.jpg'
        with open(output_image_path, 'rb') as f:
            frame = f.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
