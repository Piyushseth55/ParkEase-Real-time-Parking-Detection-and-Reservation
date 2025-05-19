################################################################################
#               Real-Time parking detecttion and reservation                   #                  
#                                                                              #
#                         Data Preprocessing                                   #
#                                                                              #
################################################################################


################################################################################
#    Loading Libraries        
################################################################################


from pymongo import MongoClient
from sympy import true
from werkzeug.security import generate_password_hash
from users import User
from flask import jsonify


################################################################################
# configuration for database 
################################################################################

client = MongoClient("mongodb+srv://piyushseth1998:OA9hxez2jRcHos4I@parking.p4uxw.mongodb.net/")
parkingdb = client.get_database("parkingdb")
users_collection = parkingdb.get_collection("users")
admin_collection = parkingdb.get_collection("admin")
booking_collection = parkingdb.get_collection("booking")
parking_collection = parkingdb.get_collection("parking")
filled_collection = parkingdb.get_collection("filled")


################################################################################
# save user 
################################################################################

def save_user(username, email, mobile, city, noplate, password):
    hash_password = generate_password_hash(password)
    users_collection.insert_one({'_id' : username, 'email' : email,
                                  'mobile': mobile, 'city' : city,
                                  'noplate' : noplate, 'password' : hash_password})

################################################################################
# fetching user details    
################################################################################
   
def get_user(username) :
    user_data = users_collection.find_one({'_id' : username})
    return User(user_data['_id'], user_data['email'], user_data['mobile'], user_data['city'],
                user_data['noplate'], user_data['password']) if user_data else None

################################################################################
# saving admin details
################################################################################

def save_admin(admin_username, admin_password) :
    hash_password = generate_password_hash(admin_password)
    admin_collection.insert_one({'_id' : admin_username , 'password' : hash_password})

################################################################################
# getting admin details
################################################################################

def get_admin(username) :
    admin_data = admin_collection.find_one({'_id' : username})
    return admin_data

################################################################################
# getting parking details
################################################################################

def get_parking():
    parking_spots = parking_collection.find()
    parking_data = []
    for spot in parking_spots:
        parking_data.append({
            'id': spot['id'],
            'status': spot['status'],
            'type': spot['type']
        })
    
    return jsonify(parking_data) 

################################################################################
# getting total parking spots       
################################################################################
       
def get_total_parking_spaces():
    total_spaces = parking_collection.count_documents({})
    return total_spaces

################################################################################
# fetching status of user licence number plate    
################################################################################

def is_car_already_booked(car_number_plate):
    """
    Check if a car with the given number plate is already in the booking table.
    """
    existing_booking = booking_collection.find_one({'car_number_plate': car_number_plate})
    return existing_booking is not None

################################################################################
# method for spot availability
################################################################################

def isAvailable() :
    total_spaces = get_total_parking_spaces()
    booking_available = booking_collection.count_documents({})
    filled_count = filled_collection.count_documents({})
    if(total_spaces <= booking_available + filled_count):
        return False
    else :
        return True

################################################################################
# save booking details
################################################################################

def store_booking(booking_details) :
    if(isAvailable() == False):
        return False
    booking_details = {
    '_customer_name': booking_details['customer_name'],
    'arrival_time': booking_details['arrival_time'],
    'session_time':booking_details['session_time'],
    'parking_id': booking_details['parking_id'],
    'parking_type': booking_details['parking_type'],
    'city': booking_details['city'],
    'car_number_plate': booking_details['car_number_plate'],
    'total_duration' : booking_details['total_duration'],
    'total_price' : booking_details['total_price']
    }
    
    booking_collection.insert_one(booking_details)
    
    # Update the status of the parking_id in parking_collection
    result = parking_collection.update_one(
        {'id': booking_details['parking_id']},  # Match the parking_id
        {'$set': {'status': 'booked'}}  # Update the status
    )
    
    # Check if the update was successful
    if result.modified_count == 0:
        print(f"Failed to update parking_id {booking_details['parking_id']} in parking_collection.")
    else:
        print(f"Parking ID {booking_details['parking_id']} successfully marked as booked.")

    return True
    
    
