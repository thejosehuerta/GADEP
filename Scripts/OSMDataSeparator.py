import shutil
import arcpy        # Arcpy package lets us work with ArcGIS Pro tools with Python
import os           # os library lets us work with directories
import zipfile
import shutil
# ********************************************************************
# Helper Functions
# ********************************************************************
# --------------------------------------------------------------------
# Prints a message in ArcGIS Pro
# --------------------------------------------------------------------
def message(message):
    arcpy.AddMessage(message)

# ********************************************************************
# Main Program
# ********************************************************************
# --------------------------------------------------------------------
# Initializing variables
# --------------------------------------------------------------------
featureLayer = arcpy.GetParameter(0)        # The feature layer that will be filtered
flField = arcpy.GetParameterAsText(1)       # The field belonging to the feauture layer 
output = arcpy.GetParameterAsText(2)        # The output directory

# Message printed out in ArcGIS Pro to let the user know what is being exported and where
message("The values in the '{}' field will be exported as a shapefile to '{}'"
    .format(flField, output))

# --------------------------------------------------------------------
# Loop through table
# --------------------------------------------------------------------
# da SearchCursor function will loop through the feature layer's attribute table, and 
# depending on the field chosen, will create a new feature layer containing only the values 
# belonging to said field
with arcpy.da.SearchCursor(featureLayer, flField) as cursor:
    # Since more than likely we will have duplicate value in the chosen field, we'll 
    # store the unique values in a list
    flFieldValues = []

    # Create a new folder in the output directory
    # Example: if the output directory is your Downloads folder, a new folder
    # will be created there: \Downloads\{feature layer name}
    outputFolder = os.path.join(output, featureLayer.name)
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
        # Folder created successfully message
        message("'{}' directory succesfully created!".format(outputFolder))

    # Loop through the attribute table
    for row in cursor:
        # If the current value DOES NOT exist in the unique value list, then:
        if not row[0] in flFieldValues:
            # (1) append the current value to it
            flFieldValues.append(row[0])
            # (2) Create a 'where' clause that will be used as an SQL expression to filter the feature layer's attribute table
            whereClause = "{} = \'{}\'".format(flField, row[0])

            # Use the Select_analysis tool to create the new filtered feature layer and output it to the output directory selected by the user
            arcpy.Select_analysis(featureLayer, os.path.join(outputFolder, row[0]), whereClause)

            # Update message
            message("{} feature layer created!".format(row[0]))
# Success message
message("All feature layers created successfully!")