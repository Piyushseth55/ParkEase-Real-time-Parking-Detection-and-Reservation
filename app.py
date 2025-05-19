################################################################################
#               Real-Time parking detecttion and reservation                   #                  
#                                                                              #
#                         Data Preprocessing                                   #
#                                                                              #
################################################################################





################################################################################
#    Loading Libraries        
################################################################################

import socket
from debugpy.common.timestamp import current
from flask import Flask, render_template, redirect, url_for, request, flash, Response
import flask
from flask_login import LoginManager, login_manager
import flask_login
from flask_login.utils import login_required, login_user, logout_user
from matplotlib.style import available
from requests import session
from sympy import total_degree
from werkzeug.security import check_password_hash
from db import get_booking_collection, get_filled_collection, save_user, get_user, get_admin,store_booking,get_total_parking_spaces, booking_to_filled, remove_from_filled, get_booked_filled_spaces, get_parking,is_car_already_booked,isAvailable, alreadyexist
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
import random
import string
from ultralytics import YOLO
import cv2
from flask_socketio import SocketIO , emit
import serial
from subprocess import Popen
import argparse
from flask import jsonify
from flask_login import current_user
from flask import session




app = Flask(__name__)
app.secret_key = "secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
model = YOLO('D:/SMART PARKING SYSTEM/NEW/ParkEase-Real-time-Parking-Detection-and-Reservation-main/models/fine_tune7.pt')
socketio = SocketIO(app)

label_mapping = {
    'Car': 'Free Space',
    'free': ' Temp Car'
}

occupied_spots_yolo = 0  # Initialize counter for occupied spots
total_spots = get_total_parking_spaces()
occupied_spots_arduino = 0



################################################################################
# Generating a video frame which montior parking spots at real-time
################################################################################

def gen_frames_from_webcam():
    cap = cv2.VideoCapture(0) # Capture from video file (or use 0 for webcam)
    address = "https://192.168.114.82:8080/video"
    cap.open(address)
    
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    ser = serial.Serial('COM5', 9600)
    global occupied_spots_yolo
    global occupied_spots_arduino
    while True:
        success, frame = cap.read()  # Capture frame-by-frame
        if not success:
            break
        else:
            # Reset the counter for each frame
            occupied_spots_yolo = 0  

            # Run object detection on the frame
            results = model.predict(frame, conf=0.35)  # Run YOLOv8 prediction
            
            for result in results:
                for label in result.boxes.data[:, 5]:  
                    original_label = result.names[int(label)]
                    # Replace with mapped label
                    new_label = label_mapping.get(original_label, original_label)  # Use original if not found
                    result.names[int(label)] = new_label  # Update the label in results


            for result in results:
                boxes = result.boxes.xyxy  # Bounding box coordinates
                class_ids = result.boxes.cls  # Class IDs
                for class_id in class_ids:
                    if int(class_id) == 1:  # Adjust based on your model's class index for cars
                        occupied_spots_yolo += 1
            
            # Read occupied spots from Arduino
            if ser.in_waiting > 0:
                sensor_data = ser.readline().decode('utf-8').strip()  # Read and decode data
                print(f"Sensor Data: {sensor_data}")  # Debug: print the sensor data
                occupied_spots_arduino = int(sensor_data)
        
            empty_spots = total_spots - occupied_spots_arduino - occupied_spots_yolo
            socketio.emit('update_counts', {'occupied': occupied_spots_yolo + occupied_spots_arduino, 'empty': empty_spots})
            
            # Annotate the frame with detection results
            annotated_frame = results[0].plot()

            # Add text to the annotated frame for total occupied spots
            cv2.putText(annotated_frame, f'Total Occupied: {occupied_spots_yolo}', (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)  # Display total count

            # Encode the frame in JPEG format for streaming
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()

            # Yield the frame as part of a streaming response for Flask
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # Exit condition for displaying locally (optional)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()  # Close all OpenCV windows


################################################################################
# ---- Login page ---- 
################################################################################

@app.route('/', methods = ['GET', 'POST'])
def login() :
    message = ''
    if request.method == "POST" :
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)
        
        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('userdashboard'))
        else:
            flash("Username or Password is incorrect.")
    return render_template('index.html', message = message)


