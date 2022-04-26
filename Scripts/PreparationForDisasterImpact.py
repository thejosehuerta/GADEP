from cmath import acos
import arcpy
from numpy import short
import pandas
import os
import math

# ********************************************************************
# Helper Functions
# ********************************************************************
# --------------------------------------------------------------------
# Prints a message in ArcGIS Pro
# --------------------------------------------------------------------
def message(message):
    arcpy.AddMessage(message)

# --------------------------------------------------------------------
# Finds the distance between two different coordinates (latitude and longitude in decimal degrees)
# Reference: https://www.youtube.com/watch?v=bzSnw-Iz6O8
# --------------------------------------------------------------------
def distance(pgaLat, pgaLong, objectLat, objectLong):
    return 6371 * math.acos(math.cos(math.radians(90-pgaLat))*
    math.cos(math.radians(90-objectLat))+
    math.sin(math.radians(90-pgaLat))*
    math.sin(math.radians(90-objectLat))*
    math.cos(math.radians(pgaLong-objectLong)))/1.609

# --------------------------------------------------------------------
# Xlookup Excel function python replication
# Reference: https://pythoninoffice.com/replicate-excel-vlookup-hlookup-xlookup-in-python/
# --------------------------------------------------------------------
def xlookup(lookup_value, lookup_array, return_array, if_not_found:str = ''):
    match_value = return_array.loc[lookup_array == lookup_value]
    if match_value.empty:
        return f'"{lookup_value}" not found!' if if_not_found == '' else if_not_found
    else:
        return match_value.tolist()[0]
# ********************************************************************
# Main Program
# ********************************************************************
# --------------------------------------------------------------------
# Setting directories
# --------------------------------------------------------------------
# Get the current directory of the script; it should look something like the following:
# {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP Project\Scripts
scriptsPath = os.getcwd()

infrastructuresPath = os.path.join(os.path.dirname(scriptsPath), "Projects", "GADEP", "Infrastructures.gdb")
pgasPath = os.path.join(os.path.dirname(scriptsPath), "PGA Values")

# --------------------------------------------------------------------
# Initialize paramter variables
# --------------------------------------------------------------------
# The first paramter will be a feature layer
inputFeature = arcpy.GetParameter(0)
# The second paramter is a boolean asking the user whether or not the PGA values in the input feature will be calculated
calculatePGA = arcpy.GetParameter(1)
# The third paramter is a boolean asking the user whether or not the resulting feature layer will be clipped
clip = arcpy.GetParameter(2)
# The fourth paramter will be the clip features 
clipFeatures = arcpy.GetParameter(3)

# --------------------------------------------------------------------
# Create local copy of the input feature in the Infrastructures.gdb
# --------------------------------------------------------------------
# Set the new name of the feature layer.
# An error will be thrown if the feature layer's name contains blanks, so we need to get rid of them first

# Store the feature layer name
featureName = inputFeature.name
# If it contains a blank, change the case of the sring to title case (it looks better), and get rid of the blanks
if " " in featureName:
    featureName = featureName.title().replace(" ", "")

# Copy the features of the input feature to the Infrastructures.gdb
arcpy.CopyFeatures_management(inputFeature, os.path.join(infrastructuresPath, featureName))

# Overwrite inputFeature to be the new, copied version
inputFeature = os.path.join(infrastructuresPath, featureName)

# Get the geometry/shape type of the input feature
ifType = arcpy.Describe(inputFeature)

# Print copy success message in ArcGIS Pro
message("{} successfully copied to {}!".format(ifType.name, ifType.path))

# --------------------------------------------------------------------
# Add latitude and longitude points according to shapetype
# --------------------------------------------------------------------
# If the input feature is a point feature, its geometry property will need to be set to "POINT".
# For all other shapetypes such as polygons and polylines, the "INSIDE" property will be set.
if ifType.shapeType == "Point":
    geometryPropertyX = "POINT_X"
    geometryPropertyY = "POINT_Y"
else:
    geometryPropertyX = "INSIDE_X"
    geometryPropertyY = "INSIDE_Y"

# Create array of array of the new fields and their geometry properties.
# Two new fields will be created and added to the input feature:
# LONG_CALC - stands for "longitude calculated" and will contain the calculated longitude values in decimal degrees
# LAT_CALC - stands for "latitude calculated" and will contain the calculated latitude values in decimal degrees
geometryProperties = [["LONG_CALC", geometryPropertyX], ["LAT_CALC", geometryPropertyY]]

# Perform the calculation 
arcpy.CalculateGeometryAttributes_management(inputFeature, geometryProperties, coordinate_format="DD")

# Print coordinate fields added success message in ArcGIS Pro
message("Latitude and longitude fields and coordinates successfully added!")

