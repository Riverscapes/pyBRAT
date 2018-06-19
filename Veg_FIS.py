# -------------------------------------------------------------------------------
# Name:        Veg FIS
# Purpose:     Runs the vegetation FIS for the BRAT input table
#
# Author:      Jordan Gilbert
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import os
import sys


def main(in_network):

    scratch = 'in_memory'

    # vegetation capacity fis function
    def vegFIS(model_run):

        arcpy.env.overwriteOutput = True

        # get list of all fields in the flowline network
        fields = [f.name for f in arcpy.ListFields(in_network)]

        # set the carrying capacity and vegetation field depending on whether potential or existing run
        if model_run == 'pt':
            out_field = "oVC_PT"
            riparian_field = "iVeg_100PT"
            streamside_field = "iVeg_30PT"
        else:
            out_field = "oVC_EX"
            riparian_field = "iVeg_100EX"
            streamside_field = "iVeg_30EX"

        # check for oVC_* field in the network attribute table and delete if exists
        if out_field in fields:
            arcpy.DeleteField_management(in_network, out_field)

        # get arrays for fields of interest
        segid_np = arcpy.da.FeatureClassToNumPyArray(in_network, "ReachID")
        riparian_np = arcpy.da.FeatureClassToNumPyArray(in_network, riparian_field)
        streamside_np = arcpy.da.FeatureClassToNumPyArray(in_network, streamside_field)

        segid_array = np.asarray(segid_np, np.int64)
        riparian_array = np.asarray(riparian_np, np.float64)
        streamside_array = np.asarray(streamside_np, np.float64)

        # check that inputs are within range of fis
        # if not, re-assign the value to just within range
        riparian_array[riparian_array < 0] = 0
        riparian_array[riparian_array > 4] = 4
        streamside_array[streamside_array < 0] = 0
        streamside_array[streamside_array > 4] = 4

        # delete temp arrays
        items = [segid_np, riparian_np, streamside_np]
        for item in items:
            del item

        # create antecedent (input) and consequent (output) objects to hold universe variables and membership functions
        riparian = ctrl.Antecedent(np.arange(0, 4, 0.01), 'input1')
        streamside = ctrl.Antecedent(np.arange(0, 4, 0.01), 'input2')
        density = ctrl.Consequent(np.arange(0, 45, 0.01), 'result')

        # build membership functions for each antecedent and consequent object
        riparian['unsuitable'] = fuzz.trapmf(riparian.universe, [0, 0, 0.1, 1])
        riparian['barely'] = fuzz.trimf(riparian.universe, [0.1, 1, 2])
        riparian['moderately'] = fuzz.trimf(riparian.universe, [1, 2, 3])
        riparian['suitable'] = fuzz.trimf(riparian.universe, [2, 3, 4])
        riparian['preferred'] = fuzz.trimf(riparian.universe, [3, 4, 4])

        streamside['unsuitable'] = fuzz.trapmf(streamside.universe, [0, 0, 0.1, 1])
        streamside['barely'] = fuzz.trimf(streamside.universe, [0.1, 1, 2])
        streamside['moderately'] = fuzz.trimf(streamside.universe, [1, 2, 3])
        streamside['suitable'] = fuzz.trimf(streamside.universe, [2, 3, 4])
        streamside['preferred'] = fuzz.trimf(streamside.universe, [3, 4, 4])

        density['none'] = fuzz.trimf(density.universe, [0, 0, 0.1])
        density['rare'] = fuzz.trapmf(density.universe, [0, 0.1, 0.5, 1.5])
        density['occasional'] = fuzz.trapmf(density.universe, [0.5, 1.5, 4, 8])
        density['frequent'] = fuzz.trapmf(density.universe, [4, 8, 12, 25])
        density['pervasive'] = fuzz.trapmf(density.universe, [12, 25, 45, 45])

        # build fis rule table
        rule1 = ctrl.Rule(riparian['unsuitable'] & streamside['unsuitable'], density['none'])
        rule2 = ctrl.Rule(riparian['barely'] & streamside['unsuitable'], density['rare'])
        rule3 = ctrl.Rule(riparian['moderately'] & streamside['unsuitable'], density['rare'])
        rule4 = ctrl.Rule(riparian['suitable'] & streamside['unsuitable'], density['occasional'])
        rule5 = ctrl.Rule(riparian['preferred'] & streamside['unsuitable'], density['occasional'])
        rule6 = ctrl.Rule(riparian['unsuitable'] & streamside['barely'], density['rare'])
        rule7 = ctrl.Rule(riparian['barely'] & streamside['barely'], density['rare']) # matBRAT has consequnt as 'occasional'
        rule8 = ctrl.Rule(riparian['moderately'] & streamside['barely'], density['occasional'])
        rule9 = ctrl.Rule(riparian['suitable'] & streamside['barely'], density['occasional'])
        rule10 = ctrl.Rule(riparian['preferred'] & streamside['barely'], density['occasional'])
        rule11 = ctrl.Rule(riparian['unsuitable'] & streamside['moderately'], density['rare'])
        rule12 = ctrl.Rule(riparian['barely'] & streamside['moderately'], density['occasional'])
        rule13 = ctrl.Rule(riparian['moderately'] & streamside['moderately'], density['occasional'])
        rule14 = ctrl.Rule(riparian['suitable'] & streamside['moderately'], density['frequent'])
        rule15 = ctrl.Rule(riparian['preferred'] & streamside['moderately'], density['frequent'])
        rule16 = ctrl.Rule(riparian['unsuitable'] & streamside['suitable'], density['occasional'])
        rule17 = ctrl.Rule(riparian['barely'] & streamside['suitable'], density['occasional'])
        rule18 = ctrl.Rule(riparian['moderately'] & streamside['suitable'], density['frequent'])
        rule19 = ctrl.Rule(riparian['suitable'] & streamside['suitable'], density['frequent'])
        rule20 = ctrl.Rule(riparian['preferred'] & streamside['suitable'], density['pervasive'])
        rule21 = ctrl.Rule(riparian['unsuitable'] & streamside['preferred'], density['occasional'])
        rule22 = ctrl.Rule(riparian['barely'] & streamside['preferred'], density['frequent'])
        rule23 = ctrl.Rule(riparian['moderately'] & streamside['preferred'], density['pervasive'])
        rule24 = ctrl.Rule(riparian['suitable'] & streamside['preferred'], density['pervasive'])
        rule25 = ctrl.Rule(riparian['preferred'] & streamside['preferred'], density['pervasive'])

        # FIS
        veg_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11,
                                       rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25])
        veg_fis = ctrl.ControlSystemSimulation(veg_ctrl)

        # run fuzzy inference system on inputs and defuzzify output
        out = np.zeros(len(riparian_array))
        for i in range(len(out)):
            veg_fis.input['input1'] = riparian_array[i]
            veg_fis.input['input2'] = streamside_array[i]
            veg_fis.compute()
            out[i] = veg_fis.output['result']

        # save fuzzy inference system output as table
        columns = np.column_stack((segid_array, out))
        out_table = os.path.dirname(in_network) + "/" + out_field + "_Table.txt"  # todo: see if possible to skip this step
        np.savetxt(out_table, columns, delimiter = ",", header = "ReachID, " + out_field, comments = "")
        ovc_table = scratch + "/" + out_field + "Tbl"
        arcpy.CopyRows_management(out_table, ovc_table)

        # join the fuzzy inference system output to the flowline network
        # create empty dictionary to hold input table field values
        tblDict = {}
        # add values to dictionary
        with arcpy.da.SearchCursor(ovc_table, ['ReachID', out_field]) as cursor:
            for row in cursor:
                tblDict[row[0]] = row[1]
        # populate flowline network out field
        arcpy.AddField_management(in_network, out_field, 'DOUBLE')
        with arcpy.da.UpdateCursor(in_network, ['ReachID', out_field]) as cursor:
            for row in cursor:
                try:
                    aKey = row[0]
                    row[1] = tblDict[aKey]
                    cursor.updateRow(row)
                except:
                    pass
        tblDict.clear()

        # calculate defuzzified centroid value for density 'none' MF group
        # this will be used to re-classify output values that fall in this group
        # important: will need to update the array (x) and MF values (mfx) if the
        #            density 'none' values are changed in the model
        x = np.arange(0, 45, 0.01)
        mfx = fuzz.trimf(x, [0, 0, 0.1])
        defuzz_centroid = round(fuzz.defuzz(x, mfx, 'centroid'), 6)

        # update vegetation capacity (ovc_*) values in stream network
        # set ovc_* to 0 if output falls fully in 'none' category

        with arcpy.da.UpdateCursor(in_network, [out_field]) as cursor:
            for row in cursor:
                if round(row[0], 6) == defuzz_centroid:
                    row[0] = 0.0
                cursor.updateRow(row)

        # delete temporary tables and arrays
        arcpy.Delete_management(out_table)
        arcpy.Delete_management(ovc_table)
        items = [columns, out, x, mfx, defuzz_centroid]
        for item in items:
            del item

    # run the combined fis function for both potential and existing
    vegFIS('pt')
    vegFIS('ex')

    makeLayers(in_network)


