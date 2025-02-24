import os
import functions_v2
from pathlib import Path
from datetime import datetime, timedelta

building = {"building": ["apartments", "barracks", "bungalow", "cabin", "detached", "annexe", "dormitory",
                         "farm", "house", "houseboat", "residential", "semidetached_house", "static_caravan",
                         "stilt_house", "terrace", "trullo", "yes"]}

pos_ref = {"building": ["public", "train_station", "retail"],
           "amenity": ["public", "townhall", "sport_centre", "information", "mall", "library", "museum",
                       "community_centre", "arts_centre", "place_of_worship", "exhibition_centre", 
                       "school", "courthouse", "theatre", "police", "marketplace"],
           "leisure": ["sport_centre", "stadium"],
           "tourism": ["museum", "hostel", "alpine_hut"],
           "shop": "mall",
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

#    cities = cities[::-1]
    
    year = 2024
    max_distance = 300
    start_date = datetime(year, 1, 1, 0, 0)
    end_date = datetime(year, 1, 1, 0, 0)
    hour_list = [start_date + timedelta(hours=i) for i in range(int((end_date - start_date).total_seconds() / 3600) + 1)]
    return cities, year, max_distance, hour_list

if __name__ == "__main__":
    cities, year, max_distance, hour_list = setup_environment()
    main_path = Path(__file__).resolve().parent.parent  
    results_path = main_path / 'Results_v2'
    os.makedirs(results_path, exist_ok=True)
    
    for city in cities:
        functions_v2.process_city(city, main_path, results_path, hour_list, max_distance, building, pos_ref)