# Geospatial Analysis for Disaster Evacuation Planning
![image](https://user-images.githubusercontent.com/44957830/166630022-0c38a204-f8e4-4339-8681-2eba715a1571.png)

# Introduction
This project seeks to provide decision-making support to emergency managers in coastal Oregon cities that are vulnerable to tsunami and earthquake hazards in order to enable a speedy recovery after such disasters. In particular, this project will consider the spatial nature of infrastructure systems using a Geographic Information System (GIS) to determine the effects of potential disaster events on them, and the consequential effect on recovery. Emergency managers will be able to use the provided tool to determine how to optimally allocate limited resources to best handle operations after a disaster event. This is done by knowing which infrastructures will sustain the most damage, and determining optimal routes for rescue and recovery personnel to access or avoid these disaster areas.

# What This Project Does
This project uses [ArcGIS Pro](https://www.esri.com/en-us/arcgis/products/arcgis-pro/overview) to create custom [geoprocessing tools](https://pro.arcgis.com/en/pro-app/latest/help/analysis/geoprocessing/basics/what-is-geoprocessing-.htm) and utilize existing ones to visually display what infrastructures will be damaged and the type of damage to be expected given a specific earthquake magnitude. This is done by the [Disaster Impact tool](https://github.com/thejosehuerta/GADEP/edit/main/README.md#disaster-impact). Furthermore, the [Disaster Route Analysis tool](https://github.com/thejosehuerta/GADEP/edit/main/README.md#disaster-route-analysis) finds an optimal route between two different sets of points and uses the [Disaster Impact tool](https://github.com/thejosehuerta/GADEP/edit/main/README.md#disaster-impact) to caclualte which bridges will be be too badly damaged for emergency personnel to get across safely in order to avoid them.
## Disaster Impact
Using data from the [Fragility Function Viewer](https://clip.engr.oregonstate.edu/), data from [OHELP](https://ohelp.oregonstate.edu/), and shapefiles from [ODOT](https://www.oregon.gov/odot/Data/Pages/GIS-Data.aspx) and [Geofabrik](https://download.geofabrik.de/north-america/us/oregon.html), disaster impact on different infrastructures given a specific earthquake magnitude is calculated. These calculations result in a damage state which signifies what type of damage an infrastructure is more likely to receive.
### Demonstration
https://user-images.githubusercontent.com/44957830/166630836-89adf62b-30d9-4f1f-91ff-e471f5973254.mp4
<details>
  <summary>View Description</summary>
  
  * First, we select a specific bridge and see its damage state of "None" given an earthquake magnitude of 8.1.
  * We then open the Disaster Impact tool, select the "Bridges" feature class and an earthquake magnitude of 9.0 as our parameters then click "Run".
  * Once the tool finishes running, we're greeted with a success message. We refresh the map then click on the same bridge again and see that its damage state has been updated to "Moderate" given an earthquake magnitude of 9.0.
</details>

## Disaster Route Analysis
Subsequently, a route analysis can be performed to find optimal routes between two different sets of points while avoiding any bridges that are too badly damaged. Given the nature of the data in this project, optimal routes can be found for a variety of different scenarios:
* Finding an optimal route between two points.
  * For example, finding a route from a specific school (e.g., Broadway Middle School in Clatsop county) to a specific hospital (e.g., Providence Seaside Hospital).
* Finding optimal routes between two sets of points in a specific county.
  * For example, finding routes from *all* schools in Clatsop county to the nearest hospitals in Clatsop county.
* Finding optimal routes between two sets of points from anywhere to anywhere.
  * For example, finding routes from all points of interest in Clatsop county to the nearest hospitals outside of Clatsop county (e.g., Columbia county).
* Combinations of the three listed above.
### Demonstration
https://user-images.githubusercontent.com/44957830/166812360-78019684-28f2-4e3d-a340-45ff05aa04ac.mp4
<details>
  <summary>View Description</summary>
  
  * First, we select three different bridges in Seaside, Oregon. They all have a damage state of "None" given an earthquake magnitude of 8.1
  * Then, we select a few hotels that are close to the bridges. These will be our starting points in the route analysis. 
  * Next, we select Seaside Fire Department as this point will be our end point. Selecting these points is not necessary to the analysis; they were only selected to show their attributes.
  * To actually perform the route analysis, we open the Disaster Route Analysis tool and begin entering our parameters:
    * We select an earthquake magnitude of 9.0 to update the damage states for the bridges in order to see how this earthquake magnitude will affect finding the best routes.
    * We then choose the Points of Interest feature layer as our starting points. Then, using an SQL expression, we can filter this feature layer to only have the hotels be our starting points.
    * The same feature layer is used as our end points parameter, except now we filter the feature layer to only have fire stations as our end points.
    * The number of facilities parameter is how many end points (facilities) will be found for _each_ starting point. We choose one, meaning we want to find only one fire station for each hotel.
    * Next, we name our analysis. This name can be anything.
    * We click "Run", then click on "View Details" to view what the tool is doing in the background. **Note:** this video skipped the amount of time it takes to run this tool; it actually took 30 seconds to run.
    * We can then see the exported route layer, titled "HotelsToFireStations", appear on the map with each unique route being a different color.
    * Next, we click and drag the exported route layer lower in the Drawing Order. This lets us see the bridges better.
    * Lastly, we refresh the map and click on the same bridges to see that their damage states have been updated. Any bridges with a damage state of "Slight" or higher will be avoided in the route analysis. Looking at the routes produced, we can see this in effect. **Note:** there are some routes that stray in from outside the current scope of the map, these are routes from hotels that aren't shown on the map.
  
</details>

# Full Documentation
See the [Wiki](https://github.com/thejosehuerta/GADEP/wiki) for the full documentation on how to get started and more.
