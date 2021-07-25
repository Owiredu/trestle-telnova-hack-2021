import torch

# Model
model = torch.hub.load('yolov5', 'custom', 'yolov5/crowdhuman_yolov5m.pt', source="local")  # or yolov5m, yolov5x, custom

# Images
img = 'https://ultralytics.com/images/zidane.jpg'  # or file, PIL, OpenCV, numpy, multiple

# Inference
results = model(img)

# Results
results.show()  # or .show(), .save(), .crop(), .pandas(), etc.