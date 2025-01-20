##
# @file python-procesar-frame.py
# 
# @brief Este script contiene el API del server de feed, maybe.
# 
# @section mets Métodos:
# - index: renderizar página principal.
# - video_feed: ejecuta gen_frames con la cámara MIPI para generar un stream.
#
# @section routes Rutas:
# - '/': renderizar página principal.
# - '/video_feed': ejecuta gen_frames con la cámara MIPI para generar un stream.
#
# @author : Felipe Ayala
# @author : Julian Sanchez
# @author : Maria del Mar Arbeláez
# 
# @date: 2025-01-19
# 
# @version: 1.0
# 
# @copyright SISTEMIC 2025
##

# -*- coding: utf-8 -*-
from flask import Flask, render_template, Response
from image_processing import run_terminal_command,gen_frames

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Ruta principal para renderizar la página de inicio
@app.route('/')
def index():
    """
    Ruta principal que sirve el archivo HTML 'index.html' como la página de inicio de la aplicación.
    Esta ruta se encarga de renderizar la página inicial de la aplicación cuando el usuario accede
    a la URL raíz ('/').
    """
    return render_template('index.html')

# Ruta para servir el flujo de video MJPEG
@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    """
    Ruta para servir el flujo de video MJPEG.
    Esta ruta maneja las peticiones 'GET' y 'POST' y genera un flujo en tiempo real de imágenes
    a partir de la función 'gen_frames()' del archivo 'image_processing'. 
    Este flujo de imágenes es entregado en el formato MJPEG (multipart/x-mixed-replace), 
    lo que permite mostrar un video en vivo en la página web.
    
    El flujo se transmite a través de la respuesta HTTP, utilizando el tipo de contenido adecuado
    para transmitir imágenes en formato JPEG de forma continua.
    """
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Si el archivo es ejecutado directamente, arranca el servidor Flask
if __name__ == '__main__':
    """
    Inicia el servidor web Flask en la dirección '0.0.0.0' (lo que permite acceso externo)
    y en el puerto 5000. Además, habilita el modo de depuración (debug=True) para facilitar el desarrollo
    y la depuración del código.
    """
    app.run(host='0.0.0.0', port=5000, debug=True)