# --------------------------------------------------------------------
# Add necessary fields to input feature
# --------------------------------------------------------------------
# Create a dictionary containing the fields that need to be added.
# This dictionary is composed of a key, value pair where:
# key: field name
# value(s): (array containing the attributes for the fields)
# Dictionary structure/index:
# [Key]           [0]         [1]
# [Field name] = (Field type, Field alias)
fieldsDict = {
    "M81_PGA": ("DOUBLE", "M81_PGA"),
    "M84_PGA": ("DOUBLE", "M84_PGA"),
    "M87_PGA": ("DOUBLE", "M87_PGA"),
    "M90_PGA": ("DOUBLE", "M90_PGA"),
    "Frag_no":("TEXT", "Frag_no"), 
    "EP": ("DOUBLE", "EP"),
    "Hazard":("TEXT", "Hazard"),
    "Damage":("TEXT", "Damage"),
    "IM":("TEXT", "IM"),
    "IM_unit":("TEXT", "IM_unit"),
    "EQ_MAG":("TEXT", "EQ_MAG")
}

# Iterate through the dictionary and add the fields to the input table
for field, fieldAttributes in fieldsDict.items():
    arcpy.AddField_management(inputFeature, field, fieldAttributes[0], field_alias=fieldAttributes[1])
    # Print a success message for each field added in ArcGIS Pro
    message("Added '{}' field!".format(field))

# --------------------------------------------------------------------
# Calculate PGA values
# --------------------------------------------------------------------
# If the second parameter is false, print a message in ArcGIS Pro
if calculatePGA == False:
    message("Calculating PGA values skipped!")
else:
    # Get the path of the file containing the PGA values.
    # This file is called "BridgePGAs.xlsx"
    filePath = os.path.join(pgasPath, "BridgePGAs.xlsx")

    # Create object containing the file's data
    file = pandas.read_excel(filePath, sheet_name=0)

    # Array containing the fields that will be read and updated
    # Index:
    # [0, 1]          LONG_CALC, LAT_CALC
    # [2, 3, 4, 5]    M81_PGA, M84_PGA, M87_PGA, M90_PGA 
    pgaFields = [
        "LONG_CALC", "LAT_CALC", \
        "M81_PGA", "M84_PGA", "M87_PGA", "M90_PGA" 
    ]

    # Calulating PGA values message
    message("Calculating PGA values...")
    # Use the UpdateCursor function to iterate and update through every row in the given feature layer table
    with arcpy.da.UpdateCursor(inputFeature, pgaFields) as cursor:
        
        # row is the nth row in the table
        # cursor is the iterator
        for row in cursor:
            
            # Create dictionary to hold distances calculated from coordinates in row to all points in the Excel file
            # This dictionary is composed of a key, value pair where:
            # key: Object ID from Excel file
            # value: Distance calculated from current row to object ID coordinates (in miles)
            # Dictionary structure/index:
            # [Key]          
            # [Object ID] = Distance in miles
            distances = {}
            # Store longitude from current row
            long = row[0]
            # Store latitude from current row
            lat = row[1]
            
            # Loop through the entire Excel file to calculate the distance from the current 
            # row's coordinates to all the coordinates in the Excel file
            for index in file.index:
                # Store calculations in dictionary 
                distances[file["OBJECTID"][index]] = distance(lat, long, file["LATITUDE"][index], file["LONGITUDE"][index])

            # Return the shortest distance in a tuple where the structure is:
            # (Distance value, Object ID key)
            shortestDistance = min(zip(distances.values(), distances.keys()))

            # Update M81_PGA column
            row[2] = xlookup(shortestDistance[1],file["OBJECTID"],file["M81_PGA"])
            # Update M84_PGA column
            row[3] = xlookup(shortestDistance[1],file["OBJECTID"],file["M84_PGA"])
            # Update M87_PGA column
            row[4] = xlookup(shortestDistance[1],file["OBJECTID"],file["M87_PGA"])
            # Update M90_PGA column
            row[5] = xlookup(shortestDistance[1],file["OBJECTID"],file["M90_PGA"])

            # Update the row
            cursor.updateRow(row)
    # Print a message in ArcGIS Pro
    message("PGA values successfully added!")

# --------------------------------------------------------------------
# Clip features
# --------------------------------------------------------------------
# If the third parameter is false, print a message in ArcGIS Pro
if clip == False:
    message("Clipping features skipped!")
else:
    # Clipping features message
    message("Clipping features...")
    # New, temporary name for the clipped feature
    clippedInputFeature = os.path.join(infrastructuresPath, featureName + "Clipped")

    # Perform pairwise clip analysis to clip the input features given the clip features, and output the 
    # clipped feature layer to the "Infrastructures.gdb".
    # ArcGIS Pro does not allow two feature layers of the same type with the same name in the same geodatabase, thus
    # why we added "Clipped" to the end of the clipped feature layer.
    arcpy.PairwiseClip_analysis(inputFeature, clipFeatures, clippedInputFeature)

    # Delete the original input feature from the "Infrastructures.gdb".
    # We are deleting it because we don't want to have the original and the clipped version in the same place.
    arcpy.Delete_management(inputFeature)

    # We don't want to have the word "Clipped" at the end of the newly clipped feature layer, so we'll rename it.
    arcpy.Rename_management(clippedInputFeature, os.path.join(infrastructuresPath, featureName))

    # Success message
    message("{} clipped!".format(featureName))