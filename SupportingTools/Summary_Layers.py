import arcpy
import os
import re
from numpy import median, mean
from operator import itemgetter

# Project folder path
pf_path = r'C:\Users\A02079569\Box\ET_AL\Projects\USA\Idaho\BRAT\FY1819\wrk_Data'
# Project Area Split by HUC8
huc8_shp_input = r'C:\Users\A02079569\Desktop\SummaryLayersTool\OtherInputs\HUC8\WBDHU8_ProjectArea.shp'
# Project Area Split by HUC6
huc6_shp = r'C:\Users\A02079569\Desktop\SummaryLayersTool\OtherInputs\HUC6\WBDHU6.shp'
# fix A shapefile containing all streams for the entire area
all_streams = r'C:\Users\A02079569\Desktop\SummaryLayersTool\OtherInputs\Merged\Data_Capture_Validation_US.shp'
# A shapefile that has the boundary for the entire project. Used for clipping, and for statewide data
project_boundary = r'C:\Users\A02079569\Desktop\SummaryLayersTool\OtherInputs\IdahoBoundary\Idaho_Boundary.shp'
# Project Area Split by region. This will be ignored if calculate_regions is false
region_shp = r'C:\Users\A02079569\Desktop\SummaryLayersTool\OtherInputs\Regions\Administrative_Regions.shp'
# Output Folder where everything will be generated
output_folder = r'C:\Users\A02079569\Desktop\SummaryLayersTool\Output'
# Folder where symbology is stored
symbology_folder = r'C:\Users\A02079569\Desktop\SummaryLayersTool\Symbology'
# The BRAT run folder that will be referenced for each watershed
run_folder = 'BatchRun_01'
# A boolean that decides if state should be calculated
calculate_state = True
# A boolean that decides if regions should be calculated
calculate_regions = True
# A boolean that decides if huc6 should be calculated
calculate_huc6 = True
# A boolean that decides if huc8 should be calculated
calculate_huc8 = True

# If you are getting a lot of folder missing errors, it might be because your folders contain
# abbreviations that aren't present in the huc_shp shapefile. Use this list to fix that,
# or leave the list blank if you have no issues.

# This list contains all abbreviations used in the folder structure
ab_list = [
           ['ShortenThis', 'ToThis'],
           ['New York City', 'NYC']

]


def main():
    # Environment settings
    arcpy.env.overwriteOutput = True

    # Create Folder Structure
    boolList = [calculate_state, calculate_regions, calculate_huc6, calculate_huc8]
    folderStructureList = create_folder_structure(boolList)

    # Add all new fields to the huc_shp
    # ***UPDATE HERE FOR NEW SUMMARIES*** [A]
    fieldList = ['oCC_EX',
                 'oCC_HPE',
                 'oPBRC_CR',
                 'oPBRC_UD',
                 'mCC_EXvHPE',
                 'CvR_Cons',
                 'CvR_Trans',
                 'oPBRC_UI'
                 ]

    # Initializes a list that holds all of the added functions
    # ***UPDATE HERE FOR NEW SUMMARIES*** [A]
    functionList = [calculate_existing_capacity,
                    calculate_historic_capacity,
                    calculate_low_hanging_fruit,
                    calculate_building_possible,
                    calculate_capacity_remaining,
                    calculate_beaver_conservation,
                    calculate_potential_translocation,
                    calculate_considerable_risk
                    ]

    # Create filepaths for each symbology layer, put them in a list
    # ***UPDATE HERE FOR NEW SUMMARIES*** [B]
    symbologyList = add_file_structure_symbology(["Summary_Labels.lyr",
                                                  "Summary_ExistingCapacity.lyr",
                                                  "Summary_HistoricCapacity.lyr",
                                                  "Summary_LowHanging.lyr",
                                                  "Summary_BuildingPossible.lyr",
                                                  "Summary_CapacityRemaining.lyr",
                                                  "Summary_BeaverConservation.lyr",
                                                  "Summary_PotentialTranslocation.lyr",
                                                  "Summary_ConsiderableRisk.lyr"
                                                 ])

    # Create layer names for each layer, put them in a list
    # ***UPDATE HERE FOR NEW SUMMARIES*** [B]
    layerNameList = ["Reference Labels",
                     "Median Existing Capacity",
                     "Median Historic Capacity",
                     "Percent \"Low Hanging Fruit\"",
                     "Percent Dam Building Possible",
                     "Percent of Capacity Remaining",
                     "Percent Immediate - Beaver Conservation",
                     "Percent Immediate - Potential Translocation",
                     "Percent Considerable Risk"]

    print "Clipping Network, this might take some time."
    clippedNetwork = clip_to_boundary(all_streams, project_boundary, output_folder)
    #clippedNetwork = r"C:\Users\A02079569\Desktop\SummaryLayersTool\Output\TempNetwork.shp"
    print "Done Clipping!"

    print_barrier()

    if calculate_state:
        create_state_layers(folderStructureList[0], fieldList, functionList, symbologyList, layerNameList, clippedNetwork, project_boundary)
        print_barrier()
    if calculate_regions:
        create_region_layers(folderStructureList[1], fieldList, functionList, symbologyList, layerNameList, clippedNetwork, region_shp, project_boundary)
        print_barrier()
    if calculate_huc6:
        create_huc6_layers(folderStructureList[2], fieldList, functionList, symbologyList, layerNameList, clippedNetwork, huc6_shp, project_boundary)
        print_barrier()
    if calculate_huc8:
        create_huc8_layers(folderStructureList[3], fieldList, functionList, symbologyList, layerNameList,
                           all_streams, huc8_shp_input, project_boundary)
        print_barrier()

    delete_layers([clippedNetwork])
    print "COMPLETE"


