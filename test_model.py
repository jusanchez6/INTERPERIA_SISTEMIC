import os
import glob
from PIL import Image, ImageDraw
from torchvision import transforms
import torch
import json
from datetime import datetime
import pytz


def test_model(model, image_directory, image_original_path, output_directory, split_width, classes):
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

    # Construir el diccionario para el JSON
    result = {
        "tipo": "Imagen",
        "detección": salida,
        "fecha": fecha_actual,  # Fecha y hora en zona horaria de Bogotá
        "bounding_boxes": bounding_boxes,
        "ruta_imagen_salida": output_image_path
    }

    return json.dumps(result, indent=4)


