import requests
import schedule
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import pyttsx3
import random
import itertools

# Initialize pyttsx3 engine for text-to-speech
engine = pyttsx3.init()

# Set the properties for the voice
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

# Fallback data (stored within the code as a list of dictionaries)
FALLBACK_DATA = [
    {'Weather': 'Clear', 'Temperature': 25.3, 'Economic Growth': 2.5, 'Geopolitical Stability': 50},
    {'Weather': 'Clouds', 'Temperature': 22.1, 'Economic Growth': 2.1, 'Geopolitical Stability': 48},
    {'Weather': 'Rain', 'Temperature': 18.4, 'Economic Growth': 1.9, 'Geopolitical Stability': 45},
    {'Weather': 'Clear', 'Temperature': 30.0, 'Economic Growth': 2.7, 'Geopolitical Stability': 55},
    {'Weather': 'Snow', 'Temperature': -5.2, 'Economic Growth': 1.8, 'Geopolitical Stability': 60}
]

# Regional-specific fallback data
REGIONAL_FALLBACK_DATA = {
    'South Africa': {'Weather': 'Clear', 'Temperature': 20.0, 'Economic Growth': 3.0, 'Geopolitical Stability': 60},
    'Vaal': {'Weather': 'Clouds', 'Temperature': 22.5, 'Economic Growth': 2.8, 'Geopolitical Stability': 62}
}

# List of places in Vaal
vaal_places = [
    "Leseding Road", "Vaal River Road", "Vaal Dam Road", "R1 Road",
    "Vereeniging Highway Road", "N1 Road", "Pretorious Street",
    "West Street Road", "Rivonia Road"
]

# List of suppliers
suppliers = ["Supplier A", "Supplier B", "Supplier C", "Supplier D"]

# Create cycling iterators for places and suppliers
vaal_place_iterator = itertools.cycle(vaal_places)
supplier_iterator = itertools.cycle(suppliers)

# Global counter to track the number of runs
run_counter = 0

# Define the speak_text function
def speak_text(text):
    print(text)  # Print to the console
    engine.say(text)
    engine.runAndWait()

# Get data from APIs or fallback to the locally stored data
def get_weather_data():
    api_key = 'b4da68812885c65b171bfb2a74625bec'
    city = 'New York'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

    try:
        response = requests.get(url, timeout=5)  # Timeout after 5 seconds
        response.raise_for_status()
        data = response.json()

        if 'weather' in data and 'main' in data:
            weather_condition = data['weather'][0]['main']
            temperature_kelvin = data['main']['temp']
            temperature_celsius = temperature_kelvin - 273.15
            return validate_weather_data(weather_condition, temperature_celsius)
        else:
            raise ValueError("Invalid weather data structure")

    except (requests.exceptions.RequestException, ValueError) as e:
        speak_text(f"Unable to access weather data online. Using fallback data. Error: {e}")
        return read_fallback_data('weather')

def get_economic_data():
    try:
        return validate_economic_data(2.5 + random.uniform(-0.5, 0.5))  # Simulate slight variations in economic data
    except Exception as e:
        speak_text(f"Unable to access economic data online. Using fallback data. Error: {e}")
        return read_fallback_data('economic')

def get_geopolitical_data():
    try:
        return validate_geopolitical_data(50 + random.uniform(-5, 5))  # Simulate slight variations in geopolitical data
    except Exception as e:
        speak_text(f"Unable to access geopolitical data online. Using fallback data. Error: {e}")
        return read_fallback_data('geopolitical')

# Fallback: Access local data stored within the code
def read_fallback_data(data_type):
    fallback = REGIONAL_FALLBACK_DATA.get('South Africa') or random.choice(FALLBACK_DATA)  # Use regional data if available
    if not fallback or data_type not in fallback:
        speak_text(f"Invalid fallback data for {data_type}. Defaulting to safe values.")
        return default_fallback_values(data_type)

    if data_type == 'weather':
        return validate_weather_data(fallback['Weather'], fallback['Temperature'])
    elif data_type == 'economic':
        return validate_economic_data(fallback['Economic Growth'])
    elif data_type == 'geopolitical':
        return validate_geopolitical_data(fallback['Geopolitical Stability'])

# Default fallback values if local data is also invalid
def default_fallback_values(data_type):
    if data_type == 'weather':
        return 'Unknown', 20.0
    elif data_type == 'economic':
        return 2.0
    elif data_type == 'geopolitical':
        return 50