def makeLayers(inputNetwork):
    """
    Makes the layers for the modified output
    :param inputNetwork: The path to the network that we'll make a layer from
    :return:
    """
    arcpy.AddMessage("Making layers...")
    intermediates_folder = os.path.dirname(inputNetwork)
    veg_folder_name = findAvailableNum(intermediates_folder) + "_VegCondition"
    veg_folder = makeFolder(intermediates_folder, veg_folder_name)

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')

    existingVegSymbology = os.path.join(symbologyFolder, "Existing_Veg_Capacity.lyr")
    historicVegSymbology = os.path.join(symbologyFolder, "Historic_Veg_Capacity.lyr")

    makeLayer(veg_folder, inputNetwork, "Existing_Veg_Conditions", existingVegSymbology, isRaster=False)
    makeLayer(veg_folder, inputNetwork, "Historic_Veg_Conditions", historicVegSymbology, isRaster=False)



def makeLayer(output_folder, layer_base, new_layer_name, symbology_layer, isRaster, description="Made Up Description"):
    """
    Creates a layer and applies a symbology to it
    :param output_folder: Where we want to put the folder
    :param layer_base: What we should base the layer off of
    :param new_layer_name: What the layer should be called
    :param symbology_layer: The symbology that we will import
    :param isRaster: Tells us if it's a raster or not
    :param description: The discription to give to the layer file
    :return: The path to the new layer
    """
    new_layer = new_layer_name + "_lyr"
    new_layer_save = os.path.join(output_folder, new_layer_name + ".lyr")

    if isRaster:
        arcpy.MakeRasterLayer_management(layer_base, new_layer)
    else:
        arcpy.MakeFeatureLayer_management(layer_base, new_layer)

    arcpy.ApplySymbologyFromLayer_management(new_layer, symbology_layer)
    arcpy.SaveToLayerFile_management(new_layer, new_layer_save)
    new_layer_instance = arcpy.mapping.Layer(new_layer_save)
    new_layer_instance.description = description
    new_layer_instance.save()
    return new_layer_save


def makeFolder(pathToLocation, newFolderName):
    """
    Makes a folder and returns the path to it
    :param pathToLocation: Where we want to put the folder
    :param newFolderName: What the folder will be called
    :return: String
    """
    newFolder = os.path.join(pathToLocation, newFolderName)
    if not os.path.exists(newFolder):
        os.mkdir(newFolder)
    return newFolder


def findAvailableNum(folderRoot):
    """
    Tells us the next number for a folder in the directory given
    :param folderRoot: Where we want to look for a number
    :return: A string, containing a number
    """
    takenNums = [fileName[0:2] for fileName in os.listdir(folderRoot)]
    POSSIBLENUMS = range(1, 100)
    for i in POSSIBLENUMS:
        stringVersion = str(i)
        if i < 10:
            stringVersion = '0' + stringVersion
        if stringVersion not in takenNums:
            return stringVersion
    arcpy.AddWarning("There were too many files at " + folderRoot + " to have another folder that fits our naming convention")
    return "100"


if __name__ == '__main__':
    main(sys.argv[1])
