import arcpy        # Arcpy package lets us work with ArcGIS Pro tools with Python
# Import math package to use in our distribution formulas
import math
from math import exp, log
# Import scipy package and tools to make our calculations accurate
from scipy.stats import norm, lognorm    
from scipy import interpolate
import os           # Import os package to be able to get the current directory

# ********************************************************************
# Helper Functions
# ********************************************************************
# --------------------------------------------------------------------
# Prints a message in ArcGIS Pro
# --------------------------------------------------------------------
def message(message):
    arcpy.AddMessage(message)

# --------------------------------------------------------------------
# Takes in the dictionary of damage states and their EP values and
# returns the state that is >= 0.5
# --------------------------------------------------------------------
def return_state(dict):
    # Sort dictionary into an array of tuples
    # Tuple array structure:
    # ((first state, first EP), (second state, second EP), (n state, n EP), etc.)
    sorted_dict = sorted(dict.items(), key=lambda x: x[1])
    
    # iterate through tuple array 
    # if b in (a, b) (which is the EP value) >= 0.50, return a (the damage state)
    for i, (a, b) in enumerate(sorted_dict):
        if float(b) >= 0.5:
            return (a, b)
    
    # if no value is >= 0.5, then the damage state will be none
    lowState = list(dict.keys())[0]     # the lowState will be the first key (state) in the dict
    lowEP = dict.get(lowState)          # using the lowState key, get the corresponding EP value

    # return none as the damage state and the EP value
    return ("None", lowEP)
    
# --------------------------------------------------------------------
# Function to return a dictionary containing the right number of damage states
# --------------------------------------------------------------------
def damage_states(fdDict, fragNo, numberOfStates, IM):
    # Explanation:
    # There is a max number of 5 different damage states an infrastructure can have. However, some infrastructures only
    # have 1 or a few more. Instead of creating one big dictionary that might have more states than it needs
    # (these values would appear as nulls in the dictionary), we can create the correct dictionary size depending on the
    # number of states stated in the fragility database under the 'No_of_damage_state' column.
    # Furthermore, once the number of states is known, we'll go ahead and calculate the EP values and store them in the dictionary that will be returned.

    # The fragility distribution respective to the fragility number (i.e. Discrete, Lognormal, Normal, Polynomial)
    fragDist = fdDict[fragNo][3] 
    # Store the formula in the 'Fragility_polynomial' column. If there is none, it's okay since it wouldn't be used anyway. 
    poly = fdDict[fragNo][17]
    # Short for IM Description, this is the string value in the 'IM' column in the fragility database (e.g. PGA, PGV, etc.). 
    IMDesc = fdDict[fragNo][1]

    # This dictionary will be the dictionary returned from this function.
    # This dictionary is composed of a key, value pair where:
    # key: Damage state (string)
    # value: EP value (string)
    # Dictionary structure/index:
    # [Key]            [0]     
    # [Damage state] = EP 
    damageStates = {}

    # Some infrastructures will require different fragility distribution functions to calculate their EP.
    # Therefore, the 'fragility_function' function returns the EP value using the correct fragility distribution function.
    if numberOfStates == 1:
        damageStates[fdDict[fragNo][5]] = fragility_function(fragDist, IM, fdDict[fragNo][6], fdDict[fragNo][7], poly, IMDesc)
    elif numberOfStates == 2:
        damageStates[fdDict[fragNo][5]] = fragility_function(fragDist, IM, fdDict[fragNo][6], fdDict[fragNo][7], poly, IMDesc)
        damageStates[fdDict[fragNo][8]] = fragility_function(fragDist, IM, fdDict[fragNo][9], fdDict[fragNo][10], poly, IMDesc)
    elif numberOfStates == 3:
        damageStates[fdDict[fragNo][5]] = fragility_function(fragDist, IM, fdDict[fragNo][6], fdDict[fragNo][7], poly, IMDesc)
        damageStates[fdDict[fragNo][8]] = fragility_function(fragDist, IM, fdDict[fragNo][9], fdDict[fragNo][10], poly, IMDesc)
        damageStates[fdDict[fragNo][11]] = fragility_function(fragDist, IM, fdDict[fragNo][12], fdDict[fragNo][13], poly, IMDesc)
    elif numberOfStates == 4:
        damageStates[fdDict[fragNo][5]] = fragility_function(fragDist, IM, fdDict[fragNo][6], fdDict[fragNo][7], poly, IMDesc)
        damageStates[fdDict[fragNo][8]] = fragility_function(fragDist, IM, fdDict[fragNo][9], fdDict[fragNo][10], poly, IMDesc)
        damageStates[fdDict[fragNo][11]] = fragility_function(fragDist, IM, fdDict[fragNo][12], fdDict[fragNo][13], poly, IMDesc)
        damageStates[fdDict[fragNo][14]] = fragility_function(fragDist, IM, fdDict[fragNo][15], fdDict[fragNo][16], poly, IMDesc)
    elif numberOfStates == 5:
        damageStates[fdDict[fragNo][5]] = fragility_function(fragDist, IM, fdDict[fragNo][6], fdDict[fragNo][7], poly, IMDesc)
        damageStates[fdDict[fragNo][8]] = fragility_function(fragDist, IM, fdDict[fragNo][9], fdDict[fragNo][10], poly, IMDesc)
        damageStates[fdDict[fragNo][11]] = fragility_function(fragDist, IM, fdDict[fragNo][12], fdDict[fragNo][13], poly, IMDesc)
        damageStates[fdDict[fragNo][14]] = fragility_function(fragDist, IM, fdDict[fragNo][15], fdDict[fragNo][16], poly, IMDesc)
        damageStates[fdDict[fragNo][18]] = fragility_function(fragDist, IM, fdDict[fragNo][19], fdDict[fragNo][20], poly, IMDesc)
    
    return damageStates     # Return dictionary