# Enhanced validation for weather data
def validate_weather_data(weather, temperature):
    valid_weather_conditions = ["Clear", "Clouds", "Rain", "Snow"]
    if weather not in valid_weather_conditions:
        speak_text(f"Invalid weather condition detected: {weather}. Defaulting to 'Unknown'.")
        weather = "Unknown"

    if not (-50 <= temperature <= 50):
        speak_text(f"Temperature out of range: {temperature}°C. Defaulting to 0°C.")
        temperature = 0.0

    return weather, temperature

# Enhanced validation for economic data
def validate_economic_data(economic_growth):
    if not (-10.0 <= economic_growth <= 10.0):
        speak_text(f"Economic growth value {economic_growth}% is out of range. Defaulting to 0%.")
        economic_growth = 0.0
    return economic_growth

# Enhanced validation for geopolitical data
def validate_geopolitical_data(geopolitical_stability):
    if not (0 <= geopolitical_stability <= 100):
        speak_text(f"Geopolitical stability index {geopolitical_stability} is out of range. Defaulting to 50.")
        geopolitical_stability = 50
    return geopolitical_stability

# Linear regression for simple risk prediction
def predict_risk(weather, economic, geopolitical):
    # Dummy dataset for training the model
    # X = [Weather Index, Economic Growth, Geopolitical Stability]
    X = np.array([[1, 2.0, 50], [2, 1.5, 60], [3, 2.8, 55], [1, 2.2, 70]])
    y = np.array([0, 1, 0, 0])  # 0 = No Risk, 1 = Risk

    model = LinearRegression()
    model.fit(X, y)

    # Predict based on the current input data
    X_input = np.array([[weather, economic, geopolitical]])
    risk_prediction = model.predict(X_input)

    # Ensure the risk prediction is between 0 and 1
    risk_prediction = np.clip(risk_prediction, 0, 1)
    return risk_prediction[0]

# Reschedule action if disruption is detected
def reschedule_shipment():
    # Get the next supplier from the iterator
    current_supplier = next(supplier_iterator)
    message = f"Rescheduling shipping or client delivery with {current_supplier} due to predicted disruptions."
    speak_text(message)

# Use text-to-speech to speak the results and append the location
def speak_text_with_location(text):
    # Get the next place from the iterator
    current_place = next(vaal_place_iterator)
    # Append the place to the message
    location_message = f"Current location: {current_place}."
    full_message = f"{text} {location_message}"
    print(full_message)  # Output the message in the console as well
    engine.say(full_message)
    engine.runAndWait()

# Explain disruptions based on location
def explain_disruption(location):
    disruptions = {
        "Leseding Road": "There are floods on Leseding Road, which could cause significant delays.",
        "Vaal River Road": "Muds from recent rains on Vaal River Road may obstruct traffic.",
        "Vaal Dam Road": "Flooding near Vaal Dam Road could disrupt shipments.",
        "R1 Road": "Economic shifts are causing increased congestion on R1 Road.",
        "Vereeniging Highway Road": "Geopolitical tensions in the area are affecting logistics.",
        "N1 Road": "Natural disasters have led to road closures on N1 Road.",
        "Pretorious Street": "Flooding on Pretorious Street may impact delivery schedules.",
        "West Street Road": "Economic shifts are causing instability along West Street Road.",
        "Rivonia Road": "Heavy traffic due to ongoing construction on Rivonia Road could delay shipments."
    }
    return disruptions.get(location, "No specific disruptions reported for this location.")

# Main function
def main():
    global run_counter
    run_counter += 1

    # Step 1: Collect Data
    weather_condition, temperature = get_weather_data()
    economic_growth = get_economic_data()
    geopolitical_stability = get_geopolitical_data()

    # Convert weather condition into a numeric index (simplified)
    weather_index = 1 if "Clear" in weather_condition else 2

    # Step 2: Simulate Risk Level for demonstration
    if run_counter in [1, 2, 3, 4]:
        risk_level = [0.33, 0.66, 0.20, 0.85][run_counter - 1]
    else:
        # After the fourth run, revert to normal prediction
        risk_level = predict_risk(weather_index, economic_growth, geopolitical_stability)

    # Generate the message to be spoken
    message = f"Supply Chain Risk Prediction. The current risk level is {risk_level:.2f}. "

    if risk_level >= 0.5:
        message += "Warning: A potential supply chain disruption is predicted."
        reschedule_shipment()  # This will now include the supplier name

        # Get the current location and explain the disruption
        current_location = next(vaal_place_iterator)  # Get the next place
        disruption_message = explain_disruption(current_location)
        message += f" {disruption_message}"
    else:
        message += "The supply chain is stable at this location."

    # Speak the message and include the location
    speak_text_with_location(message)

# Schedule the job to run every 10 seconds
schedule.every(10).seconds.do(main)

# Start the schedule
speak_text("Starting supply chain risk prediction program.")
while True:
    schedule.run_pending()
    time.sleep(1)