def print_barrier():
    print "______________________________________"
    print "______________________________________"
    print "______________________________________\n"


def create_folder_structure(boolList):
    folderStructureList = []
    nameList = ['Statewide', "By_Region", "By_HUC6", "By_HUC8"]
    for name, bool in zip(nameList, boolList):
        if bool:
            folderStructureList.append(make_folder(output_folder, name))
        else:
            folderStructureList.append(name + " is not being calculated.")
    return folderStructureList


def make_folder(path_to_location, new_folder_name):
    """
    Makes a folder and returns the path to it
    :param path_to_location: Where we want to put the folder
    :param new_folder_name: What the folder will be called
    :return: String
    """
    newFolder = os.path.join(path_to_location, new_folder_name)
    if not os.path.exists(newFolder):
        os.mkdir(newFolder)
    return newFolder


def add_file_structure_symbology(filenames):
    # Takes input symbology names and adds the symbolgy folder structure. Returns a list.

    temp = []
    for filename in filenames:
        temp.append(os.path.join(symbology_folder, filename))
    return temp


def clip_to_boundary(network, boundary, folder):

    tempLocation = os.path.join(folder, "TempNetwork.shp")
    arcpy.Clip_analysis(network, boundary, tempLocation)
    return tempLocation


def clip_area(area, boundary, folder):

    tempLocation = os.path.join(folder, "TempClip.shp")
    arcpy.Clip_analysis(area, boundary, tempLocation)
    return tempLocation


def add_fields(fieldnames, shapefile):
    # Adds all field names to the_shp, as well as returning a list with all of the field names

    temp = []
    for field in fieldnames:
        temp.append(field)
        arcpy.AddField_management(shapefile, field, 'DOUBLE')
    return temp


def sort_abbreviations(abList):
    # Sorts the abbreviation list by length of the unnabreviated string. This is necessary for it to function correctly

    for ab in abList:
        ab.append(len(ab[0]))
    abList = sorted(abList, key=itemgetter(2), reverse=True)
    return abList


def remove_prefix(text, prefix):  # Cuts off the start of a string, as long as it starts with a certain prefix

    return text[text.startswith(prefix) and len(prefix):]


def clean_huc_name(text, abbreviationList):
    # Removes any innapropriate characters from a huc_name, replaces necessary abbreviations

    clean = re.sub('[. "-,\']', '', text)
    for abbreviation in abbreviationList:
        temp = clean.replace(abbreviation[0], abbreviation[1])
        clean = temp
    return clean