################################################################################
# ---- Userdashboard ---- 
################################################################################

@app.route('/userdashboard')
@login_required
def userdashboard():
    total_spaces = get_total_parking_spaces()
    empty_spaces = total_spaces - get_booked_filled_spaces()
    return render_template('userdashboard.html', user = flask_login.current_user, total_spaces = total_spaces, available_spaces = empty_spaces)
  

################################################################################
# ---- Back button ----
################################################################################

@app.route('/back', methods = ['POST'])
@login_required
def back():
    return redirect(url_for('userdashboard'))


@app.route('/signup')
def signup() :
    return render_template('signup.html')


################################################################################
# ---- Signup Form ---- 
################################################################################

@app.route('/signup', methods = ['GET', 'POST'])
def registration() :
    message = ''
    if request.method == "POST" :
        username = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        city = request.form.get('city')
        noplate = request.form.get('noplate')
        password_input = request.form.get('password')
        try :
            save_user(username, email,mobile,city,noplate, password_input)
            flash("Successfully Account Created !")
            return redirect(url_for('login'))       
        except DuplicateKeyError:
            message = "User already exists!"
    return render_template('signup.html')
    
################################################################################
# ---- Logout button ----
################################################################################
 
@app.route('/logout', methods = ['POST'])
@login_required
def logout():
    logout_user()
    flash("Successfully logged out!")
    return redirect(url_for('login'))

@app.route('/home', methods = ['GET','POST'])
def home() :
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    return render_template('admin.html')



################################################################################
# ---- Admin Login page ---- 
################################################################################

@app.route('/admin', methods = ['POST'])
def adminlogin():
    message = ''
    if request.method == "POST" :
        username = request.form.get('username')
        password_input = request.form.get('password')
        admin = get_admin(username)
        if admin and check_password_hash(admin['password'], password_input):
            return redirect(url_for('admindashboard'))
        else :
            message = "Enter valid username and password"
    return render_template('admin.html' , message = message)
 

################################################################################
# ---- Admin Dashboard ---- 
################################################################################   

@app.route('/admindashboard')
def admindashboard() :
    collection1 = get_booking_collection()
    collection2 = get_filled_collection()
    return render_template('admindashboard.html', collection1 = collection1, collection2 = collection2)

@app.route('/video_feed_webcam', methods = ['POST', 'GET'])
def video_feed_webcam():
    
    return Response(gen_frames_from_webcam(), mimetype='multipart/x-mixed-replace; boundary=frame')


################################################################################
# ---- Methods for removing user from booking table and from filled table ----
################################################################################
 
@app.route('/confirm_checked_rows', methods=['POST'])
def confirm_checked_rows():
    data = request.get_json()
    ids_to_remove = data.get('ids', [])
    
    if not ids_to_remove:
        return jsonify(success=False, message="No IDs provided"), 400
    
    try:
        booking_to_filled(ids_to_remove)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route('/remove_checked_rows', methods=['POST'])
def remove_checked_rows():
    data = request.get_json()
    ids_to_remove = data.get('ids', [])
    
    if not ids_to_remove:
        return jsonify(success=False, message="No IDs provided"), 400
    
    try:
        remove_from_filled(ids_to_remove)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

################################################################################
# ---- Price Calculator ----
################################################################################
 
@app.route('/price_calculator', methods = ['GET'])
@login_required
def price_calculator():
    return render_template('price_calculator.html')
    

@app.route('/parking', methods=['GET'])
@login_required
def get_parking_data():
    # Fetch all parking spots data from the database
    return get_parking()   
   
@app.route('/parkspot')
@login_required 
def parkspot():
     
    return render_template('parkingspot.html')
   
@app.route('/bookslot')
@login_required
def bookslot():
    user = current_user
    spot_id = request.args.get('spot_id')
    spot_type = request.args.get('spot_type')
    return render_template('booking.html', user = user, spot_id = spot_id, spot_type = spot_type)

################################################################################
# ---- booking form ---- 
################################################################################
      
