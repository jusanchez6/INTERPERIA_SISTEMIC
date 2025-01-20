##
# @file test_model.py
# 
# @brief Este script contiene un test del funcionamiento del modelo de imagen,
# dando la opción de usar una imagen de prueba, tomar una imagen uno con el micrófono que esté
# conectado.
#  
# @section funcs Funciones:
# - run_terminal_command: Corre un comando por la terminal.
# - extract_features: Extrae características de un archivo de audio usando la librería de librosa.
# - test_model: Realiza la detección de armas en las imágenes de un directorio.
#
#
# @author : Felipe Ayala
# @author : Julian Sanchez
# @author : Maria del Mar Arbelaez
# 
# @date: 2025-01-15
# 
# @version: 1.0
# 
# @copyright SISTEMIC 2025
##

import os
import subprocess
import glob
from PIL import Image, ImageDraw
from torchvision import transforms
import torch
import json
from datetime import datetime
import pytz
#esto es para medir el tiempo de ejecución
import time

from image_model.image_processing import *
from image_model.vgg_model import ModifiedVGG16Model, FusionVGG16Model

#-----------------------------------------
# Variables de entrada
images_directory = "./images_cropped"
# Este folder puede no existir
output_directory = "./output_images"
split_width = 256
overlap_percentage = 0.6
classes = ["arma de fuego", "no arma de fuego"]
path_model = "../../.lib/image_model/models/model_Vgg16_60_weapons"

def test_model(model, image_directory, image_original_path, output_directory, split_width, classes):
    """
    Realiza la detección de armas en las imágenes de un directorio.

    Args:
        model (torch.nn.Module): Modelo de PyTorch.
        image_directory (str): Directorio con las imágenes a procesar.
        image_original_path (str): Ruta de la imagen original.
        output_directory (str): Directorio de salida.
        split_width (int): Ancho de las imágenes divididas.
        classes (list): Lista con las clases del modelo.

    Returns:
        str: JSON con los resultados de la detección.  
    """
    
    salida = "No"
    flag = False
    bounding_boxes = {}
    normalize = transforms.Normalize(mean=[0.4105, 0.3696, 0.1959], std=[0.1948, 0.1904, 0.1755])
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        normalize
    ])
    
    files = glob.glob(os.path.join(image_directory, "*.png"))
    
    for image_file in files:
        image_file = os.path.basename(image_file) 
        x, y = map(int, image_file.split('.')[0].split('_'))
        image_path = os.path.join(image_directory, image_file)
        imagen = Image.open(image_path)
        
        if imagen.mode != 'RGB':
            imagen = imagen.convert('RGB')
        
        imagen = transform(imagen).unsqueeze(0)
        output = model(imagen)
        _, predicted = torch.max(output, 1)
        
        if predicted.item() == 0:
            bounding_boxes[image_file] = (x, y)
            if not flag:
                print("Weapon Detected")
                salida = "Weapon Detected"
                flag = True

    # Dibujar los bounding boxes en la imagen original
    imagen_original = Image.open(image_original_path)
    draw = ImageDraw.Draw(imagen_original)
    
    for image_file, (x, y) in bounding_boxes.items():
        width, height = split_width, split_width
        draw.rectangle([x, y, x + width, y + height], outline="green")

    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)

    output_image_path = os.path.join(output_directory, "imagen_original_con_bounding_boxes.png")
    imagen_original.save(output_image_path)
    print(f"Image with bounding boxes saved at: {output_image_path}")
    
    # Obtener la hora actual en la zona horaria de Bogotá
    timezone_bogota = pytz.timezone('America/Bogota')
    fecha_actual = datetime.now(timezone_bogota).isoformat()


    ## Revisar posible error de tipo de dato en el json
    ## Julian Sanchez, 23 de Oct 2024

    # Construir el diccionario para el JSON
    result = {
        "tipo": "Imagen",
        "deteccion": salida,
        "fecha": fecha_actual,  # Fecha y hora en zona horaria de Bogotá
        "bounding_boxes": bounding_boxes,
        "ruta_imagen_salida": output_image_path
    }

    return json.dumps(result, indent=4)


# Julian Sanchez, 23 de Oct 2024

# Ejemplo de uso:

#---------------------------------------------
# Desde un video (Esto lo arreglo después)
# Extraer y guardar el primer frame de un video
# video_path = "output_test.mp4"
# output_image_path = "image_test.png"

# extract_and_save_frame(video_path, output_image_path)

#---------------------------------------------
# Ejecutando el terminal

if input("Usar imagen de prueba? y/n: ")!="y":
    #Captura solo un fotograma de nombre: single_frame.jpg
    command = "../../.lib/mipi_camera/mipi /dev/video50"
    run_terminal_command(command)
    file = "single_frame.jpg"

#---------------------------------------------
# Usando imagen de prueba
else:
    file = "sample_images/image_test.png"

#---------------------------------------------
# Inferencia del modelo


start = time.time()
split_image(file, images_directory, split_width, overlap_percentage)
discard_images(images_directory, 7.0, 0.40)

model = torch.load(path_model, map_location=torch.device('cpu'))

r = test_model(model, images_directory, file, output_directory, split_width, classes)
end = time.time()

print("r",r)
print("Tiempo de preparación y predicción: ",end - start)

#---------------------------------------------