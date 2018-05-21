# -------------------------------------------------------------------------------
# Name:        iHYD
# Purpose:     Adds the hydrologic attributes to the BRAT input table
#
# Author:      Jordan
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
import numpy as np
import os
import sys


def main(
    in_network,
    region):

    scratch = 'in_memory'

    arcpy.env.overwriteOutput = True

    # create segid array for joining output to input network
    segid_np = arcpy.da.FeatureClassToNumPyArray(in_network, "ReachID")
    segid = np.asarray(segid_np, np.int64)

    # create array for input network drainage area ("iGeo_DA")
    DA_array = arcpy.da.FeatureClassToNumPyArray(in_network, "iGeo_DA")
    DA = np.asarray(DA_array, np.float32)

    # convert drainage area (in square kilometers) to square miles
    # note: this assumes that streamflow equations are in US customary units (e.g., inches, feet)
    DAsqm = np.zeros_like(DA)
    DAsqm = DA * 0.3861021585424458

    # create Qlow and Q2
    Qlow = np.zeros_like(DA)
    Q2 = np.zeros_like(DA)

    arcpy.AddMessage("Adding Qlow and Q2 to network...")

    if region is None:
        region = 0

    # --regional curve equations for Qlow (baseflow) and Q2 (annual peak streamflow)--
    # # # Add in regional curve equations here # # #
    if float(region) == 101:  # example 1 (box elder county)
        Qlow = 0.019875 * (DAsqm ** 0.6634) * (10 ** (0.6068 * 2.04))
        Q2 = 14.5 * DAsqm ** 0.328

    elif float(region) == 102:  # example 2 (upper green generic)
        Qlow = 4.2758 * (DAsqm ** 0.299)
        Q2 = 22.2 * (DAsqm ** 0.608) * ((42 - 40) ** 0.1)

    elif float(region) == 24:  # oregon region 5
        Qlow = 0.000133 * (DAsqm ** 1.05) * (15.3 ** 2.1)
        Q2 = 0.000258 * (DAsqm ** 0.893) * (15.3 ** 3.15)

    else:
        Qlow = (DAsqm ** 0.2098) + 1
        Q2 = 14.7 * (DAsqm ** 0.815)

    # save segid, Qlow, Q2 as single table
    columns = np.column_stack((segid, Qlow, Q2))
    tmp_table = os.path.dirname(in_network) + "/ihyd_Q_Table.txt"
    np.savetxt(tmp_table, columns, delimiter = ",", header = "ReachID, iHyd_QLow, iHyd_Q2", comments = "")
    ihyd_table = scratch + "/ihyd_table"
    arcpy.CopyRows_management(tmp_table, ihyd_table)

    # join Qlow and Q2 output to the flowline network
    # create empty dictionary to hold input table field values
    tblDict = {}
    # add values to dictionary
    with arcpy.da.SearchCursor(ihyd_table, ['ReachID', "iHyd_QLow", "iHyd_Q2"]) as cursor:
        for row in cursor:
            tblDict[row[0]] = [row[1], row[2]]
    # populate flowline network out field
    arcpy.AddField_management(in_network, "iHyd_QLow", 'DOUBLE')
    arcpy.AddField_management(in_network, "iHyd_Q2", 'DOUBLE')
    with arcpy.da.UpdateCursor(in_network, ['ReachID', "iHyd_QLow", "iHyd_Q2"]) as cursor:
        for row in cursor:
            try:
                aKey = row[0]
                row[1] = tblDict[aKey][0]
                row[2] = tblDict[aKey][1]
                cursor.updateRow(row)
            except:
                pass
    tblDict.clear()

    # delete temporary table
    arcpy.Delete_management(tmp_table)

    # check that Q2 is greater than Qlow
    # if not, re-calculate Q2 as Qlow + 0.001
    with arcpy.da.UpdateCursor(in_network, ["iHyd_QLow", "iHyd_Q2"]) as cursor:
        for row in cursor:
            if row[1] < row[0]:
                row[1] = row[0] + 0.001
            else:
                pass
            cursor.updateRow(row)

    arcpy.AddMessage("Adding stream power to network...")

    # calculate Qlow and Q2 stream power
    # where stream power = density of water (1000 kg/m3) * acceleration due to gravity (9.80665 m/s2) * discharge (m3/s) * channel slope
    # note: we assume that discharge ("iHyd_QLow", "iHyd_Q2") was calculated in cubic feet per second and handle conversion to cubic
    #       meters per second (e.g., "iHyd_QLow" * 0.028316846592
    arcpy.AddField_management(in_network, "iHyd_SPLow", "DOUBLE")
    arcpy.AddField_management(in_network, "iHyd_SP2", "DOUBLE")
    with arcpy.da.UpdateCursor(in_network, ["iGeo_Slope", "iHyd_QLow", "iHyd_SPLow", "iHyd_Q2", "iHyd_SP2"]) as cursor:
        for row in cursor:
            row[2] = (1000 * 9.80665) * row[0] * (row[1] * 0.028316846592)
            row[4] = (1000 * 9.80665) * row[0] * (row[3] * 0.028316846592)
            cursor.updateRow(row)


def makeLayers(inputNetwork):
    """
    Makes the layers for the modified output
    :param inputNetwork: The path to the network that we'll make a layer from
    :return:
    """
    arcpy.AddMessage("Making layers...")
    intermediates_folder = os.path.dirname(inputNetwork)
    braid_folder_name = findAvailableNum(intermediates_folder) + "_BraidHandler"
    braid_folder = makeFolder(intermediates_folder, braid_folder_name)


    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')

    mainstemSymbology = os.path.join(symbologyFolder, "Mainstems.lyr")

    makeLayer(braid_folder, inputNetwork, "Mainstem_Braids", mainstemSymbology, isRaster=False)



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
    main(
        sys.argv[1],
        sys.argv[2])
