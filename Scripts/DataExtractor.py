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
# --------------------------------------------------------------------
# Initializing variables
# --------------------------------------------------------------------
inputTable = arcpy.GetParameter(0)                  # This is the table from the feature layer that will be updated
inputTableJoinField = arcpy.GetParameterAsText(1)   # This is the join field 
joinTable = arcpy.GetParameter(2)                   # This is the join table containing the data that will be added to the input table
joinTableField = arcpy.GetParameter(3)              # This is the join field. It must be the same as the join field in the previous parameter
dataToExtract = arcpy.GetParameter(4)               # This is a list composed of the fields containing the data that will be "extracted"

# Input table fields - composed of the input table join field concatendated with the dataToExtract fields
itFields = [inputTableJoinField] + dataToExtract

# Join table fields - composed of the input table join field concatendated with the dataToExtract fields
jtFields = [joinTableField] + dataToExtract

# Use list comprehension to build a dictionary from a da.SearchCursor
# Join table dictionary - composed of a key, value pair where:
# key: Join table field 
# value(s): (array containing the values for each of the fields in the dataToExtract list)
jtDict = {row[0]:(row[1:]) for row in arcpy.da.SearchCursor(joinTable, jtFields)}

# Use the UpdateCursor function to iterate and update through every row in the given feature class table
with arcpy.da.UpdateCursor(inputTable, itFields) as cursor:
    # row is the nth row in the table
    # cursor is the iterator
    for row in cursor:
        # row[0] = Join field value (this is generally the object ID)
        objectID = row[0]
        
        # check if the current object exists in the jtDict
        if objectID in jtDict:
            
            # Update the current row given the fields chosen by the user
            for data in range(len(dataToExtract)):
                row[data + 1] = jtDict[objectID][data]
        
            # Update the row
            cursor.updateRow(row)

# Print a message in ArcGIS Pro
message("{} DATA EXTRACTION SUCCESSFUL!".format(inputTable))