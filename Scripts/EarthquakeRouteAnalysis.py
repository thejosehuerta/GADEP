import arcpy        # Arcpy package lets us work with ArcGIS Pro tools with Python
import os           # Import os package to be able to get the current directory
# Import random package
import random

# ********************************************************************
# Helper Functions
# ********************************************************************
# --------------------------------------------------------------------
# Prints a message in ArcGIS Pro
# --------------------------------------------------------------------
def message(message):
    arcpy.AddMessage(message)

# --------------------------------------------------------------------
# Checks a string if it contains blanks. If it does, get rid of them.
# --------------------------------------------------------------------
def name_checker(name):
    # If it contains a blank, change the case of the sring to title case (it looks better), and get rid of the blanks
    return name.title().replace(" ", "") if " " in name else name

# --------------------------------------------------------------------
# Checks if a value is an empty string or not.
# If it is, return a default value, else return the original value
# --------------------------------------------------------------------
def analysis_name(parameter, defaultName): 
    return defaultName if parameter == "" or parameter == " " or parameter == "#" else name_checker(parameter)

# --------------------------------------------------------------------
# Calculate an array of random RGB values. 
# --------------------------------------------------------------------
def random_rgb():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    # Return RGB array with an alpha value of 100.
    # The alpha value dictates the color transparency - we don't wan't any transparency.
    return [r, g, b, 100]

# --------------------------------------------------------------------
# This function converts a non-point feature layer to a point feature layer.
# The first paramter is the non-point feature layer, and the second parameter is the
# directory where the point feature layer will be written to.
# --------------------------------------------------------------------
def feature_to_point(inFeature, outFeature):
    # Get descriptive properties of the feature layer to be converted
    inFeatureDesc = arcpy.Describe(inFeature)

    # If the feature layer is already a point feature, then return the point feature
    if inFeatureDesc.shapeType == "Point":
        return inFeature
    else:
        # Status message
        message("Your input is not a point feature, it will be converted to one in order to continue with the analysis.")

        # Perform the conversion
        arcpy.FeatureToPoint_management(inFeature, outFeature, "INSIDE")
        # Return the directory where the point feature is located
        return outFeature

# ********************************************************************
# Main Program
# ********************************************************************
# ////////////////////////////////////////////////////////////////////
# Earthquake Simulation
# ////////////////////////////////////////////////////////////////////
# --------------------------------------------------------------------
# Setting directories
# --------------------------------------------------------------------
# First, we'll calculate the exceedance probability values of the bridges.
# Get the current directory of the script; it should look something like the following:
# {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP Project\Scripts
scriptsPath = os.getcwd()

# However, we want to get the parent directory of the script. We'll get something like this:
# {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP Project
# Then, in the same line, we compose a new directory.
# The resulting directory will look something like this:
# {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP Project\Projects\GADEP
projectPath = os.path.join(os.path.dirname(scriptsPath), "Projects", "GADEP")

# Now that we have the main project path stored as a variable, we can use it to 
# compose a path for other directories we need to traverse to
# Path to "Infrastructures.gdb"
infrastructuresPath = os.path.join(projectPath, "Infrastructures.gdb")

# Path to "NetworkAnaysis.gdb"
networkAnalysisPath = os.path.join(projectPath, "NetworkAnalysis.gdb")

# Path to "TransportationNetwork.gdb"
transportationNetworkPath = os.path.join(projectPath, "TransportationNetwork.gdb")

# Path to the "GADEP.gdb"
gadepPath = os.path.join(projectPath, "GADEP.gdb")

# ////////////////////////////////////////////////////////////////////
# Disaster impact - bridges
# ////////////////////////////////////////////////////////////////////

# Get the boolean value of the first parameter.
runDisasterImpact = arcpy.GetParameter(0)

# Filtered bridges layer to be used in the Select_analysis function
bridgesFiltered = os.path.join(gadepPath, "BridgesFiltered")   

