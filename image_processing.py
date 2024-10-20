from PIL import Image
import os
def start_points(size, split_size, overlap=0):
    stride = int(split_size * (1 - overlap))
    return range(0, size, stride)

def split_image(file, output_directory, split_width, overlap_percentage):
    img = Image.open(file)
    img_w, img_h = img.size
    X_points = start_points(img_w, split_width, overlap_percentage)
    Y_points = start_points(img_h, split_width, overlap_percentage)
    
    for y_point in Y_points:
        for x_point in X_points:
            img_cropped = img.crop(box=(x_point, y_point, x_point + split_width, y_point + split_width))
            name_image = f"{x_point}_{y_point}.png"
            img_cropped.save(os.path.join(output_directory, name_image))
            #print(f"Image saved: {name_image}")
    print("images saved")


from PIL import Image, ImageFilter
import numpy as np
import os
import glob

def calculate_entropy(image):
    """Calcula la entropía de una imagen"""
    histogram = image.histogram()
    histogram_length = sum(histogram)
    samples_probability = [float(h) / histogram_length for h in histogram]
    return -sum([p * np.log2(p + 1e-7) for p in samples_probability if p != 0])

def calculate_complexity(image):
    """Calcula el índice de complejidad de una imagen"""
    # Convertir la imagen a escala de grises
    gray_image = image.convert('L')
    # Calcular el gradiente de la imagen utilizando el operador Sobel
    gradient_x = np.abs(np.asarray(gray_image.filter(ImageFilter.Kernel((3, 3), (-1, 0, 1, -2, 0, 2, -1, 0, 1))))).sum()
    gradient_y = np.abs(np.asarray(gray_image.filter(ImageFilter.Kernel((3, 3), (-1, -2, -1, 0, 0, 0, 1, 2, 1))))).sum()
    return (gradient_x + gradient_y) / image.size[0] / image.size[1]

def discard_images(dataset_path, entropy_threshold, complexity_threshold):
    """Descarta imágenes que caen por debajo de los umbrales de entropía y complejidad"""
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
            os.makedirs(f"{dataset_path}/discard", exist_ok=True)
            os.rename(f"{dataset_path}/{file}", f"{dataset_path}/discard/{file}")
            i = i + 1
            #os.remove(os.path.join(dataset_path, filename))
    #print(i)