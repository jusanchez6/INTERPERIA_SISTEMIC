import os
import glob
from PIL import Image, ImageDraw
from torchvision import transforms
import torch
import json
from datetime import datetime
import pytz
from image_processing import split_image, calculate_entropy, calculate_complexity, discard_images

#-----------------------------------------
# Variables de entrada
images_directory = "./images_cropped"
output_directory = "./output_images"
split_width = 256
overlap_percentage = 0.6
classes = ["arma de fuego", "no arma de fuego"]
path_model = "model_Vgg16_60_weapons"



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
        "detección": salida,
        "fecha": fecha_actual,  # Fecha y hora en zona horaria de Bogotá
        "bounding_boxes": bounding_boxes,
        "ruta_imagen_salida": output_image_path
    }

    return json.dumps(result, indent=4)


# Julian Sanchez, 23 de Oct 2024

# Ejemplo de uso:

command = "./mipi /dev/video50"

#---------------------------------------------
# Ejecutando el terminal

run_terminal_comand(command)

#---------------------------------------------

#---------------------------------------------
# Desde un video
video_path = "output_test.mp4"
output_image_path = "image_test.png"

extract_and_save_frame(video_path, output_image_path)
#---------------------------------------------
# Inferencia del modelo
file = "imahge_test2.png"
split_image(file, image_directory, split_width, overlap_percentage)
discard_images(image_directory, 7.0, 0.40)

model = torch.load(path_model, map_location=torch.device('cpu'))
r = test_model(model, images_directory, output_image_path, output_directory, split_width, classes)

print(r)