# If the boolean is true, then the Disaster Impact tool will be ran using only the bridges as
# its parameter.
if runDisasterImpact:
    # Status messsage
    message("Running Disaster Impact tool...")
    # Bridges directory
    bridges = os.path.join(infrastructuresPath, "Bridges")
    # The earthquake magnitude chosen
    em = arcpy.GetParameterAsText(1)

    # The Disaster Impact toolbox directory
    gadepToolBox = os.path.join(projectPath, "GADEP.tbx")

    # Import the Disaster Impact toolbox
    arcpy.ImportToolbox(gadepToolBox, "tool")
    # Run the Disaster Impact tool.
    # Here we use the string "Bridges" because the Disaster Impact tool checks the 
    # names of the feature layers contained in the "Infrastructures.gdb", and not
    # the full path of them.
    arcpy.DisasterImpact_tool("Bridges", em)

    # Success message
    message("Disaster Impact simulation successful!")

    # --------------------------------------------------------------------
    # BridgesFiltered layer for routing
    # --------------------------------------------------------------------
    # After the simulation is complete, we'll create a new map layer called "BridgesFiltered".
    # Using an SQL expression, this layer will consist of specific bridges given the expression.
    # This layer will serve as the PointBarriers feature for the routing.

    # The SQL expression that dictates what features will be selected
    whereClause = 'Damage = \'Slight\' Or Damage = \'Moderate\' Or Damage = \'Extensive\' Or Damage = \'Complete\''     

    # In the case that the bridge layer does not exist in the "Infrastructures.gdb", it will throw an error.
    # Wrap the next function in a try-except statement to handle this case.
    try: 
        # The Select_analysis will take in the latest data in the "Bridges" feature layer and create/replace the values of the 
        # 'BridgesFiltered' feature layer leaving only the values resulting from the SQL expression
        arcpy.Select_analysis(bridges, bridgesFiltered, whereClause)
    except:
        message("A possible error occurred but it was caught. \n\
            After this script completes the simulation, it filters the 'Bridges' layer. \n\
            It's possible that this layer does not exist yet.")

message("Preparing for route analysis...")

# ////////////////////////////////////////////////////////////////////
# Routing Analysis
# ////////////////////////////////////////////////////////////////////
# --------------------------------------------------------------------
# Initializing variables for routing
# --------------------------------------------------------------------
network = os.path.join(transportationNetworkPath, "OregonNetwork", "OregonNetworkDataset")  # Analysis network
travelMode = "Vehicle"                                                                      # Currently the only mode of transportation
# The name of the output layer.
# We concatenate a string of random integers at the end in order to create a unique layer each time.
defaultLayerName = "ClosestFacilities" + str(random.randint(100000,999999))  

# The incidents, facilities, and barriers that will be used in the analysis
incidents = arcpy.GetParameter(2)
incidentsWhereClause = arcpy.GetParameter(3)        # The SQL expression that will filter the incidents feature layer
facilities = arcpy.GetParameter(4)
facilitiesWhereClause = arcpy.GetParameter(5)       # The SQL expression that will filter the incidents feature layer
numberOfFacilities = arcpy.GetParameter(6)          # The number of facilities parameter value
overwrite = arcpy.GetParameter(8)                   # The checkmark box 

# Try to onvert the number of facilities parameter to an integer
try:
    numberOfFacilities = int(numberOfFacilities)
# If we can't, then it's not a valid value. Default the value to 1.
except:
    numberOfFacilities = 1

# The checkmark box is checked, then the exisitng analysis layer will be overwritten
# else, a new analysis layer will be created
if overwrite:
    layerName = arcpy.GetParameter(9)
    outputLayerFile = os.path.join(networkAnalysisPath, layerName)
    arcpy.Delete_management(outputLayerFile)

    message("Exisiting route layer will be overwritten.")
else:
    layerName = analysis_name(arcpy.GetParameter(7), defaultLayerName)
    outputLayerFile = os.path.join(networkAnalysisPath, layerName)
    message("New route layer will be created.")

# --------------------------------------------------------------------
# Filter incidents and facilities
# --------------------------------------------------------------------
# Status message
message("Applying your filters (if you selected any)...")

# If the incidents feature layer is not a point feature, e.g., a polygon shape, it will be converted
# into a point feature. Else, it will not change.
incidents = feature_to_point(incidents, os.path.join(gadepPath, "IncidentsPoints"))

