################################################################################
#               Real-Time parking detecttion and reservation                   #                  
#                                                                              #
#                         Ensemble  Model                                      #
#                                                                              #
################################################################################


################################################################################
#    Loading Libraries        
################################################################################

import torch
from collections import defaultdict
import numpy as np
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO


################################################################################
#    Class to manages the YOLOv8 model and  handle the ensemble predictions        
################################################################################


class YOLOv8Ensemble:
    def __init__(self, model_configs):
        self.models = []
        for config in model_configs:
            model_path = config['model_path']
            # Load the model directly from local path
            model = YOLO(model_path)  # Load directly from local path
            self.models.append((model, config))

    def ensemble_predict(self, image_path):
        results = []
        for model, config in self.models:
            result = model.predict(image_path, conf = 0.2)  # Run inference
            results.append(result)
        return results

    def aggregate_predictions(self, predictions):
        votes = defaultdict(list)

        # Iterate through all model predictions
        for result in predictions:
            boxes = result[0].boxes  # Access the Boxes object

            # Check if there are any boxes
            if boxes is not None and len(boxes.xyxy) > 0:  # Ensure boxes are available
                for i in range(len(boxes.xyxy)):  # Iterate over each box
                    # Access coordinates and confidence
                    x1, y1, x2, y2, conf, cls = boxes.data[i].tolist()  # Use data[i] for access
                    votes[int(cls)].append((x1, y1, x2, y2, conf))  # Store the box

        final_boxes = []
        for cls, boxes in votes.items():
            if len(boxes) > 0:
                avg_box = np.mean(np.array([b[:4] for b in boxes]), axis=0)
                avg_conf = np.mean([b[4] for b in boxes])
                final_boxes.append((*avg_box, avg_conf, cls))

        return final_boxes


    def predict(self, image_path):
        predictions = self.ensemble_predict(image_path)
        final_boxes = self.aggregate_predictions(predictions)
        return final_boxes

    def visualize_results(self, image_path, final_boxes):
        # Load image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Draw final boxes with labels
        for box in final_boxes:
            x1, y1, x2, y2 = box[:4]  # Bounding box coordinates
            conf = box[4]             # Confidence score
            cls = int(box[5])         # Class label

            # Draw rectangle and label
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(image, f'Class {cls}: {conf:.2f}', (int(x1), int(y1 - 5)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Show the image
        plt.imshow(image)
        plt.axis('off')
        plt.show()

################################################################################
#    Instantiate and Use the Ensemble Class       
################################################################################
model_configs = [
    {
        'model_path' : 'E:/PKLot/PKLot/runs/detect/train/weights/best.pt',
        'config_path' : 'E:/PKLot/PKLot/config.yaml'  # Path to the first model's config file
    },
    {
        
        'model_path': 'E:/PKLot/PKLot/runs/detect/train3/weights/best.pt',
        'config_path': 'E:/PKLot/PKLot/new_config.yaml'  # Path to the second model's config file
    },
    {
        'model_path': 'E:/PKLot/PKLot/runs/detect/train6/weights/best.pt',
        'config_path': 'E:/PKLot/PKLot/config_3.yaml'  # Path to the second model's config file
    }
]

# Create an instance of the ensemble model
ensemble_model = YOLOv8Ensemble(model_configs)

# Predict on an image
image_path = 'E:/PKLot/PKLot/data/test/images/2013-04-16_07_30_01.jpg'  # Replace with your image path
final_boxes = ensemble_model.predict(image_path)

# Output final boxes with labels
for box in final_boxes:
    print(f"Box: {box[:4]}, Confidence: {box[4]:.2f}, Class: {int(box[5])}")

# Visualize results
ensemble_model.visualize_results(image_path, final_boxes)


################################################################################
#    Result -- 
#    The output is not as expected so, not dropped this model.
################################################################################