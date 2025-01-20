## Work In Progress
The following model of evaluation and optimisation of access to services is framed under the doctoral thesis developed by Asier Divasson-J. at the University of Deusto (Spain), directed by Dr. Cruz E. Borges, Dr. J. Ignacio Garcia, and Dr. Ana M. Macarulla.

# AccessiCity
AccesiCity is an urban accessibility analysis model designed to evaluate proximity and
access to key resources in urban environments. It combines geographic data and
optimization techniques to address specific population needs. Below is a detailed
explanation of its methodology:

## Data Collection
AccesiCity relies on data from OpenStreetMap (OSM), a collaborative platform that offers
detailed geographic information. This includes data on building types and uses, such as
residential, public, and commercial structures, as well as information about transportation
infrastructure, including roads, pedestrian pathways, and access points. Additionally, it
incorporates terrain features, such as elevation and slope, to provide a comprehensive
overview of the urban landscape.

## Distance Calculation
AccesiCity calculates the shortest routes from each residential building to the nearest
services. Additionally, the model considers the hourly availability of services, factoring in
their varying operational hours throughout the day to ensure accurate accessibility analysis.

## Optimization
A Greedy Algorithm was developed to maximize service coverage by identifying areas with
the lowest current accessibility and proposing the opening of additional services in buildings
that would provide the greatest benefit to the largest population.

## Currently Applied to Climate Shelter Networks
On relation to the current application, it further prioritizes climate shelters that can be
established quickly and with minimal investment. This method ensures a progressive and
cost-effective optimization of the service network.

![Alt text](images/AccessiCity.jpg)