# ********************************************************************
# Fragility Functions
# ********************************************************************
# --------------------------------------------------------------------
# Lognormal Distribution Function 
# Reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html
# --------------------------------------------------------------------
def lognormal_cdf(IM, med, std) -> float:
    return lognorm.cdf(IM, float(std), scale = exp(log(float(med))))

# --------------------------------------------------------------------
# Normal Distribution 
# Reference: https://python.plainenglish.io/probability-distributions-with-python-discrete-continuous-1a11d7c8d717
# --------------------------------------------------------------------
def normal_cdf(IM, med, std) -> float:
    return (1 + math.erf((IM - float(med)) / math.sqrt(2) / float(std))) / 2

# --------------------------------------------------------------------
# Discrete Distribution Function  
# --------------------------------------------------------------------
def discrete(IM, med, std) -> float:
    # For discrete distributions, med and std are strings of values concatenated together where
    # the median acts as the IM values (e.g. PGA), and the std acts as the EP values (the values we want).
    # However, since these are fixed values and we want to be able to use any value we want as the IM, we'll
    # use linear interpolation to calculate the EP values that we don't know.
    # More on linear interpolation: https://www.statology.org/linear-interpolation-python/

    # First, convert med and std to individual arrays containing floats
    x = [float(num) for num in med.split()]
    y = [float(num) for num in std.split()]

    # If the IM value we choose is less than the first element in the x array (which should be the smallest one by default),
    # then linear interpolation will fail. 
    # We can get around this by defaulting the IM value to that first element. 
    if IM < x[0]:
        IM = x[0]

    # Use interpolate function to take in float arrays and develop a function.
    # The fill_value is set to ???extrapolate???, which means we can calculate points outside the data range.
    linearInterpolation = interpolate.interp1d(x, y, fill_value='extrapolate')

    # Utilize this interpolation function with the IM as an argument to calculate and return the EP value 
    return linearInterpolation(IM)

# --------------------------------------------------------------------
# Polynomial Distribution Function 
# --------------------------------------------------------------------
def polynomial(IM, polynomial, IMDesc, D = 1) -> float:
    # For polynomial distributions, there are formulas already written for us in the database under the
    # 'Fragility_polynomial' column. We take this formula (which is a string), and replace the IM description (e.g., PGA, PGV, etc.)
    # in this formula with the IM value given by the user.
    # The D parameter applies to buried pipelines and is the pipe diameter. This value will show up in the formula as
    # a 'D' and will be replaced by the D parameter. 
    # NOTE: as of the year 2022, when this script was created, we didn't have access to any data regarding buried pipelines.
    # Therefore, while this function works, this script does not take in a D parameter anywhere else. This is a 
    # feature that will need to be added. In the meantime, D is defaulted to 1 so the program doesn't return an error if it's called. 
    # Lastly, we use the eval function to evaluate this string as a python arithmetic and voila, we get our EP value.

    # Cast D parameter to string and wrap it in parantheses.
    # Some formulas use log, therefore, we want to make sure the D parameter is wrapped in parentheses.
    D = "(" + str(D) + ")"

    # Store the new string with the updated IM value in a temporary variable
    temp = str(polynomial).replace(IMDesc, str(IM)).replace("D", D).replace("^", "**")
    # Evaluate and return the calculated value.
    return eval(temp)                                   