@app.route('/bookslot', methods = ['POST'])
@login_required
def conf_booking() :
    if request.method == "POST" :
        customer_name = request.form.get('customer_name')
        arrival_time = request.form.get('arrival_time')
        session_time = request.form.get('session_time')
        parking_id = request.form.get('parking_id')
        parking_type = request.form.get('parking_type')
        city = request.form.get('city')
        car_number_plate = request.form.get('car_number_plate')
        try:
            # Get the current time and add 1 hour to it
            current_time = datetime.now()
            print(current_time)
            min_arrival_time = current_time + timedelta(hours=1) 
            print(min_arrival_time)
            arrival_time_obj = datetime.strptime(arrival_time, '%H:%M')
            arrival_time_obj = current_time.replace(
                hour=arrival_time_obj.hour, 
                minute=arrival_time_obj.minute, 
                second=arrival_time_obj.second, 
                microsecond=0
            )
             # If arrival time is earlier than current time, assume it's the next day
            if arrival_time_obj < current_time:
                arrival_time_obj += timedelta(days=1)

            print(arrival_time_obj)
            # Ensure the selected datetime is in the future
            if arrival_time_obj > min_arrival_time:
                flash('Please select time only just 1 hour after.', 'danger')
                return redirect(url_for('bookslot' , spot_id = parking_id, spot_type = parking_type))
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return redirect(url_for('bookslot', spot_id = parking_id, spot_type = parking_type))
        
        if is_car_already_booked(car_number_plate):
            flash('Your car number plate is already booked.','danger')
        elif isAvailable() :
            return redirect(url_for('confirmation', 
                            customer_name=customer_name, 
                            arrival_time=arrival_time, 
                            session_time = session_time,
                            parking_id=parking_id, 
                            parking_type=parking_type, 
                            city=city, 
                            car_number_plate=car_number_plate))
        else :
            flash('No empty spaces are available !', 'warning')
        
    return redirect(url_for('bookslot', spot_id = parking_id, spot_type = parking_type))

@app.route('/confirmation')
@login_required
def confirmation():
    booking_details = {
        'customer_name': request.args.get('customer_name'),
        'arrival_time': request.args.get('arrival_time'),
        'session_time': request.args.get('session_time'),
        'parking_id': request.args.get('parking_id'),
        'parking_type': request.args.get('parking_type'),
        'city': request.args.get('city'),
        'car_number_plate': request.args.get('car_number_plate'),
    }
    today = datetime.now().date()
    arrival = datetime.strptime(f"{today} {booking_details['arrival_time']}", '%Y-%m-%d %H:%M')
    departure = datetime.strptime(f"{today} {booking_details['session_time']}", '%Y-%m-%d %H:%M')

    # Handle cases where the session time is past midnight
    if departure < arrival:
        departure += timedelta(days=1)
        
    # Calculate total period in hours
    total_duration = (departure - arrival).total_seconds() / 3600  # Duration in hours

    # Determine pricing based on parking type
    price_per_hour = {
        'open roof': 2,  # Example: $2/hour
        'inner parking': 3,  # Example: $3/hour
    }
    
    p_type = str(booking_details['parking_type'])
    total_price = round(total_duration * price_per_hour.get(p_type, 2), 2)

    # Add calculated fields to booking details
    booking_details['total_duration'] = f"{round(total_duration, 2)}"  # In hours
    booking_details['total_price'] = f"{total_price}"

    session['booking_details'] = booking_details
    return render_template('confirmation.html', booking_details=booking_details)
    
@app.route('/payment', methods = ['GET', 'POST'])
@login_required
def payment():
    booking_details = session.get('booking_details')
    user = current_user  
    if request.method == 'POST' :
        if alreadyexist(booking_details) :
            store_booking(booking_details)
            return render_template('process_payment.html')
        else:
            print("Your parking spot is already booked !")
            return render_template('payment.html', user = user, booking_details = booking_details)
    
    return render_template('payment.html', user = user, booking_details = booking_details)


@app.route('/process_payment')
@login_required
def process_payment() :
    booking_details = session.get('booking_details')
    user = current_user
    session.pop
    return render_template('process_payment.html', user = user, booking_details = booking_details)
    
    
    
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@login_manager.user_loader
def load_user(username) :
    return get_user(username)


if __name__ == "__main__" :
    app.run(debug=True)