def clean_filepath(text):  # Removes any innapropriate characters from a filepath

    return (re.sub('[ ",-]', '', text))


def add_no_data(dataListList):  # For every data list, add in a value of -1 to represent NoData
    for dataList in dataListList:
        dataList.append(-1)


def check_field(lyr, field):
    field_names = [f.name for f in arcpy.ListFields(lyr)]
    return field in field_names


def missing_field(field):
    # This should be updated to print to a log as well.
    print field + " is missing for this area, data will be incomplete",


def create_state_layers (outputFolder, fieldList, functionList, symbologyList, layerNameList, network, state):

    print "Calculating layers for entire state",

    fieldList = add_fields(fieldList, state)
    dataListList = [[] for i in range(len(functionList))]
    layerPathList = []

    for dataList, function in zip(dataListList, functionList):
        dataList.append(function(network))
        print ".",

    for field, dataList in zip(fieldList, dataListList):
        update_huc(field, state, dataList)

    print "\n"
    layerPathList = make_layers(state, symbologyList, layerNameList, outputFolder)
    package_layers(layerPathList, outputFolder)
    delete_layers(layerPathList)

    print "\nDone with state!"


def create_huc6_layers (outputFolder, fieldList, functionList, symbologyList, layerNameList, network, huc6_shp, state):

    print "Calculating layers for HUC6s"

    fieldList = add_fields(fieldList, huc6_shp)
    dataListList = [[] for i in range(len(functionList))]
    layerPathList = []

    clipLocation = clip_area(huc6_shp, state, outputFolder)

    huc6s_list = [row[0] for row in arcpy.da.SearchCursor(clipLocation, 'NAME')]

    for huc6 in huc6s_list:
        print '\n\nCalculating data for ' + str(huc6),
        sqlString = (""""NAME" = """ + """'""" + str(huc6) + """'""")
        tempArea = arcpy.MakeFeatureLayer_management(clipLocation, 'temp_huc6.shp', sqlString)
        tempAreaPath= os.path.join(outputFolder, "TempBorder.lyr")
        arcpy.SaveToLayerFile_management(tempArea, tempAreaPath)
        tempNetwork = arcpy.MakeFeatureLayer_management(network, 'TempNetworkFull')
        tempNetworkPath = os.path.join(outputFolder, "TempNetworkFull.lyr")
        arcpy.SaveToLayerFile_management(tempNetwork, tempNetworkPath)
        clippedRegion = clip_to_boundary(tempNetworkPath, tempAreaPath, outputFolder)
        for dataList, function in zip(dataListList, functionList):
            if huc6 == "Missouri Headwaters":
                dataList.append(-1)
            else:
                dataList.append(function(clippedRegion))
            print ".",
        delete_layers([clippedRegion])
        delete_layers([tempAreaPath])
        delete_layers([tempNetworkPath])

    for field, dataList in zip(fieldList, dataListList):
        update_huc(field, clipLocation, dataList)

    print "\n"
    layerPathList = make_layers(clipLocation, symbologyList, layerNameList, outputFolder)
    package_layers(layerPathList, outputFolder)
    delete_layers(layerPathList)
    delete_layers([clipLocation])

    print "\nDone with HUC6s!"


def create_region_layers (outputFolder, fieldList, functionList, symbologyList, layerNameList, network, region_shp, state):

    print "Calculating layers for Regions"

    fieldList = add_fields(fieldList, region_shp)
    dataListList = [[] for i in range(len(functionList))]
    layerPathList = []

    clipLocation = clip_area(region_shp, state, outputFolder)

    regions_list = [row[0] for row in arcpy.da.SearchCursor(clipLocation, 'NAME')]

    for region in regions_list:
        print '\n\nCalculating data for ' + str(region),
        sqlString = (""""NAME" = """ + """'""" + str(region) + """'""")
        tempArea = arcpy.MakeFeatureLayer_management(clipLocation, 'temp_region.shp', sqlString)
        tempAreaPath= os.path.join(outputFolder, "TempBorder.lyr")
        arcpy.SaveToLayerFile_management(tempArea, tempAreaPath)
        tempNetwork = arcpy.MakeFeatureLayer_management(network, 'TempNetworkFull')
        tempNetworkPath = os.path.join(outputFolder, "TempNetworkFull.lyr")
        arcpy.SaveToLayerFile_management(tempNetwork, tempNetworkPath)
        clippedRegion = clip_to_boundary(tempNetworkPath, tempAreaPath, outputFolder)
        for dataList, function in zip(dataListList, functionList):
            dataList.append(function(clippedRegion))
            print ".",
        delete_layers([clippedRegion])
        delete_layers([tempAreaPath])
        delete_layers([tempNetworkPath])

    for field, dataList in zip(fieldList, dataListList):
        update_huc(field, clipLocation, dataList)

    print "\n"
    layerPathList = make_layers(clipLocation, symbologyList, layerNameList, outputFolder)
    package_layers(layerPathList, outputFolder)
    delete_layers(layerPathList)
    delete_layers([clipLocation])

    print "\nDone with Regions!"


