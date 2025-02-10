import os
import functions
from pathlib import Path
from datetime import datetime, timedelta
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import functions

building = {"building": ["apartments", "barracks", "bungalow", "cabin", "detached", "annexe", "dormitory",
                         "farm", "house", "houseboat", "residential", "semidetached_house", "static_caravan",
                         "stilt_house", "terrace", "trullo", "yes"]}

pos_ref = {"amenity": ["community_centre", "place_of_worship", "school"],
           "tourism": "hostel",
           "railway": "subway_entrance"}

def setup_environment():
    """Configura las variables del entorno."""
    cities = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
        "London", "Paris", "Berlin", "Madrid", "Rome", "Amsterdam", "Vienna", "Barcelona", "Milan", "Stockholm",
        "Tokyo", "Osaka", "Seoul", "Shanghai", "Beijing", "Hong Kong", "Bangkok", "Singapore", "Kuala Lumpur", "Jakarta",
        "Sydney", "Melbourne", "Brisbane", "Perth", "Auckland", "Toronto", "Vancouver", "Montreal", "Mexico City", "São Paulo",
        "Rio de Janeiro", "Buenos Aires", "Santiago", "Bogotá", "Lima", "Caracas", "Quito", "Havana", "San Juan", "Montevideo",
        "Dubai", "Abu Dhabi", "Doha", "Riyadh", "Jeddah", "Istanbul", "Jerusalem", "Tehran", "Baghdad", "Kuwait City",
        "Moscow", "Saint Petersburg", "Kyiv", "Warsaw", "Prague", "Budapest", "Bucharest", "Belgrade", "Sofia", "Athens",
        "Cairo", "Casablanca", "Johannesburg", "Cape Town", "Nairobi", "Lagos", "Accra", "Addis Ababa", "Algiers", "Tunis",
        "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Dhaka", "Karachi", "Lahore", "Colombo",
        "Manila", "Hanoi", "Ho Chi Minh City", "Yangon", "Phnom Penh", "Kathmandu", "Taipei", "Ulaanbaatar", "Tashkent", "Astana"
    ]
    year = 2024
    max_distance = 300
    start_date = datetime(year, 1, 1, 0, 0)
    end_date = datetime(year, 1, 1, 0, 0)
    hour_list = [start_date + timedelta(hours=i) for i in range(int((end_date - start_date).total_seconds() / 3600) + 1)]
    return cities, year, max_distance, hour_list

# Definir la función fuera del bloque __main__
def process_single_city(city, main_path, results_path, hour_list, max_distance, building, pos_ref):
    functions.process_city(city, main_path, results_path, hour_list, max_distance, building, pos_ref)

if __name__ == "__main__":
    cities, year, max_distance, hour_list = setup_environment()
    main_path = Path(__file__).resolve().parent.parent  
    results_path = main_path / 'Results'
    os.makedirs(results_path, exist_ok=True)

    # Obtener el número de procesos óptimos
    num_workers = min(multiprocessing.cpu_count(), len(cities))  
    print(f"Using {num_workers} workers to process cities.")

    # Ejecutar en paralelo con ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=1) as executor:
        executor.map(process_single_city, cities, [main_path] * len(cities),
                     [results_path] * len(cities), [hour_list] * len(cities),
                     [max_distance] * len(cities), [building] * len(cities), 
                     [pos_ref] * len(cities))