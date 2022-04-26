import arcpy        # Arcpy package lets us work with ArcGIS Pro tools with Python

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
# The first paramter is a list of the tables whose tables will add the new field(s)
inputTables = arcpy.GetParameter(0)

# The second parameter is a value table
# How they work: https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/valuetable.htm
fields = arcpy.GetParameter(1)

# Iterate through the input tables list and add the fields to each table
for table in inputTables:
    # Iterate 'row' number of times, 'row' being the number of rows in the value table
    for row in range(fields.rowCount):
        # Add the field to the table
        # Using the AddField tool, we set the field name, its alias, and its type
        arcpy.AddField_management(table, fields.getValue(row, 0), fields.getValue(row, 1) , field_alias=fields.getValue(row, 0))
        
        # Print a success message for each field added in ArcGIS Pro
        message("Added '{}' field to {}!".format(fields.getValue(row, 0), table.name))

# Print a success message in ArcGIS Pro
message("Fields successfully added!")