def create_huc8_layers (outputFolder, fieldList, functionList, symbologyList, layerNameList, network, huc8_shp, state):

    print "Calculating layers for HUC8s"

    fieldList = add_fields(fieldList, huc8_shp)
    dataListList = [[] for i in range(len(functionList))]
    layerPathList = []

    clipLocation = huc8_shp

    huc8s_list = [row[0] for row in arcpy.da.SearchCursor(clipLocation, 'NAME')]

    for huc8 in huc8s_list:
        hucString = str(huc8)
        print '\n\nCalculating data for ' + hucString,
        if hucString == """Coeur d'Alene Lake""":
            hucString = """Coeur d''Alene Lake"""
        if hucString == """South Fork Coeur d'Alene""":
            hucString = """South Fork Coeur d''Alene"""
        if hucString == """Upper Coeur d'Alene""":
            hucString = """Upper Coeur d''Alene"""
        sqlString = (""""NAME" = """ + """'""" + hucString + """'""")
        tempArea = arcpy.MakeFeatureLayer_management(clipLocation, 'temp_huc8.shp', sqlString)
        tempAreaPath= os.path.join(outputFolder, "TempBorder.lyr")
        arcpy.SaveToLayerFile_management(tempArea, tempAreaPath)
        tempNetwork = arcpy.MakeFeatureLayer_management(network, 'TempNetworkFull')
        tempNetworkPath = os.path.join(outputFolder, "TempNetworkFull.lyr")
        arcpy.SaveToLayerFile_management(tempNetwork, tempNetworkPath)
        clippedRegion = clip_to_boundary(tempNetworkPath, tempAreaPath, outputFolder)
        for dataList, function in zip(dataListList, functionList):
            dataList.append(function(clippedRegion))
            print ".",
        delete_layers([clippedRegion])
        delete_layers([tempAreaPath])
        delete_layers([tempNetworkPath])

    for field, dataList in zip(fieldList, dataListList):
        update_huc(field, clipLocation, dataList)

    print "\n"
    layerPathList = make_layers(clipLocation, symbologyList, layerNameList, outputFolder)
    package_layers(layerPathList, outputFolder)
    delete_layers(layerPathList)
    delete_layers([clipLocation])

    print "\nDone with HUC8s!"


