import sys
import json
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

class ImageRetrievalSystem:
    def __init__(self, model_path, feature_dim=2048, feature_file='image_features.pkl'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path, feature_dim)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.feature_file = feature_file
        self.image_features = []
        self.image_names = []
        self._load_features()

    def _load_model(self, model_path, feature_dim):
        model = models.resnet50(weights='IMAGENET1K_V1')
        model = nn.Sequential(*list(model.children())[:-1])
        model.eval()
        model.to(self.device)
        return model

    def _load_features(self):
        if os.path.exists(self.feature_file):
            with open(self.feature_file, 'rb') as f:
                data = pickle.load(f)
                self.image_features = data['features']
                self.image_names = data['names']
        else:
            # print("Feature file not found. Please run `save_image_features` first.")
            pass

    def save_image_features(self, image_folder):
        image_paths = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if
                       img.endswith(('jpg', 'png'))]
        features = []
        names = []
        for img_path in image_paths:
            img = Image.open(img_path).convert('RGB')
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                feature = self.model(img_tensor).squeeze().cpu().numpy()
            features.append(feature)
            names.append(os.path.basename(img_path))
        
        self.image_features = np.array(features)
        self.image_names = names
        
        with open(self.feature_file, 'wb') as f:
            pickle.dump({'features': self.image_features, 'names': self.image_names}, f)
    
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
                'confidence': float(similarities[idx])  # Convert to float for JSON serialization
            })

        return results

if __name__ == "__main__":
    model_path = './model/resnet50_model.pth'
    image_folder = './img'
    query_image = sys.argv[1]

    retrieval_system = ImageRetrievalSystem(model_path)
    
    # Uncomment the following line if you need to save image features
    # retrieval_system.save_image_features(image_folder)
    
    results = retrieval_system.query(query_image)
    print(json.dumps(results))
