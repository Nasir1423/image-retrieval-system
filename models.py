import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
import json

class ImageRetrievalSystem:
    def __init__(self, model_name='resnet50', feature_dim=2048):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_name, feature_dim)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.image_features = []
        self.image_names = []

    def _load_model(self, model_name, feature_dim):
        model = models.__dict__[model_name](pretrained=True)
        model = nn.Sequential(*list(model.children())[:-1])
        model.eval()
        model.to(self.device)
        return model

    def load_images(self, image_folder):
        image_paths = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if
                       img.endswith(('jpg', 'png'))]
        for img_path in image_paths:
            img = Image.open(img_path).convert('RGB')
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                features = self.model(img_tensor).squeeze().cpu().numpy()
            self.image_features.append(features)
            self.image_names.append(os.path.basename(img_path))
        self.image_features = np.array(self.image_features)

    def query(self, query_image_path, top_k=5):
        query_img = Image.open(query_image_path).convert('RGB')
        query_tensor = self.transform(query_img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            query_features = self.model(query_tensor).squeeze().cpu().numpy()

        similarities = cosine_similarity([query_features], self.image_features)[0]
        top_indices = similarities.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                'image_name': self.image_names[idx],
                'confidence': float(similarities[idx])
            })

        return results

if __name__ == "__main__":
    image_folder = './img'
    query_image = sys.argv[1]

    retrieval_system = ImageRetrievalSystem()
    retrieval_system.load_images(image_folder)
    results = retrieval_system.query(query_image)

    print(json.dumps(results))