def create_huc8_layers_old(outputFolder, fieldList, functionList, symbologyList, layerNameList, huc_shp):

    fieldList = add_fields(fieldList, huc_shp)
    # Create a list containing all HUC8 names from the shapefile
    huc8s_list = [row[0] for row in arcpy.da.SearchCursor(huc_shp, 'HUC8')]

    # Progress Counter
    totalWatersheds = len(huc8s_list)
    finishedWatersheds = 0

    # Initialize lists to hold data later
    dataListList = [[] for i in range(len(functionList))]
    layerPathList = []

    # Sort the abbreviations list (This is necessary for it to function correctly
    abListSorted = sort_abbreviations(ab_list)

    for watershedCounter, huc8 in enumerate(
            huc8s_list):  # This loop calculates data for each individual watershed, or prints a warning

        # Compress HUC8 name
        huc8_shp = arcpy.Select_analysis(huc_shp, 'in_memory/huc8_' + str(huc8), "HUC8 = '%s'" % str(huc8))
        huc8_name = str(arcpy.da.SearchCursor(huc8_shp, ['NAME']).next()[0])
        huc8_name_new = re.sub(r'/W+', '', huc8_name)
        huc8_name_clean = clean_huc_name(huc8_name_new, abListSorted)
        huc8_folder = clean_filepath(os.path.join(pf_path, huc8_name_clean + '_' + str(huc8)))

        print '\n\nCalculating values for ' + remove_prefix(huc8_folder, pf_path + "\\") + " (" + str(
            watershedCounter + 1) + "/" + str(totalWatersheds) + ')',

        if os.path.exists(huc8_folder):  # Looks to see if there is a HUC8 folder for the current watershed

            try:
                data_cap_valid = os.path.join(huc8_folder, 'BRAT', run_folder,
                                              r'Outputs\Output_01\02_Analyses\Data_Capture_Validation.shp')

                if os.path.exists(
                        data_cap_valid):  # Looks to see if the current watershed has a Data Capture Validation File

                    # Select only the perennial data from Data Capture Validation
                    peren_data_cap_valid = arcpy.MakeFeatureLayer_management(data_cap_valid, 'tmp_peren_data_cap_valid')
                    arcpy.SelectLayerByAttribute_management(peren_data_cap_valid, "NEW_SELECTION", """ "IsPeren" = 1 """)

                    # For this watershed, run every summary function and put the data into the corresponding list. This is where the bulk of work is done.
                    for dataList, function in zip(dataListList, functionList):
                        dataList.append(function(peren_data_cap_valid))
                        print ".",

                    finishedWatersheds += 1

                else:  # If finding data is impossible, fill the corresponding list with "-1" for NoData, then print a warning

                    add_no_data(dataListList)
                    print '\nWARNING: Skipping ' + remove_prefix(huc8_folder, pf_path + "\\") + ' - No shapefile found',

            except Exception as err:  # If finding data is impossible, fill the corresponding list with "-1" for NoData, then print a warning

                add_no_data(dataListList)
                print '\nFailed for ' + huc8_folder + '. Error thrown was:',
                print err

        else:  # If finding data is impossible, fill the corresponding list with "-1" for NoData, then print a warning

            add_no_data(dataListList)
            print '\nWARNING: Skipping ' + remove_prefix(huc8_folder, pf_path + "\\") + ' - No folder found',

        watershedCounter += 1

    # Fill in all fields of the huc_shp
    for field, dataList in zip(fieldList, dataListList):
        update_huc(field, huc_shp, dataList)

    # Create a list of the filepaths to every layer
    print "\n"
    layerPathList = make_layers(huc_shp, symbologyList, layerNameList, outputFolder)

    # Create the layer package
    package_layers(layerPathList, outputFolder)

    # Delete layers
    delete_layers(layerPathList)

    print "\n\n\nCompleted! " + str(finishedWatersheds) + " out of " + str(
        totalWatersheds) + " Watersheds successfully summarized."


def calculate_existing_capacity(lyr):  # Calculates median existing capacity for a single watershed

    # Initialize Variables
    medianValue = 0
    dataList = []
    field = 'oCC_EX'

    # Retrieve Data
    if check_field(lyr, field):
        with arcpy.da.SearchCursor(lyr, field) as cursor:
            for capacity in cursor:
                dataList.append(capacity)

        # Calculate the median for this watershed
        medianValue = median(dataList)
        return medianValue
    else:
        missing_field(field)
        return -1


def calculate_historic_capacity(lyr): # Calculates median historic

    # Initialize Variables
    medianValue = 0
    dataList = []
    field = 'oCC_HPE'

    # Retrieve Data
    if check_field(lyr, field):
        with arcpy.da.SearchCursor(lyr, field) as cursor:
            for capacity in cursor:
                dataList.append(capacity)

        # Calculate the median for this watershed
        medianValue = median(dataList)
        return medianValue
    else:
        missing_field(field)
        return -1


