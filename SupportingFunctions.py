# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Name: Supporting Functions
# Purpose: A series of useful functions, placed in one spot so they're easier to bug fix
#
# Author: Braden Anderson
# Created on: 7 September 2018
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


import os
import arcpy


def findFolder(folderLocation, folderName):
    """
    If the folder exists, returns it. Otherwise, raises an error
    :param folderLocation: Where to look
    :param folderName: The folder to look for
    :return: Path to folder
    """
    folders = os.listdir(folderLocation)
    for folder in folders:
        if folder.endswith(folderName):
            return os.path.join(folderLocation, folder)

    return None


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


def makeLayer(output_folder, layer_base, new_layer_name, symbology_layer=None, isRaster=False, description="Made Up Description", fileName=None, symbology_field=None):
    """
    Creates a layer and applies a symbology to it
    :param output_folder: Where we want to put the layer
    :param layer_base: What we should base the layer off of
    :param new_layer_name: What the layer should be called
    :param symbology_layer: The symbology that we will import
    :param isRaster: Tells us if it's a raster or not
    :param description: The discription to give to the layer file
    :return: The path to the new layer
    """
    new_layer = new_layer_name
    if fileName is None:
        fileName = new_layer_name.replace(' ', '')
    new_layer_save = os.path.join(output_folder, fileName)
    if not new_layer_save.endswith(".lyr"):
        new_layer_save += ".lyr"

    if isRaster:
        try:
            arcpy.MakeRasterLayer_management(layer_base, new_layer)
        except arcpy.ExecuteError as err:
            if err[0][6:12] == "000873":
                arcpy.AddError(err)
                arcpy.AddMessage("The error above can often be fixed by removing layers or layer packages from the Table of Contents in ArcGIS.")
                raise Exception
            else:
                raise arcpy.ExecuteError(err)

    else:
        arcpy.MakeFeatureLayer_management(layer_base, new_layer)

    if symbology_layer:
        arcpy.ApplySymbologyFromLayer_management(new_layer, symbology_layer)

    if not os.path.exists(new_layer_save):
        arcpy.SaveToLayerFile_management(new_layer, new_layer_save, "RELATIVE")
        new_layer_instance = arcpy.mapping.Layer(new_layer_save)
        new_layer_instance.description = description
        if symbology_field:
            new_layer_instance.symbology.valueField = symbology_field
        new_layer_instance.save()
    return new_layer_save