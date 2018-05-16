# -------------------------------------------------------------------------------
# Name:        BRAT Project Builder
# Purpose:     Gathers and structures the inputs for a BRAT project
#
# Author:      Jordan Gilbert
#
# Created:     09/25/2015
# Latest Update: 02/08/2017
# Copyright:   (c) Jordan Gilbert 2017
# Licence:     This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
#              License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/.
# -------------------------------------------------------------------------------

# import modules
import os
import arcpy
import shutil
import sys
import string


def main(projPath, ex_veg, hist_veg, network, DEM, landuse, valley, road, rr, canal):
    """Create a BRAT project and populate the inputs"""
    arcpy.env.overwriteOutput = True

    if not os.path.exists(projPath):
        os.mkdir(projPath)

    inputsFolder = makeFolder(projPath, "Inputs")

    vegetationFolder = makeFolder(inputsFolder, "01_Vegetation")
    networkFolder = makeFolder(inputsFolder, "02_Network")
    topoFolder = makeFolder(inputsFolder, "03_Topography")
    conflictFolder = makeFolder(inputsFolder, "04_Conflict")

    exVegFolder = makeFolder(vegetationFolder, "01_ExistingVegetation")
    histVegFolder = makeFolder(vegetationFolder, "02_HistoricVegetation")

    valleyBottomFolder = makeFolder(conflictFolder, "01_ValleyBottom")
    roadFolder = makeFolder(conflictFolder, "02_Roads")
    railroadFolder = makeFolder(conflictFolder, "03_Railroads")
    canalsFolder = makeFolder(conflictFolder, "04_Canals")
    landUseFolder = makeFolder(conflictFolder, "05_LandUse")

    # add the existing veg inputs to project
    copyMultiInputToFolder(exVegFolder, ex_veg, "Ex_Veg", isRaster=True)

    # add the historic veg inputs to project
    copyMultiInputToFolder(histVegFolder, hist_veg, "Hist_Veg", isRaster=True)

    # add the network inputs to project
    copyMultiInputToFolder(networkFolder, network, "Network", isRaster=False)

    # add the DEM inputs to the project
    copyMultiInputToFolder(topoFolder, DEM, "DEM", isRaster=True)

    # add landuse raster to the project
    if landuse is not None:
        copyMultiInputToFolder(landUseFolder, landuse, "Land_Use", isRaster=True)

    # add the conflict inputs to the project
    if valley is not None:
        copyMultiInputToFolder(valleyBottomFolder, valley, "Valley", isRaster=False)

    # add road layers to the project
    if road is not None:
        copyMultiInputToFolder(roadFolder, road, "Roads", isRaster=False)

    # add railroad layers to the project
    if rr is not None:
        copyMultiInputToFolder(railroadFolder, rr, "Railroads", isRaster=False)

    # add canal layers to the project
    if canal is not None:
        copyMultiInputToFolder(canalsFolder, canal, "Canals", isRaster=False)


def copyMultiInputToFolder(folderPath, multiInput, subFolderName, isRaster):
    """
    Copies multi input ArcGIS inputs into the folder that we want them in
    :param folderPath: The root folder, where we'll put a bunch of sub folders
    :param multiInput: A string, with paths to the inputs seperated by semicolons
    :param subFolderName: The name for each subfolder (will have a number after it)
    :param isRaster: Tells us if the thing is a raster or not
    :return:
    """
    splitInput = multiInput.split(";")
    i = 1
    for inputPath in splitInput:
        newSubFolder = makeFolder(folderPath, subFolderName + "_" + str(i))
        destinationPath = os.path.join(newSubFolder, os.path.basename(inputPath))

        if isRaster:
            arcpy.CopyRaster_management(inputPath, destinationPath)
        else:
            arcpy.Copy_management(inputPath, destinationPath)
        i += 1


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


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
        sys.argv[8],
        sys.argv[9],
        sys.argv[10])