def calculate_low_hanging_fruit(lyr):  # Calculates % low hanging fruit for a single watershed

    # Initialize Variables
    easiestLength = 0.0
    percentEasiest = 0.0
    totalLength = 0.0
    field = 'oPBRC_CR'

    # Retrieve Data
    if check_field(lyr, field):
        with arcpy.da.SearchCursor(lyr, ['SHAPE@Length', field]) as cursor:
            for length, category in cursor:
                totalLength += length
                if category == "Easiest - Low-Hanging Fruit":
                    easiestLength += length
                else:
                    pass

        # Calculate the percent labeled "Low Hanging Fruit" this watershed
        percentEasiest = (easiestLength / totalLength) * 100

        return percentEasiest
    else:
        missing_field(field)
        return -1


def calculate_building_possible(lyr):  # Calculates %of watershed where dam building is possible

    # Initialize Variables
    possibleLength = 0.0
    percentPossible = 0.0
    totalLength = 0.0
    field = 'oPBRC_UD'

    # Retrieve Data
    if check_field(lyr, field):
        with arcpy.da.SearchCursor(lyr, ['SHAPE@Length', 'oPBRC_UD']) as cursor:
            for length, category in cursor:
                totalLength += length
                if category == "Dam Building Possible":
                    possibleLength += length
                else:
                    pass
        # Calculate the percent where dam building is possible
        percentPossible = (possibleLength / totalLength) * 100

        return percentPossible
    else:
        missing_field(field)
        return -1


def calculate_capacity_remaining(lyr):
    # Initialize Variables
    medianValue = 0
    dataList = []
    field = 'mCC_EXvHPE'

    # Retrieve Data
    if check_field(lyr, field):
        with arcpy.da.SearchCursor(lyr, field) as cursor:
            for remaining in cursor:
                dataList.append(remaining)

        # Calculate the median for this watershed
        medianValue = median(dataList) * 100
        return medianValue
    else:
        missing_field(field)
        return -1


def calculate_beaver_conservation(lyr):
    # Initialize Variables
    beaverLength = 0.0
    percentBeaver = 0.0
    totalLength = 0.0
    field = 'ConsVRest'

    # Retrieve Data
    if check_field(lyr, field):
        with arcpy.da.SearchCursor(lyr, ['SHAPE@Length', field]) as cursor:
            for length, category in cursor:
                totalLength += length
                if category == "Immediate - Beaver Conservation":
                    beaverLength += length
                else:
                    pass

        percentBeaver = (beaverLength / totalLength) * 100

        return percentBeaver
    else:
        missing_field(field)
        return -1


def calculate_potential_translocation(lyr):
    # Initialize Variables
    potentialLength = 0.0
    percentPotential = 0.0
    totalLength = 0.0
    field = 'ConsVRest'

    # Retrieve Data
    if check_field(lyr, field):
        with arcpy.da.SearchCursor(lyr, ['SHAPE@Length', field]) as cursor:
            for length, category in cursor:
                totalLength += length
                if category == "Immediate - Potential Beaver Translocation":
                    potentialLength += length
                else:
                    pass

        percentPotential = (potentialLength / totalLength) * 100

        return percentPotential
    else:
        return -1


def calculate_considerable_risk(lyr):
    # Initialize Variables
    potentialLength = 0.0
    percentPotential = 0.0
    totalLength = 0.0
    field = 'oPBRC_UI'

    # Retrieve Data
    if check_field(lyr, field):
        with arcpy.da.SearchCursor(lyr, ['SHAPE@Length', field]) as cursor:
            for length, category in cursor:
                totalLength += length
                if category == "Considerable Risk":
                    potentialLength += length
                else:
                    pass

        percentPotential = (potentialLength / totalLength) * 100

        return percentPotential
    else:
        return -1


def update_huc(field, huc_shp, array):  # Updates a specific field of the main huc_shp from an array of values

    # Update the huc_shp with data from the array
    with arcpy.da.UpdateCursor(huc_shp, field) as cursor:
        for counter, row in enumerate(cursor):
            row[0] = array[counter]
            cursor.updateRow(row)