# --------------------------------------------------------------------
# Fragility function evaluator 
# --------------------------------------------------------------------
def fragility_function(fragDist, IM, med, std, poly, IMDesc):
    # There are four different types of fragility distributions:
    #   1. Discrete
    #   2. Lognormal
    #   3. Normal
    #   4. Polynomial
    # These functions are defined above. 
    # This function computes which function will be used based on the fragDist (Fragility Distribution).
    # Once the correct funciton is chosen, it's called using the remaining paramters and returns the calculated value (the EP).
    if fragDist == "Discrete":
        return str(discrete(IM, med, std))
    elif fragDist == 'Lognormal':
        return str(lognormal_cdf(IM, med, std))
    elif fragDist == 'Normal':
        return str(normal_cdf(IM, med, std))
    elif fragDist == 'Polynomial':
        return str(polynomial(IM, poly, IMDesc))

# ********************************************************************
# Main Program
# ********************************************************************
# --------------------------------------------------------------------
# Setting directory
# --------------------------------------------------------------------
# First, we'll calculate the exceedance probability values of the bridges.
# Get the current directory of the script; it should look something like the following:
# {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP\Scripts
scriptsPath = os.getcwd()

# However, we want to get the parent directory of the script. We'll get something like this:
# {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP
# Then, in the same line, we compose a new directory.
# The resulting directory will look something like this:
# {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP\Projects\GADEP
projectPath = os.path.join(os.path.dirname(scriptsPath), "Projects", "GADEP")

# Now that we have the main project path stored as a variable, we can use it to 
# compose a path for other directories we need to traverse to
# Path to "Infrastructures.gdb"
infrastructuresPath = os.path.join(projectPath, "Infrastructures.gdb")

# To avoid typing out the entire directory everytime, we set the workspace to our composed directory.
# This lets us refer to the contents in the directory directly.
arcpy.env.workspace = infrastructuresPath

# --------------------------------------------------------------------
# Initializing variables
# --------------------------------------------------------------------
# Fragility Database
# This link takes you to where the Fragility Database is hosted on ArcGIS Online
fd = r"https://services1.arcgis.com/CD5mKowwN6nIaqd8/arcgis/rest/services/Fragility_Database_USA/FeatureServer/0"

# asset (infrastructure/map layer) is the first parameter
# This parameter is a list of values and its length will depend on how many map layers the user chooses
asset = arcpy.GetParameter(0)

# em is the earthquake magnitude
# The user has 4 choices:
# 1) 8.1 
# 2) 8.4
# 3) 8.7
# 4) 9.0
# These values come from the CSZ tool in OHELP: https://ohelp.oregonstate.edu/
em = arcpy.GetParameterAsText(1)

# This dictionary contains the earthquake magnitudes as its keys, and the corresponding column name as its values.
# These column names will (should) already be present in the map layer's attribute table, and should contain the
# PGA (Peak Ground Acceleration) values before running this script. 
# The em parameter will dictate what PGA column will be used in the rest of the program, i.e. what PGA values will be used
# in the calculations.
magDict = {
    '8.1': 'M81_PGA',
    '8.4': 'M84_PGA',
    '8.7': 'M87_PGA',
    '9.0': 'M90_PGA',
}

# Asset attribute table columns
# Index:
# [0]        Fragility no
# [1, 2]     Damage state, EP
# [3, 4, 5]  Hazard type, IM, IM unit
# [6, 7]     PGA column, Earthquake magnitude
assetFields = [ 
    'Frag_no', \
    'Damage', 'EP', \
    'Hazard', 'IM', 'IM_unit', \
    magDict.get(em), 'EQ_MAG'
]

