import torch
import torch.nn as nn
from torchvision import models

class ModifiedVGG16Model(torch.nn.Module):
    def __init__(self):
        super(ModifiedVGG16Model, self).__init__()

        model = models.vgg16(weights='VGG16_Weights.DEFAULT')
        self.features = model.features

        for param in self.features.parameters():
            param.requires_grad = False

        self.classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(25088, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 2))

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

class FusionVGG16Model(nn.Module):
    def __init__(self):
        super(FusionVGG16Model, self).__init__()

        model = models.vgg16(weights='VGG16_Weights.DEFAULT')
        self.features = model.features

        for param in self.features.parameters():
            param.requires_grad = False

        self.classifier1 = nn.Sequential(
            nn.Dropout(),
            nn.Linear(25088, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 2))  

        self.classifier2 = nn.Sequential(
            nn.Dropout(),
            nn.Linear(25088, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 2))

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        output1 = self.classifier1(x)  # Salida para la primera clasificación
        output2 = self.classifier2(x)  # Salida para la segunda clasificación
        return output1, output2        