# The path for a new feature layer called "IncidentsFiltered"
incidentsFiltered = os.path.join(gadepPath,"IncidentsFiltered")

# The Select_analysis will take in the latest data in the "incidents" feature layer and create (or replace, if it exists) the values of the 
# 'IncidentsFiltered' feature layer per the SQL expression
arcpy.Select_analysis(incidents, incidentsFiltered, incidentsWhereClause)

# If the facilities feature layer is not a point feature, e.g., a polygon shape, it will be converted
# into a point feature. Else, it will not change.
facilities = feature_to_point(facilities, os.path.join(gadepPath, "FacilitiesPoints"))

# The path for a new feature layer called "IncidentsFiltered"
facilitiesFiltered = os.path.join(gadepPath,"FacilitiesFiltered")

# The Select_analysis will take in the latest data in the "incidents" feature layer and create (or replace, if it exists) the values of the 
# 'IncidentsFiltered' feature layer per the SQL expression
arcpy.Select_analysis(facilities, facilitiesFiltered, facilitiesWhereClause)

# --------------------------------------------------------------------
# Start analysis
# Reference: https://pro.arcgis.com/en/pro-app/latest/arcpy/network-analyst/closestfacility.htm
# --------------------------------------------------------------------
# Status message
message("Preparing route analysis...")

# Network name
ndLayerName = "OregonNetworkDataset"

# Create a network dataset layer and get the desired travel mode for analysis
arcpy.nax.MakeNetworkDatasetLayer(network, ndLayerName)

# Instantiate a ClosestFacility solver object
closestFacility = arcpy.nax.ClosestFacility(network)
# Set properties
closestFacility.travelMode = travelMode     # The mode of travel
# The number of facilities the analysis will find for each incident
closestFacility.defaultTargetFacilityCount = 1 if numberOfFacilities == "" or numberOfFacilities == "#" else int(numberOfFacilities)
# Load inputs
closestFacility.load(arcpy.nax.ClosestFacilityInputDataType.Facilities, facilitiesFiltered)
closestFacility.load(arcpy.nax.ClosestFacilityInputDataType.Incidents, incidentsFiltered)
closestFacility.load(arcpy.nax.ClosestFacilityInputDataType.PointBarriers, bridgesFiltered)

# Status message
message("Running analysis... Finding the nearest facilities.".format(numberOfFacilities))

# --------------------------------------------------------------------
# Solve and export analysis
# --------------------------------------------------------------------
result = closestFacility.solve()

# Export the analysis as a route layer
result.export(arcpy.nax.ClosestFacilityOutputDataType.Routes, outputLayerFile)

# Status message
message("Route analysis successful! Exporting the route layer...")

# Add the route layer to the map
aprx = arcpy.mp.ArcGISProject("CURRENT")
aprxMap = aprx.listMaps("Map")[0] 
aprxMap.addDataFromPath(outputLayerFile)

# --------------------------------------------------------------------
# Adjust route layer properties
# References:
# https://pro.arcgis.com/en/pro-app/latest/arcpy/mapping/uniquevaluerenderer-class.htm
# --------------------------------------------------------------------
# Once the layer is added to the map, adjust its physical properties.
# Get the layer first.
lyr = aprxMap.listLayers(layerName)[0]
# Symbology object with adjustable properties
sym = lyr.symbology

# Update the symbology to render a unique color for every unique IncidentOID value
sym.updateRenderer('UniqueValueRenderer')
sym.renderer.fields = ['IncidentOID']

# Loop through the groups in the current unique value render.
for grp in sym.renderer.groups:
    # Loop through the values in the group items (the group items are the values in the chosen renderer fields)
    for itm in grp.items:
        # For each layer:
        # 1. Change the symbol style
        itm.symbol.applySymbolFromGallery("Marker Arrow Line 3 (Bold)")
        # 2. Set a random color to it
        itm.symbol.outlineColor = {'RGB': random_rgb()}   

# Apply new properties
lyr.symbology = sym

# Print success message
message("Script completed successfully!")