def make_layers(huc_shp, symbologyList, nameList, outputFolder):
    # Creates all necessary layers, given a list of symbology filepaths and names for the files

    # Initialize Variables
    layerPathList = []

    # Create every layer
    for symbology, name in zip(symbologyList, nameList):
        print "\nCreating Layer: " + name + "...\n"
        # Make a new layer with a name from the nameList
        newLayer = arcpy.MakeFeatureLayer_management(huc_shp, name)
        # Apply appropriate symbology from the symbology List
        arcpy.ApplySymbologyFromLayer_management(newLayer, symbology)
        # Create a filepath to save the layer
        filePath = clean_filepath(os.path.join(outputFolder, (name + "_Summary.lyr")))
        # Check to see if the layer we are looking at is the reference labels file, as that has special considerations
        if symbology == os.path.join(symbology_folder, "Summary_Labels.lyr"):
            temp = symbolize_labels(newLayer, filePath, symbology, outputFolder)
            newLayer = temp
        # Save the layer
        arcpy.SaveToLayerFile_management(newLayer, filePath)
        # Add this filepath to a list. This will be used to create the layer package
        layerPathList.append(filePath)

    return layerPathList


def symbolize_labels(newLayer, filePath, symbology, outputFolder):
    # Adds proper symbology to the reference labels shapefile.
    # Because labels aren't technically 'symbology', more work has to be done to transfer them over.
    # Code partially adapted from Ian Broad. http://ianbroad.com/download/script/UpdateLayerProperties.py

    # Save the layer file so it is accessible later
    arcpy.SaveToLayerFile_management(newLayer, filePath)

    # Initialize the map document and data frame
    mxd = arcpy.mapping.MapDocument(os.path.join(symbology_folder, "Summary_Labels.mxd"))
    df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

    # Add the current data to the new map
    newLayer = arcpy.mapping.Layer(filePath)
    arcpy.mapping.AddLayer(df, newLayer, "BOTTOM")

    # Save all necessary data about the current layers so it can be restored later
    layer_file_object = arcpy.mapping.Layer(symbology)
    original_fc_name = str(layer_file_object.name)
    input_layer_object = arcpy.mapping.ListLayers(mxd, newLayer)[0]
    input_fc_name = str(input_layer_object.datasetName)
    input_fc_toc_name = str(input_layer_object.name)
    input_fc_workspace = str(input_layer_object.workspacePath)

    # Set the new worspace type based off of the workspace ID
    workspace_id = str(arcpy.Describe(input_fc_workspace).workspaceFactoryProgID)
    if workspace_id == "esriDataSourcesGDB.AccessWorkspaceFactory.1":
        workspace_type = "ACCESS_WORKSPACE"
    elif workspace_id == "esriDataSourcesGDB.FileGDBWorkspaceFactory.1":
        workspace_type = "FILEGDB_WORKSPACE"
    elif workspace_id == "esriDataSourcesGDB.SdeWorkspaceFactory.1":
        workspace_type = "SDE_WORKSPACE"
    else:
        workspace_type = "SHAPEFILE_WORKSPACE"

    # Update the layer to hold necessary labels and symbology

    arcpy.mapping.UpdateLayer(df, input_layer_object, layer_file_object, False)
    refocus_layer = arcpy.mapping.ListLayers(mxd, original_fc_name)[0]
    refocus_layer.replaceDataSource(input_fc_workspace, workspace_type, input_fc_name)
    refocus_layer.name = input_fc_toc_name
    arcpy.RefreshTOC()

    # Create an image file of the area for reference
    arcpy.Delete_management(arcpy.mapping.ListLayers(mxd, "", df)[0])
    ext = input_layer_object.getExtent()
    df.extent = ext
    arcpy.mapping.ExportToJPEG(mxd, os.path.join(outputFolder, "ReferenceMap.jpeg"), df, 5000, 5000, 150)

    # Return the new layer, that now has correct labels and symbology
    return input_layer_object


def package_layers(layerPathList, outputFolder):
    # Packages all of the layers together into a single layer package
    arcpy.PackageLayer_management(layerPathList, os.path.join(outputFolder, "SummaryLayers.lpk"))


def delete_layers(layerPathList):  # Deletes all layer files, leaving only the layer package
    for layer in layerPathList:
        arcpy.Delete_management(layer)


if __name__ == "__main__":
    main()
