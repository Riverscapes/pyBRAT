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
    arcpy.env.workspace = projPath

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

    sourceCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(sourceCodeFolder, 'BRATSymbology')
    exVegSymbology = os.path.join(symbologyFolder, "Ex_Veg_Raster.lyr")
    histVegSymbology = os.path.join(symbologyFolder, "Hist_Veg_Raster.lyr")
    networkSymbology = os.path.join(symbologyFolder, "Network.lyr")
    landuseSymbology = os.path.join(symbologyFolder, "Land_Use_Raster.lyr")
    canalsSymbology = os.path.join(symbologyFolder, "Canals.lyr")
    roadsSymbology = os.path.join(symbologyFolder, "Roads.lyr")
    railroadsSymbology = os.path.join(symbologyFolder, "Railroads.lyr")
    valleyBottomSymbology = os.path.join(symbologyFolder, "ValleyBottom.lyr")

    # add the existing veg inputs to project
    exVegDestinations = copyMultiInputToFolder(exVegFolder, ex_veg, "Ex_Veg", isRaster=True)
    makeInputLayers(exVegDestinations, "Existing_Vegetation", symbologyLayer=None, isRaster=True)

    # add the historic veg inputs to project
    histVegDestinations = copyMultiInputToFolder(histVegFolder, hist_veg, "Hist_Veg", isRaster=True)
    makeInputLayers(histVegDestinations, "Historic_Vegetation", symbologyLayer=None, isRaster=True)

    # add the network inputs to project
    networkDestinations = copyMultiInputToFolder(networkFolder, network, "Network", isRaster=False)
    makeInputLayers(networkDestinations, "Network", symbologyLayer=networkSymbology, isRaster=False)

    # add the DEM inputs to the project
    copyMultiInputToFolder(topoFolder, DEM, "DEM", isRaster=True)
    makeTopoLayers(topoFolder)

    # add landuse raster to the project
    if landuse is not None:
        landuseDestinations = copyMultiInputToFolder(landUseFolder, landuse, "Land_Use", isRaster=True)
        makeInputLayers(landuseDestinations, "Land_Use_Raster", symbologyLayer=landuseSymbology, isRaster=True)

    # add the conflict inputs to the project
    if valley is not None:
        vallyBottomDestinations = copyMultiInputToFolder(valleyBottomFolder, valley, "Valley", isRaster=False)
        makeInputLayers(vallyBottomDestinations, "Valley_Bottom", symbologyLayer=valleyBottomSymbology, isRaster=False)

    # add road layers to the project
    if road is not None:
        roadDestinations = copyMultiInputToFolder(roadFolder, road, "Roads", isRaster=False)
        makeInputLayers(roadDestinations, "Roads", symbologyLayer=roadsSymbology, isRaster=False)

    # add railroad layers to the project
    if rr is not None:
        rrDestinations = copyMultiInputToFolder(railroadFolder, rr, "Railroads", isRaster=False)
        makeInputLayers(rrDestinations, "Railroads", symbologyLayer=railroadsSymbology, isRaster=False)

    # add canal layers to the project
    if canal is not None:
        canalDestinations = copyMultiInputToFolder(canalsFolder, canal, "Canals", isRaster=False)
        makeInputLayers(canalDestinations, "Canals", symbologyLayer=canalsSymbology, isRaster=False)


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
    destinations = []
    for inputPath in splitInput:
        newSubFolder = makeFolder(folderPath, subFolderName + "_" + str(i))
        destinationPath = os.path.join(newSubFolder, os.path.basename(inputPath))

        if isRaster:
            arcpy.CopyRaster_management(inputPath, destinationPath)
        else:
            arcpy.Copy_management(inputPath, destinationPath)
        destinations.append(destinationPath)
        i += 1
    return destinations


def makeTopoLayers(topoFolder):
    """
    Writes the layers
    :param topoFolder: We want to make layers for the stuff in this folder
    :return:
    """
    sourceCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(sourceCodeFolder, 'BRATSymbology')
    demSymbology = os.path.join(symbologyFolder, "DEM.lyr")
    slopeSymbology = os.path.join(symbologyFolder, "Slope.lyr")
    layers = []

    for folder in os.listdir(topoFolder):
        demFolderPath = os.path.join(topoFolder, folder)
        demFile = None
        for fileName in os.listdir(demFolderPath):
            if fileName.endswith(".tif"):
                demFile = os.path.join(demFolderPath, fileName)
                layers.append(makeLayer(demFolderPath, demFile, os.path.basename(demFile), demSymbology, isRaster=True))

        hillshadeFolder = makeFolder(demFolderPath, "Hillshade")
        hillshadeFile = os.path.join(hillshadeFolder, "Hillshade.tif")
        arcpy.HillShade_3d(demFile, hillshadeFile)
        makeLayer(hillshadeFolder, hillshadeFile, "Hillshade", isRaster=True)

        slopeFolder = makeFolder(demFolderPath, "Slope")
        slopeFile = os.path.join(slopeFolder, "Slope.tif")
        outSlope = arcpy.sa.Slope(demFile)
        outSlope.save(slopeFile)
        makeLayer(slopeFolder, slopeFile, "Slope", slopeSymbology, isRaster=True)


def makeLayer(output_folder, layer_base, new_layer_name, symbology_layer=None, isRaster=False, description="Made Up Description"):
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
    new_layer = new_layer_name + "_lyr"
    new_layer_save = os.path.join(output_folder, new_layer_name + ".lyr")

    if isRaster:
        try:
            arcpy.MakeRasterLayer_management(layer_base, new_layer)
        except arcpy.ExecuteError as err:
            if err[0][6:12] == "000873":
                arcpy.AddError(err)
                arcpy.AddMessage("The error above can often be fixed by removing layers or layer packages from the Table of Contents in ArcGIS.")
                raise Exception

    else:
        arcpy.MakeFeatureLayer_management(layer_base, new_layer)

    if symbology_layer:
        arcpy.ApplySymbologyFromLayer_management(new_layer, symbology_layer)

    arcpy.SaveToLayerFile_management(new_layer, new_layer_save, "RELATIVE")
    new_layer_instance = arcpy.mapping.Layer(new_layer_save)
    new_layer_instance.description = description
    new_layer_instance.save()
    return new_layer_save


def makeInputLayers(destinations, layerName, isRaster, symbologyLayer=None):
    """
    Makes the layers for everything in the folder
    :param destinations: A list of paths to our input
    :param layerName: The name of the layer
    :param isRaster: Whether or not it's a raster
    :param symbologyLayer: The base for the symbology
    :return:
    """
    for destination in destinations:
        destDirName = os.path.dirname(destination)
        makeLayer(destDirName, destination, layerName, symbology_layer=symbologyLayer, isRaster=isRaster)



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
