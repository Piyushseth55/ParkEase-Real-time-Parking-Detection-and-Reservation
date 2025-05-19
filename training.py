################################################################################
#               Real-Time parking detecttion and reservation                   #                  
#                                                                              #
#                          Training  Model                                     #
#                                                                              #
################################################################################


################################################################################
#    Loading Libraries        
################################################################################

from ultralytics import YOLO


################################################################################
#    Load model        
################################################################################+-

model = YOLO("yolov8s.pt")

################################################################################
#    Train Model      
################################################################################

model.train(data = 'E:/PKLot/PKLot/config.yaml',
            epochs=50,
            lr0=1e-5,          # Use a lower learning rate for fine-tuning
            weight_decay=1e-4, # Apply regularization to avoid overfitting
            patience = 8,
            workers = 8,
            batch = 4,
            augment = True,
            freeze = 2,
            pretrained = True)


################################################################################
#    Retrain best_model.pt  on a diverse dataset      
################################################################################

# Define path to the best model

best_model_path = "E:/PKLot/PKLot/runs/detect/train13/weights/best.pt"

# Load model
best_model = YOLO(best_model_path)


# Fine-tune on the new dataset with a lower learning rate
best_model.train(
    data='E:/PKLot/PKLot/new_config.yaml',
    epochs=50,
    lr0=1e-5,          # Use a lower learning rate for fine-tuning
    weight_decay=1e-4, # Apply regularization to avoid overfitting
    patience = 8,
    workers = 8,
    batch = 16,
    augment = True,
    freeze = 15,
    pretrained = True
)                       
     
     
# Validate the model on the validation set
results = best_model.val()

# Save the fine-tuned model
best_model.save('E:/PKLot/PKLot/fine_tune7.pt')


print(results)                            
                                 
                                 


                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                 
                                  
                                   
                                    
                                     
                                      
                                        
                                         
                                          
      
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                          
                                 
                                       
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             
                                             