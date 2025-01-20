##
# @file vgg_model.py
#
# @brief Este módulo se encarga de generar la clase del modelo modificado o con fusión. SE REQUIERE esta
# clase para la apertura del modelo.
#
# @section classs Clases:
# - ModifiedVGG16Model: Clase del modelo modificado.
# - FusionVGG16Model: Clase del modelo fusionado.
#
# @author: Felipe Ayala
# @author: Julian Sanchez
# @author: Maria del Mar Arbelaez
#
# @date: 2024-10-24
#
# @version: 1.0
#
# @copyright SISTEMIC 2024
#
##

import torch
import torch.nn as nn
from torchvision import models

# Definición de la clase del modelo modificado VGG16
class ModifiedVGG16Model(torch.nn.Module):
    """
    Clase que define un modelo modificado basado en la arquitectura VGG16.
    Se utiliza el modelo preentrenado VGG16 de torchvision y se modifica la parte del clasificador 
    para ajustarlo a una tarea con 2 clases de salida. Los parámetros de la red convolucional se congelan.
    """

    def __init__(self):
        """
        Inicializa la clase `ModifiedVGG16Model`, cargando el modelo VGG16 preentrenado de torchvision.
        El clasificador de la red se modifica para una tarea binaria (con 2 clases).
        Además, se congelan los parámetros de la parte de características del modelo.
        """

        # Llamada al inicializador de la clase base `torch.nn.Module`
        super(ModifiedVGG16Model, self).__init__()

        # Cargar el modelo VGG16 preentrenado desde torchvision
        # 'VGG16_Weights.DEFAULT' se usa para cargar los pesos preentrenados de VGG16
        model = models.vgg16(weights='VGG16_Weights.DEFAULT')

        # Extraer la parte de características (convolucional) del modelo VGG16
        self.features = model.features

        # Congelar los parámetros de las características (evitar que se actualicen durante el entrenamiento)
        for param in self.features.parameters():
            param.requires_grad = False

        # Definir el clasificador con capas totalmente conectadas
        self.classifier = nn.Sequential(
            nn.Dropout(),            # Capa de dropout para regularización
            nn.Linear(25088, 4096),  # Capa completamente conectada de 25088 a 4096

            nn.ReLU(inplace=True),   # Función de activación ReLU

            nn.Dropout(),            # Otra capa de dropout
            nn.Linear(4096, 4096),   # Segunda capa completamente conectada de 4096 a 4096
            nn.ReLU(inplace=True),   # Función de activación ReLU

            # Capa de salida con 2 unidades para la clasificación binaria
            nn.Linear(4096, 2))

    def forward(self, x):
        """
        Define la pasada hacia adelante (forward pass) del modelo.

        Args:
            x (Tensor): El tensor de entrada que representa las imágenes de entrada al modelo.
        
        Returns:
            Tensor: El resultado de la clasificación, con dos valores para las dos clases.
        """

        # Pasar las imágenes de entrada a través de la parte convolucional (features)
        x = self.features(x)
        
        # Aplanar las características extraídas (flatten) para que puedan ser pasadas al clasificador
        x = x.view(x.size(0), -1)

        # Pasar las características a través del clasificador totalmente conectado
        x = self.classifier(x)
        return x

# Definición de la clase FusionVGG16Model
class FusionVGG16Model(nn.Module):
    """
    Clase que define un modelo basado en VGG16 modificado con dos clasificadores independientes.
    El modelo utiliza la arquitectura VGG16 preentrenada y tiene dos redes completamente conectadas
    (fully connected) para realizar dos tareas de clasificación separadas, pero usando las mismas características
    extraídas por la red convolucional.
    """
    def __init__(self):
        """
        Inicializa la clase `FusionVGG16Model`, cargando el modelo VGG16 preentrenado de torchvision.
        Se crean dos clasificadores independientes, cada uno con una capa de salida para clasificación binaria.
        Además, se congela la parte convolucional del modelo (features) para evitar el entrenamiento de los pesos
        preentrenados durante el entrenamiento.
        """
        
        # Llamada al inicializador de la clase base `nn.Module` para configurar la red correctamente
        super(FusionVGG16Model, self).__init__()

        # Cargar el modelo VGG16 preentrenado con pesos de 'VGG16_Weights.DEFAULT'
        model = models.vgg16(weights='VGG16_Weights.DEFAULT')
        self.features = model.features # Extraer las características (convolucionales) del modelo VGG16

        # Congelar los parámetros de la parte convolucional (para que no se actualicen durante el entrenamiento)
        for param in self.features.parameters():
            param.requires_grad = False

        # Definición de dos clasificadores independientes con las mismas capas
        # El primero, `classifier1`, genera una salida para la primera tarea de clasificación
        self.classifier1 = nn.Sequential(
            nn.Dropout(),           # Regularización con Dropout
            nn.Linear(25088, 4096), # Capa totalmente conectada de 25088 a 4096
            nn.ReLU(inplace=True),  # Función de activación ReLU
            nn.Dropout(),           # Otra capa de Dropout
            nn.Linear(4096, 4096),  # Segunda capa totalmente conectada de 4096 a 4096
            nn.ReLU(inplace=True),  # Función de activación ReLU
            nn.Linear(4096, 2))     # Capa de salida para clasificación binaria (2 clases)

        # El segundo clasificador, `classifier2`, también tiene la misma arquitectura,
        # pero genera una salida para una segunda tarea de clasificación
        self.classifier2 = nn.Sequential(
            nn.Dropout(),
            nn.Linear(25088, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 2)) # Otra salida binaria para una segunda clasificación

    def forward(self, x):
        """
        Define el paso hacia adelante (forward pass) del modelo.

        param:
            x (Tensor): El tensor de entrada que representa las imágenes de entrada.

        returns:
            tuple: Dos tensores de salida, `output1` y `output2`, cada uno representando
                   la salida de los dos clasificadores (para las dos tareas de clasificación).
        """

        # Pasar la entrada a través de la parte convolucional del modelo (features)
        x = self.features(x)
        
        # Aplanar las características extraídas para que puedan ser pasadas a través de los clasificadores
        x = x.view(x.size(0), -1)

        output1 = self.classifier1(x)  # Salida para la primera clasificación
        output2 = self.classifier2(x)  # Salida para la segunda clasificación
        
        # Retornar ambas salidas
        return output1, output2        
