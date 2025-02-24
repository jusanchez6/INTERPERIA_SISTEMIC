##
# 
# @file image_processing.py
#
# @brief Este módulo contiene funciones para dividir una imagen en partes más pequeñas y
# calcular la entropía y complejidad de las imágenes.
#
# @section funcs Funciones:
# - start_points: Genera los puntos de inicio para dividir una imagen en partes más pequeñas.
# - split_image: Divide una imagen en partes más pequeñas.
# - calculate_entropy: Calcula la entropía de una imagen.
# - calculate_complexity: Calcula el índice de complejidad de una imagen.
# - discard_images: Descarta imágenes que caen por debajo de los umbrales de entropía y complejidad.
# - extract_and_save_frame: Extrae el primer frame de un video .mp4 y lo guarda como un archivo .png.
# - gen_frames: Genera un flujo de imágenes en un hilo separado en el modo multitoma y las envía a través de HTTP.
# - run_terminal_command: corre un comando en el terminal.
#
# @author: Felipe Ayala
# @author: Julian Sanchez
# @author: Maria del Mar Arbelaez
#
# @date: 2025-01-19
#
# @version: 1.0
#
# @copyright SISTEMIC 2025
##

from PIL import Image, ImageFilter
import numpy as np
import os
import imageio
import glob
import subprocess
import threading
from time import sleep


def start_points(size, split_size, overlap=0):
    """Genera los puntos de inicio para dividir una imagen en partes más pequeñas.
    Args:
        size (int): Tamaño de la imagen.
        split_size (int): Tamaño de la división.
        overlap (float): Porcentaje de superposición entre divisiones.
    Returns:
        range: Puntos de inicio.
    """
    stride = int(split_size * (1 - overlap))
    return range(0, size, stride)

def split_image(file, output_directory, split_width, overlap_percentage):
    """Divide una imagen en partes más pequeñas,  no retorna nada, guarda la
        imagen recortada en output_directory.
    Args:
        file (str): Ruta de la imagen.
        output_directory (str): Directorio de salida.
        split_width (int): Ancho de las divisiones.
        overlap_percentage (float): Porcentaje de superposición entre divisiones.

    """
    img = Image.open(file)
    img_w, img_h = img.size
    X_points = start_points(img_w, split_width, overlap_percentage)
    Y_points = start_points(img_h, split_width, overlap_percentage)
    
    for y_point in Y_points:
        for x_point in X_points:
            img_cropped = img.crop(box=(x_point, y_point, x_point + split_width, y_point + split_width))
            name_image = f"{x_point}_{y_point}.png"
            
            # Si el directorio de salida no existe, se crea
            os.makedirs(output_directory, exist_ok=True)
            img_cropped.save(os.path.join(output_directory, name_image))
    print("images saved")

def calculate_entropy(image):
    """Calcula la entropía de una imagen
    
    Args:
        image (PIL.Image): Imagen a procesar.

    Returns:
        float: Entropía de la imagen.
    """
    histogram = image.histogram()
    histogram_length = sum(histogram)
    samples_probability = [float(h) / histogram_length for h in histogram]
    return -sum([p * np.log2(p + 1e-7) for p in samples_probability if p != 0])

def calculate_complexity(image):
    """Calcula el índice de complejidad de una imagen

    Args:
        image (PIL.Image): Imagen a procesar.

    Returns:
        float: Índice de complejidad de la imagen.
    """
    # Convertir la imagen a escala de grises
    gray_image = image.convert('L')
    # Calcular el gradiente de la imagen utilizando el operador Sobel
    gradient_x = np.abs(np.asarray(gray_image.filter(ImageFilter.Kernel((3, 3), (-1, 0, 1, -2, 0, 2, -1, 0, 1))))).sum()
    gradient_y = np.abs(np.asarray(gray_image.filter(ImageFilter.Kernel((3, 3), (-1, -2, -1, 0, 0, 0, 1, 2, 1))))).sum()
    return (gradient_x + gradient_y) / image.size[0] / image.size[1]

def discard_images(dataset_path, entropy_threshold, complexity_threshold):
    """Descarta imágenes que caen por debajo de los umbrales de entropía y complejidad
    
    Args:
        dataset_path (str): Directorio con las imágenes a procesar.
        entropy_threshold (float): Umbral de entropía.
        complexity_threshold (float): Umbral de complejidad.
    """
    files = glob.glob(f"{dataset_path}/*.png")
    i = 0
    for filename in files:
        image = Image.open(filename)
        entropy = calculate_entropy(image)
        file = filename.split("/")[-1]
        #print(file)
        complexity = calculate_complexity(image)
        #print(entropy, complexity)
        if entropy < entropy_threshold or complexity < complexity_threshold:
            # Si el directorio 'discard' no existe, se crea
            os.makedirs(f"{dataset_path}/discard", exist_ok=True)
            os.rename(f"{dataset_path}/{file}", f"{dataset_path}/discard/{file}")
            i = i + 1
            #os.remove(os.path.join(dataset_path, filename))
    #print(i)

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

def gen_frames():
    """
    Función que genera un flujo de imágenes en formato JPEG. 
    Ejecuta el comando `./frameC /dev/video50` en un hilo separado para capturar las imágenes de un dispositivo de video
    y las envía como un flujo de imágenes JPEG a través de HTTP.

    El flujo generado es compatible con el protocolo `multipart/x-mixed-replace`, utilizado comúnmente para 
    transmisión de video MJPEG en tiempo real.
    """

    # Comando que ejecuta la captura de imágenes del dispositivo de video
    command = "./frameC /dev/video50"

    # Ejecuta el comando en un hilo separado para no bloquear el hilo principal
    threading.Thread(target=run_terminal_command, args=(command,)).start()  # Ejecuta el comando en paralelo
    while True:
        # Ruta del archivo de imagen generado por el comando
        output_image_path = 'current_frame.jpg'

        try:
            # Abre el archivo de imagen en modo de lectura binaria
            with open(output_image_path, 'rb') as f:
                # Lee el contenido del archivo (la imagen JPEG)
                frame = f.read()

                # Genera el flujo multipart para el protocolo MJPEG
                # El flujo se divide en partes separadas por los delimitadores '--frame'
                # Cada parte incluye los encabezados para el tipo de contenido 'image/jpeg' y el contenido de la imagen
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        except FileNotFoundError:
            # Si no se encuentra el archivo, espera 0.1 segundos y vuelve a intentarlo
            # Esto puede ocurrir si el archivo de imagen aún no está disponible
            sleep(0.1)
            continue
        
        except Exception as e:
            # En caso de cualquier otro error, muestra el mensaje de error y termina la ejecución
            print(f"Error al leer el archivo de imagen: {e}")
            break

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
