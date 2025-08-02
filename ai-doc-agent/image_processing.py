import pymupdf
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

def extract_images(pdf_path, output_dir):
    doc = pymupdf.open(pdf_path)
    for i, page in enumerate(doc):
        images = page.get_images(full=True)
        for img_i, _ in enumerate(images):
            xref = images[img_i][0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_filename = f"{output_dir}/{i}_{img_i}.png"
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)

def embed_image(image_path):
    image = Image.open(image_path)
    inputs = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").get_image_features(**inputs)
    return image_features.squeeze().numpy()