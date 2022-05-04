# Geospatial Analysis for Disaster Evacuation Planning
![image](https://user-images.githubusercontent.com/44957830/166630022-0c38a204-f8e4-4339-8681-2eba715a1571.png)

# Introduction
This project seeks to provide decision-making support to emergency managers in coastal Oregon cities that are vulnerable to tsunami and earthquake hazards in order to enable a speedy recovery after such disasters. In particular, this project will consider the spatial nature of infrastructure systems using a Geographic Information System (GIS) to determine the effects of potential disaster events on them, and the consequential effect on recovery. Emergency managers will be able to use the provided tool to determine how to optimally allocate limited resources to best handle operations after a disaster event. This is done by knowing which infrastructures will sustain the most damage given a disaster impact, and determining optimal routes for rescue and recovery personnel to access disaster areas.

# What This Project Does
This project uses [ArcGIS Pro](https://www.esri.com/en-us/arcgis/products/arcgis-pro/overview) to create custom [geoprocessing tools](https://pro.arcgis.com/en/pro-app/latest/tool-reference/main/arcgis-pro-tool-reference.htm) and utilize existing ones to visually display what infrastructures will be damaged and the type of damage to be expected given a specific earthquake magnitude. This is done by the [Disaster Impact tool](https://github.com/thejosehuerta/GADEP/edit/main/README.md#disaster-impact). Furthermore, the [Disaster Route Analysis tool](https://github.com/thejosehuerta/GADEP/edit/main/README.md#disaster-route-analysis) finds an optimal route between two different sets of points on the map while using the [Disaster Impact tool](https://github.com/thejosehuerta/GADEP/edit/main/README.md#disaster-impact) to avoid any bridges that would be too badly damaged for emergency personnel to get across safely.
## Disaster Impact
Using data from the [Fragility Function Viewer](https://clip.engr.oregonstate.edu/), data from [OHELP](https://ohelp.oregonstate.edu/), and shapefiles from [ODOT](https://www.oregon.gov/odot/Data/Pages/GIS-Data.aspx) and [Geofabrik](https://download.geofabrik.de/north-america/us/oregon.html), disaster impact on different infrastructures given a specific earthquake magnitude is calculated. These calculations result in a damage state which signifies what type of damage an infrastructure is more likely to receive.
### Demonstration
https://user-images.githubusercontent.com/44957830/166630836-89adf62b-30d9-4f1f-91ff-e471f5973254.mp4
<details>
  <summary>View Description</summary>
  First, we select a specific bridge and see its damage state of "None" given an earthquake magnitude of 8.1.
  We then open the Disaster Impact tool, select the "Bridges" feature class and an earthquake magnitude of 9.0 as our parameters then click "Run".<p>
  Once the tool finishes running, we're greeted with a success message. We refresh the map then click on the same bridge again and see that its damage state has been updated to "Moderate" given an earthquake magnitude of 9.0.
</details>

## Disaster Route Analysis
Subsequently, a route analysis can be performed to find optimal routes between two different sets of points while avoiding these damaged infrastructures. Given the nature of the data in this project, optimal routes can be found for a variety of different scenarios:
* Finding an optimal route between two points.
  * For example, finding a route from a specific school (e.g., Broadway Middle School in Clatsop county) to a specific hospital (e.g., Providence Seaside Hospital).
* Finding optimal routes between two sets of points in a specific county.
  * For example, finding routes from *all* schools in Clatsop county to the nearest hospitals in Clatsop county.
* Finding optimal routes between two sets of points from anywhere to anywhere.
  * For example, finding routes from all points of interest in Clatsop county to the nearest hospitals outside of Clatsop county (e.g., Columbia county).
### Demonstration
<details>
  <summary>View Description</summary>
  # ADD DESCRIPTION
</details>

# Full Documentation
See the [Wiki](https://github.com/thejosehuerta/GADEP/wiki) for the full documentation on how to get started and more.
