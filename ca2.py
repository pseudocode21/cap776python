import requests
import bcrypt
import re
from datetime import datetime
import pytz

def register():
    print("User Registration")
    name = input("Enter your name: ")

    while True:
        email = input("Enter your email address: ")
        if re.fullmatch(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            break  
        else:
            print("Invalid email format. Please enter a valid email (e.g., user@example.com).")
    while True:
        password = input("Enter your password: ").encode('utf-8')
        if len(password) >= 8:
            if re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[-+_!@#$%^&*.,?]).{8,}$', password.decode('utf-8')):
                hash_pass = bcrypt.hashpw(password, salt)
                break
            else:
                print("Password must contain at least one lowercase, one uppercase, one digit, and one special character.")
        else:
            print("Password should be at least 8 characters long!")

    with open("login.csv", 'a') as file:
        file.write(f"{name},{email},{hash_pass.decode('utf-8')}\n")
    
    print("Registration Done")

def get_coordinates(city_name):
    api_key = 'ad2b88cfd26c71c33a66c3691393635f'  
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"

    try:
        response = requests.get(geocode_url)
        if response.status_code == 200:
            location_data = response.json()
            if location_data:
                latitude = location_data[0]['lat']
                longitude = location_data[0]['lon']
                return latitude, longitude
            else:
                print("No data found for the specified city.")
                return None, None
        else:
            print(f"Error {response.status_code}: Failed to retrieve location data.")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}. Please check your internet connection.")
        return None, None

def convert_utc_to_local(utc_time):
    utc_time = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S+00:00')
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone()
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

def get_sunrise_sunset_data(latitude, longitude):
    api_url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&formatted=0"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()['results']
            local_sunrise = convert_utc_to_local(data['sunrise'])
            local_sunset = convert_utc_to_local(data['sunset'])
            print(f"Sunrise Time : {local_sunrise}")
            print(f"Sunset Time : {local_sunset}")
        else:
            print(f"Error {response.status_code}: Failed to retrieve data.")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}. Please check your internet connection.")

def login():
    print("User Login")
    attempts = 5
    while attempts > 0:
        print(f"You have {attempts} attempts remaining")
        email = input("Enter your email address: ")
        password = input("Enter your password: ").encode('utf-8')

        with open("login.csv", 'r') as file:
            for line in file:
                details = line.strip().split(",")
                stored_email = details[1]
                stored_password = details[2].encode('utf-8')

                if email == stored_email:
                    if bcrypt.checkpw(password, stored_password):
                        print(f"Welcome {details[0]}! You have successfully logged in.")
                        city_name = input("Enter the city name for sunrise/sunset data: ")
                        latitude, longitude = get_coordinates(city_name)
                        if latitude is not None and longitude is not None:
                            get_sunrise_sunset_data(latitude, longitude)
                        return
        attempts -= 1

    print("You exceeded your attempts! Please restart the program to try again.")

while True:
    print("\n1. Registration\n2. Login\n3. Exit")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        register()
    elif choice == 2:
        login()
    elif choice == 3:
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Please enter a valid choice (1-3).")