# Fragility Database column name fields
# The order of these elements is the order they're in respective to the database
# Index:
# [0, 1, 2, 3]          Fragility_no, Hazard_type, IM, IM_unit
# [4, 5]                Fragility distribution, No. of damage states
# [6, 7, 8]             (1) Damage state, median, standard deviation
# [9, 10, 11]           (2) Damage state, median, standard deviation
# [12, 13, 14]          (3) Damage state, median, standard deviation
# [15, 16, 17]          (4) Damage state, median, standard deviation
# [18]                  Fragility polynomial
# [19, 20, 21]          (5) Damage state, median, standard deviation
fdFields = [ \
    'Fragility_no', 'Hazard_type', 'IM', 'IM_unit', \
    'Fragility_distribution', 'No_of_damage_state', \
    'Damage_state_1', 'Damage_state_med_1', 'Damage_state_std_1', \
    'Damage_state_2', 'Damage_state_med_2', 'Damage_state_std_2', \
    'Damage_state_3', 'Damage_state_med_3', 'Damage_state_std_3', \
    'Damage_state_4', 'Damage_state_med_4', 'Damage_state_std_4', \
    'Fragility_polynomial', \
    'Damage_state_5', 'Damage_state_med_5', 'Damage_state_std_5'
]

# Use list comprehension to build a dictionary from a da.SearchCursor
# This dictionary is composed of a key, value pair where:
# key: fragility number (string)
# value(s): (array containing the values for each of the columns stated) (strings)
# Dictionary structure/index:
# [Key]            [0]           [1] [2]
# [Fragility_no] = (Hazard_type, IM, IM_unit, 
#                   [3]                     [4]
#                   Fragility_distribution, No_of_damage_state
#                   [5]             [6]                 [7]
#                   Damage_state_1, Damage_state_med_1, Damage_state_std_1, 
#                   [8]             [9]                [10]
#                   Damage_state_2, Damage_state_med_2, Damage_state_std_2, 
#                   [11]            [12]                [13]
#                   Damage_state_3, Damage_state_med_3, Damage_state_std_3, 
#                   [14]            [15]                [16]
#                   Damage_state_4, Damage_state_med_4, Damage_state_std_4, 
#                   [17]
#                   Fragility_polynomial, 
#                   [18]            [19]                [20]
#                   Damage_state_5, Damage_state_med_5, Damage_state_std_5)
fdDict = {row[0]:(row[1:]) for row in arcpy.da.SearchCursor(fd, fdFields)}

# Loop through the asset list (the different map layers chosen by the user).
# Basically, we're updating each attribute table for each map layer that is chosen by the user.
for assetIndex in asset:
    # Use the UpdateCursor function to iterate and update through every row in the given feature class table
    with arcpy.da.UpdateCursor(assetIndex, assetFields) as cursor:
        # row is the nth row in the table
        # cursor is the iterator
        for row in cursor:
            # row[0] = Fragility_no column
            fragNo = str(row[0])
            
            # check if the current fragility number exists in the fdDict
            if fragNo in fdDict:
                IM = (row[6])

                # The damage_states function is called which returns a dictionary
                # composed of a key, value pair where:
                # key: Damage state (string)
                # value: Exeedence probability (EP) (string)
                # Dictionary structure/index:
                # [Key]            [0]         
                # [Damage state] = EP
                damageStates = damage_states(fdDict, fragNo, fdDict[fragNo][4], IM)

                # Use return_state function to return the "optimal" state, i.e. the state that is most likely to occur and be relevant
                optimalState = return_state(damageStates)

                # row[1] = Damage_State column
                row[1] = optimalState[0]        # Update what the value is going to be in the Damage_State column
                # row[2] = EP column
                row[2] = optimalState[1]        # Update what the value is going to be in the EP column
                # row[3] = Hazard_type column
                row[3] = fdDict[fragNo][0]      # Update the Hazard_type column to contain the type of hazard as stated in the fragility database
                # row[4] = IM column
                row[4] = fdDict[fragNo][1]      # Update the IM column to contain the IM as stated in the fragility database
                # row[5] = IM_unit column
                row[5] = fdDict[fragNo][2]      # Update the IM_unit column to contain the unit of measure as stated in the fragility database
                # row[7] = Earthquake magnitude
                row[7] = str(em)                # Update the EQ_MAG column to contain the earthquake magnitude chosen 

                # Update the row
                cursor.updateRow(row)
    # Print a message in ArcGIS Pro
    message("{} SIMULATION SUCCESSFUL!".format(assetIndex))

# Delete dictionary
del fdDict
