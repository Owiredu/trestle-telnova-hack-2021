import torch

# Model
model = torch.hub.load('yolov5', 'custom', 'yolov5/crowdhuman_yolov5m.pt', source="local")  # or yolov5m, yolov5x, custom

# Images
img = 'https://ultralytics.com/images/zidane.jpg'  # or file, PIL, OpenCV, numpy, multiple

# Inference
results = model(img)

# Results
result_df = results.pandas().xyxy[0]
persons = result_df[result_df["name"] == "person"]
for i in range(persons.shape[0]):
    person_row = persons.iloc[i]
    xmin = person_row["xmin"]
    ymin = person_row["ymin"]
    xmax = person_row["xmax"]
    ymax = person_row["ymax"]
    confidence = person_row["confidence"]
    print(xmax-xmin, ymax-ymin)  # or .show(), .save(), .crop(), .pandas(), etc.