def set_capacity(floor, numberofspot) :
    parking_details = parking_collection.find_one({'_id' : floor})
    if parking_details :
        parking_collection.update_one({'_id' : floor}, {'$set' : {'total_spaces' : numberofspot}})
    else :
        parking_collection.insert_one({'_id' : floor, 'total_spaces' : numberofspot})

################################################################################
# checking already exist user
################################################################################

def alreadyexist(booking_details) :
    customer_name = booking_details['customer_name']
    if booking_collection.find_one({'_customer_name' : customer_name}) == None :
        return True
    return False
               

################################################################################
# initialize parking
################################################################################
       
def initialize_parking_data():
    """
    Initializes parking spot data with id, status, and type for the database.
    Creates 5 open roof parking spots (OP-1 to OP-5) and 5 inner parking spots (IP-1 to IP-5).
    """
    # Sample data for parking spots (5 open roof and 5 inner parking spots)
    parking_spots = [
        {'id': 'OP-1', 'status': 'empty', 'type': 'open roof'},
        {'id': 'OP-2', 'status': 'empty', 'type': 'open roof'},
        {'id': 'OP-3', 'status': 'empty', 'type': 'open roof'},
        {'id': 'OP-4', 'status': 'empty', 'type': 'open roof'},
        {'id': 'OP-5', 'status': 'empty', 'type': 'open roof'},
        {'id': 'OP-6', 'status': 'empty', 'type': 'open roof'},
        {'id': 'IP-1', 'status': 'empty', 'type': 'inner parking'},
        {'id': 'IP-2', 'status': 'empty', 'type': 'inner parking'},
        {'id': 'IP-3', 'status': 'empty', 'type': 'inner parking'},
        {'id': 'IP-4', 'status': 'empty', 'type': 'inner parking'}
    ]
    
    # Insert each parking spot data into the collection
    for spot in parking_spots:
        # Check if the spot already exists (by id)
        existing_spot = parking_collection.find_one({'id': spot['id']})
        
        if not existing_spot:
            # Insert the parking spot data if it doesn't exist
            parking_collection.insert_one(spot)
            print(f"Initialized parking spot {spot['id']} with status '{spot['status']}' and type '{spot['type']}'.")
        else:
            # If the spot already exists, print a message
            print(f"Parking spot {spot['id']} already exists. No changes made.")

# Call the function to initialize the data
#initialize_parking_data()


################################################################################
# getting booked spots data   
################################################################################
   
def get_booking_collection() :
    collection = list(booking_collection.find())
    return collection

################################################################################
# getting filled spots data
################################################################################

def get_filled_collection() :
    collection = list(filled_collection.find())
    return collection

################################################################################
# changing the user to booked to filled
################################################################################

def booking_to_filled(ids_to_remove) :
    for customer_name in ids_to_remove :
        document = booking_collection.find_one_and_delete({"_customer_name" : customer_name})
        
        if document : 
            # Update the status of the parking_id in parking_collection
            parking_id = document['parking_id']
            result = parking_collection.update_one(
                {'id': parking_id},  # Match the parking_id
                {'$set': {'status': 'filled'}}  # Update the status
            )
            
            # Check if the update was successful
            if result.modified_count == 0:
                print(f"Failed to update parking_id {parking_id} in parking_collection.")
            else:
                print(f"Parking ID {parking_id} successfully marked as booked.")

            filled_collection.insert_one(document)

# remove the user from filled data and make spot empty          
def remove_from_filled(ids_to_remove) :
    for customer_name in ids_to_remove :
        document = filled_collection.find_one_and_delete({"_customer_name" : customer_name})
        if document : 
            # Update the status of the parking_id in parking_collection
            parking_id = document['parking_id']
            result = parking_collection.update_one(
                {'id': parking_id},  # Match the parking_id
                {'$set': {'status': 'empty'}}  # Update the status
            )
            
            # Check if the update was successful
            if result.modified_count == 0:
                print(f"Failed to update parking_id {parking_id} in parking_collection.")
            else:
                print(f"Parking ID {parking_id} successfully marked as booked.")

        

def get_booked_filled_spaces() :
    filled_count = filled_collection.count_documents({})
    booked_count = booking_collection.count_documents({})
    return filled_count + booked_count
