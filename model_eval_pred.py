################################################################################
#               Real-Time parking detecttion and reservation                   #                  
#                                                                              #
#                     Model Evaluation And Prediction                          #
#                                                                              #
################################################################################



################################################################################
#    Loading Libraries        
################################################################################

import os
import shutil
from PIL import Image
from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
import seaborn as sns 
import cv2
import pandas as pd
from sklearn.metrics import confusion_matrix
from ultralytics import YOLO
import torch

################################################################################
#    List of generated files       
################################################################################

# Define the path to the directory
post_training_file_path = "E:/PKLot/PKLot/runs/detect/train13"


# List the files in the directory
for file in os.listdir(post_training_file_path) :
    print(file)
    

################################################################################
#    Learning Curve Analysis       
################################################################################

# Define a function to plot learning curves for loss values
def plot_learning_curve(df, train_loss_col, val_loss_col, title) :
    plt.figure(figsize=(20, 10))
    sns.lineplot(data =df,x = 'epoch', y = train_loss_col, label = 'Train Loss' , color = '#141140', linestyle = '-'  , linewidth = 2) # type igonre
    sns.lineplot(data = df,x = 'epoch', y = val_loss_col, label = 'Val Loss' , color = 'orangered', linestyle = '--' , linewidth = 2)
    plt.title(title)
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    plt.show()
    

# Create full path for results.csv

result_path = os.path.join(post_training_file_path, 'results.csv')
df = pd.read_csv(result_path)
df.columns = df.columns.str.strip()
df


# plot the learning curve for each loss
plot_learning_curve(df, 'train/box_loss', 'val/box_loss' , 'Box Loss Learning curve')
plot_learning_curve(df, 'train/cls_loss', 'val/cls_loss' , 'Classification Loss Learning curve')
plot_learning_curve(df, 'train/dfl_loss', 'val/dfl_loss' , 'Distribution Focal Loss Learning curve')

################################################################################
#    Observation : 
#       -> The model is learning effectively, as both train and validation 
#          losses decrease consistently.
#       -> There is no significant overfitting, as the two curves are closely 
#          aligned.
#       -> The learning rate could be adjusted to see if the model can converge 
#          faster, but this performance seems stable.
################################################################################


################################################################################
#    Confusion Matrix Evaluation       
################################################################################

# Define the path to normalize the confusion matrix image
confusion_matrix_path = os.path.join(post_training_file_path, 'confusion_matrix_normalized.png')


# Read the image 
cm_img = cv2.imread(confusion_matrix_path)

# convert the image from BGR to RGB for accurate color representation
cm_img  = cv2.cvtColor(cm_img, cv2.COLOR_BGR2RGB)

# Display the image 
plt.figure(figsize = (10, 10), dpi= 120)
plt.imshow(cm_img)
plt.axis('off')
plt.show()

################################################################################
#    Observation : 
#    -> The confusion matrix shows that while the model can identify "Car" and 
#       "Background" perfectly when it gets the prediction right, there is a 
#        misclassification issue where it tends to confuse "Background" for 
#        "Car."
################################################################################

################################################################################
#    Performance Metrics Assessment       
################################################################################

# Path to best model
best_model_path = os.path.join(post_training_file_path, 'weights/best.pt')

# Load the best model
best_model = YOLO(best_model_path)

# Validate the best model using the validation set with default parameters
metrics = best_model.val(split='val')

# Convert the dictionary to a pandas DataFrame and use the keys as the index
metrics_df = pd.DataFrame.from_dict(metrics.results_dict, orient='index', columns=['Metric Value'])

# Display the DataFrame
metrics_df.round(3)


################################################################################
#    Inference on Validation Set Images      
################################################################################

# Define the path to the validation images
val_iamges_path = 'E:/PKLot/PKLot/data/val/images'

# List all jpg images
image_files = [f for f in os.listdir(val_iamges_path) if f.endswith('.jpg')]

# Select 9 images at equal interval
num_images = len(image_files)
selected_images = [image_files[i] for i in range(0, num_images, num_images // 9)]


# Initialize the subplot
fig, axes = plt.subplots(3, 3, figsize=(20, 21))
fig.suptitle('Validation Set Inferences', fontsize=24) 

# Perform inference on each selected image and display it
for i, ax in enumerate(axes.flatten()):
    image_path = os.path.join(val_iamges_path, selected_images[i])
    results = best_model.predict(source=image_path, conf=0.5)
    
    

    annotated_image = results[0].plot(line_width=1)
    annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    ax.imshow(annotated_image_rgb)
    ax.axis('off')

plt.tight_layout()
plt.show()



################################################################################
#    Inference on Unseen Test set Images      
################################################################################

# define path to 2nd model
model_2 = YOLO("E:/PKLot/PKLot/models/fine_tune7.pt")

# Define path to test images
test_iamges_path = 'E:/PKLot/PKLot/olddata2/test/images'

# List all jpg images
image_files = [f for f in os.listdir(test_iamges_path)]

# Select 9 images at equal interval
num_images = len(image_files)
selected_images = [image_files[i] for i in range(0, num_images)]

# Initialize the subplot
fig, axes = plt.subplots(3, 3, figsize=(20, 21))
fig.suptitle('Unseen Set Inferences', fontsize=24) 

# Perform inference on each selected image and display it
for i, ax in enumerate(axes.flatten()):
    image_path = os.path.join(test_iamges_path, selected_images[i])
    results = model_2.predict(source=image_path, conf=0.5)
    
    annotated_image = results[0].plot(line_width=1)
    annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    ax.imshow(annotated_image_rgb)
    ax.axis('off')

plt.tight_layout()
plt.show()



################################################################################
#    Inference on Unseen Test Images      
################################################################################

sample_image_path = "C:/Users/HP/Parking detection/Resources/carParkImg.png"

results = model_2.predict(source=sample_image_path , conf = 0.2)

print(results[0].boxes)
sample_image = results[0].plot(line_width=2)
sample_image = cv2.cvtColor(sample_image, cv2.COLOR_BGR2RGB)

plt.figure(figsize= (20, 15))
plt.imshow(sample_image)
plt.title("Detected parking space by YOLOv8 ", fontsize = 20)
plt.axis('off')
plt.show()


################################################################################
#    Observation : 
#    -> The model did not perform on new images. There is a need to train the 
#       model on diverse dataset.
################################################################################


################################################################################
#    Export the model in onnx format      
################################################################################

# Load your trained YOLOv8 model
model = YOLO('E:/PKLot/PKLot/runs/detect/train/weights/best.pt')

# Export the model to ONNX format
model.export(format='onnx')