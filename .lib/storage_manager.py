##
# @file storage_manager.py
#
# @brief Este módulo se encarga de generar la clase del modelo modificado o con fusión. SE REQUIERE esta
# clase para la apertura del modelo.

# Este script contiene varias funciones utilitarias para manejar estructuras de directorios, 
# gestionar el espacio de almacenamiento, calcular el tamaño de las carpetas y guardar archivos de audio. 
# Las funciones trabajan con operaciones del sistema de archivos, como verificar el espacio libre, 
# eliminar archivos antiguos y asegurar suficiente espacio de almacenamiento para nuevos archivos. 
# Además, proporciona una forma de guardar archivos de audio con nombres de archivo basados en la marca de tiempo.
#
# @section funcs Funciones
#  - get_free_space_gb: Obtiene el espacio libre en gigabytes de un directorio.
#  - get_folder_size: Calcula el tamaño de una carpeta en gigabytes.
#  - get_folder_size_du: Calcula el tamaño de una carpeta en gigabytes usando el comando 'du'.
#  - create_directory_structure: Crea la estructura de directorios para almacenar archivos de audio.
#  - delete_old_files: Elimina archivos más antiguos de ciertos días en una carpeta.
#  - ensure_storage_space: Asegura que haya suficiente espacio de almacenamiento antes de guardar nuevos archivos.
#  - save_audio: Guarda un archivo de audio en la carpeta de destino con un nombre basado en la marca de tiempo.
#
# @author: Felipe Ayala ??????
# @author: Maria del Mar Arbelaez (Docs)
#
# @date: 2024-03-29
#
# @version: 1.0
#
# @copyright SISTEMIC 2025
#
##

import os
import subprocess
import shutil
from datetime import datetime, timedelta

def get_free_space_gb(folder):
    """
    Get free space in gigabytes in the specified directory.
    
    Args:
    - folder (str): Directory path.
    
    Returns:
    - float: Free space in gigabytes.
    """
    statvfs = os.statvfs(folder)
    return (statvfs.f_frsize * statvfs.f_bavail) / (1024 ** 3)

def get_folder_size(folder):
    """
    Get folder size in gigabytes.
    
    Args:
    - folder (str): Directory path.
    
    Returns:
    - float: Folder size in gigabytes.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 ** 3)

def get_folder_size_du(folder):
    """
    Get folder size in gigabytes using the 'du' command.
    
    Args:
    - folder (str): Directory path.
    
    Returns:
    - float: Folder size in gigabytes.
    """
    result = subprocess.run(['du', '-sb', folder], stdout=subprocess.PIPE)
    total_size = int(result.stdout.split()[0].decode('utf-8'))
    return total_size / (1024 ** 3)


def create_directory_structure(base_path, segments_folder, events_folder):
    """
    Create directory structure to store audio files.
    
    Args:
    - base_path (str): Base directory path.
    - segments_folder (str): Segments folder name.
    - events_folder (str): Events folder name.

    Returns:
    - tuple: Paths to segments and events directories.
    """
    segments_path = os.path.join(base_path, segments_folder)
    events_path = os.path.join(base_path, events_folder)
    os.makedirs(segments_path, exist_ok=True)
    os.makedirs(events_path, exist_ok=True)
    return segments_path, events_path

def delete_old_files(folder, days_to_keep=0):
    """
    Delete files older than a specific number of days in the folder.
    
    Args:
    - folder (str): Directory path.
    - days_to_keep (int): Number of days to keep files (default is 0).
    """
    now = datetime.now()
    cutoff = now - timedelta(days=days_to_keep)
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mtime < cutoff or days_to_keep == 0:
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")

def ensure_storage_space(base_path, max_segments_size_gb, max_events_size_gb, segments_folder, events_folder, days_to_keep_storage):
    """
    Ensure sufficient storage space before saving new files.
    
    Args:
    - base_path (str): Base directory path.
    - max_segments_size_gb (float): Maximum size in gigabytes for segments folder.
    - max_events_size_gb (float): Maximum size in gigabytes for events folder.
    
    Returns:
    - tuple: Paths to segments and events directories.
    """
    free_space = get_free_space_gb(base_path)
    segments_path, events_path = create_directory_structure(base_path, segments_folder, events_folder)
    #print(f"free_space: {free_space}")

    # Tamaño máximo permitido para cada carpeta
    #print(f"max_segments_size_gb: {max_segments_size_gb}")
    #print(f"max_events_size_gb: {max_events_size_gb}")

    # Tamaño actual de cada carpeta
    current_segments_size = get_folder_size_du(segments_path)
    current_events_size = get_folder_size_du(events_path)
    #print(f"current_segments_size: {current_segments_size}")
    #print(f"current_events_size: {current_events_size}")
    

    # Verificar si se necesita espacio adicional
    if current_segments_size > max_segments_size_gb:
        delete_old_files(segments_path, days_to_keep_storage)
    if current_events_size > max_events_size_gb:
        delete_old_files(events_path, days_to_keep_storage)

    return segments_path, events_path

def save_audio(file_path, destination_folder, event_name=None):
    """
    Save audio file in the destination folder with a timestamp-based file name.
    
    Args:
    - file_path (str): Path to the audio file.
    - destination_folder (str): Destination folder path.
    - event_name (str): Name of the event (default is None).
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if event_name:
        filename = f"{timestamp}_{event_name}.wav"
    else:
        filename = f"{timestamp}.wav"
    destination_path = os.path.join(destination_folder, filename)
    shutil.move(file_path, destination_path)
    print(f"Saved audio to: {destination_path}")
