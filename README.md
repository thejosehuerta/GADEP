# Geospatial Analysis for Disaster Evacuation Planning
![image](https://user-images.githubusercontent.com/44957830/166508424-6d4c3ad3-c261-43c4-b9e6-b35c9442e57d.png)

# Introduction
This project seeks to provide decision-making support to emergency managers in coastal Oregon cities that are vulnerable to tsunami and earthquake hazards to enable a speedy recovery after such a disaster. In particular, this project will consider the spatial nature of infrastructure systems using a Geographic Information System (GIS) to determine the effects of potential disaster events on them, and the consequential effect on recovery. Emergency managers will be able to use the provided tools to determine how to optimally allocate limited resources to best handle operations after a disaster event. This is done by knowing which infrastructures will sustain the most damage given a disaster impact, and determining optimal routes for rescue and recovery personnel to access and escape disaster areas.

# What This Project Does
### Disaster Impact
Using [ArcGIS Pro](https://www.esri.com/en-us/arcgis/products/arcgis-pro/overview), a powerful desktop GIS software, data from the [Fragility Function Viewer](https://clip.engr.oregonstate.edu/), data from [OHELP](https://ohelp.oregonstate.edu/), and shapefiles from [ODOT](https://www.oregon.gov/odot/Data/Pages/GIS-Data.aspx) and [Geofabrik](https://download.geofabrik.de/north-america/us/oregon.html), damage impact on different infrastructures given a specific earthquake magnitude is calculated. As a result, it's then possible to see which infrastructures will receive the most damage given the earthquake magnitude. 
### Route Analysis
Subsequently, a route analysis can be performed to find optimal routes between two different sets of points while avoiding these damaged infrastructures. Given the nature of the data in this project, optimal routes can be found for a variety of different options:
* Finding an optimal route between only two points.
  * For example, finding a route from a specific school (e.g., Broadway in Clatsop county) to a specific hospital (e.g., Providence Seaside Hospital).
* Finding optimal routes between two sets of points in a specific county.
  * For example, finding routes from *all* schools in Clatsop county to the nearest hospitals in Clatsop county.
* Finding optimal routes between two sets of points from anywhere to anywhere.
  * For example, finding routes from all points of interest in Clatsop county to the nearest hospitals outside of Clatsop county (e.g., Columbia county).
