import os
import functions
from pathlib import Path
from datetime import datetime, timedelta

building = {"building": ["apartments", "barracks", "bungalow", "cabin", "detached", "annexe", "dormitory",
                         "farm", "house", "houseboat", "residential", "semidetached_house", "static_caravan",
                         "stilt_house", "terrace", "trullo", "yes"]}

pos_ref = {"amenity": ["community_centre", "place_of_worship", "school"],
           "tourism": "hostel",
           "railway": "subway_entrance"}

def setup_environment():
    """Configura las variables del entorno."""
    cities = ["Bilbao","Madrid",
        "Valletta",
        "Valencia",
        "Zaragoza",
        "Barcelona",
        "Amsterdam",
        "London",
        "Bangkok",
        "Ho Chi Minh City",
        "Shenzhen",
        "Melbourne",
        "Cardiff",
        "Seoul",
        "Boston",
        "Nairobi",
        "Marrakesh",
        "Venice",
        "Mexico City",
        "Cairo",
        "Mumbai",
        "Jakarta"]
    year = 2024
    max_distance = 300
    start_date = datetime(year, 1, 1, 0, 0)
    end_date = datetime(year, 1, 1, 0, 0)
    hour_list = [start_date + timedelta(hours=i) for i in range(int((end_date - start_date).total_seconds() / 3600) + 1)]
    return cities, year, max_distance, hour_list

if __name__ == "__main__":
    cities, year, max_distance, hour_list = setup_environment()
    main_path = Path(__file__).resolve().parent.parent  
    results_path = main_path / 'Results'
    os.makedirs(results_path, exist_ok=True)
    
    for city in cities:
        functions.process_city(city, main_path, results_path, hour_list, max_distance, building, pos_ref)