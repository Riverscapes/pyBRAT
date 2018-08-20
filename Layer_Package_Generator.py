

import arcpy
import os

def main(output_folder, layer_package_name):
    makeLayerPackage(output_folder, layer_package_name)


def makeLayerPackage(outputFolder, layerPackageName):
    """
    Makes a layer package for the project
    :param outputFolder: The folder that we want to base our layer package off of
    :param layerPackageName: The name of the layer package that we'll make
    :return:
    """
    if layerPackageName == "" or layerPackageName==None:
        layerPackageName = "LayerPackage"
    if not layerPackageName.endswith(".lpk"):
        layerPackageName += ".lpk"

    arcpy.AddMessage("Making Layer Package...")
    intermediatesFolder = os.path.join(outputFolder, "01_Intermediates")
    analysesFolder = os.path.join(outputFolder, "02_Analyses")
    projectFolder = os.path.dirname(outputFolder)
    inputsFolder = findFolder(projectFolder, "Inputs")

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')
    emptyGroupLayer = os.path.join(symbologyFolder, "EmptyGroupLayer.lyr")

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]

    outputLayers = findLayersInFolder(analysesFolder)

    inputsLayer = getInputsLayer(emptyGroupLayer, inputsFolder, df, mxd)
    BRATLayer = groupLayers(emptyGroupLayer, "Beaver Restoration Assessment Tool - BRAT", outputLayers, df, mxd)
    intermediatesLayer = getIntermediatesLayers(emptyGroupLayer, intermediatesFolder, df, mxd)
    outputLayer = groupLayers(emptyGroupLayer, "Output", [intermediatesLayer, BRATLayer], df, mxd)
    outputLayer = groupLayers(emptyGroupLayer, layerPackageName[:-4], [outputLayer, inputsLayer], df, mxd, removeLayer=False)

    layerPackage = os.path.join(outputFolder, layerPackageName)
    arcpy.PackageLayer_management(outputLayer, layerPackage)



def getInputsLayer(emptyGroupLayer, inputsFolder, df, mxd):
    """
    Gets all the input layers, groups them properly, returns the layer
    :param emptyGroupLayer: The base to build the group layer with
    :param inputsFolder: Path to the inputs folder
    :param df: The dataframe we're working with
    :param mxd: The map document we're working with
    :return: layer for inputs
    """
    vegetationFolder = findFolder(inputsFolder, "_Vegetation")
    exVegFolder = findFolder(vegetationFolder, "_ExistingVegetation")
    histVegFolder = findFolder(vegetationFolder, "_HistoricVegetation")

    networkFolder = findFolder(inputsFolder, "_Network")

    topoFolder = findFolder(inputsFolder, "_Topography")

    conflictFolder = findFolder(inputsFolder, "_Conflict")
    valleyFolder = findFolder(conflictFolder, "_ValleyBottom")
    roadsFolder = findFolder(conflictFolder, "_Roads")
    railroadsFolder = findFolder(conflictFolder, "_Railroads")
    canalsFolder = findFolder(conflictFolder, "_Canals")
    landUseFolder = findFolder(conflictFolder, "_LandUse")

    exVegLayers = findInstanceLayers(exVegFolder)
    exVegLayer = groupLayers(emptyGroupLayer, "Existing Vegetation Dam Capacity", exVegLayers, df, mxd)
    histVegLayers = findInstanceLayers(histVegFolder)
    histVegLayer = groupLayers(emptyGroupLayer, "Historic Vegetation Dam Capacity", histVegLayers, df, mxd)
    vegLayer = groupLayers(emptyGroupLayer, "Vegetation", [exVegLayer, histVegLayer], df, mxd)

    networkLayers = findInstanceLayers(networkFolder)
    networkLayer = groupLayers(emptyGroupLayer, "Network", networkLayers, df, mxd)

    demLayers = findInstanceLayers(topoFolder)
    hillshadeLayers = find_dem_derivative(topoFolder, "Hillshade")
    slopeLayers = find_dem_derivative(topoFolder, "Slope")
    flowLayers = find_dem_derivative(topoFolder, "Flow")
    topoLayer = groupLayers(emptyGroupLayer, "Topography", hillshadeLayers + demLayers + slopeLayers + flowLayers, df, mxd)

    valleyLayers = findInstanceLayers(valleyFolder)
    valleyLayer = groupLayers(emptyGroupLayer, "Valley Bottom", valleyLayers, df, mxd)
    roadLayers = findInstanceLayers(roadsFolder)
    roadLayer = groupLayers(emptyGroupLayer, "Roads", roadLayers, df, mxd)
    railroadLayers = findInstanceLayers(railroadsFolder)
    railroadLayer = groupLayers(emptyGroupLayer, "Railroads", railroadLayers, df, mxd)
    canalLayers = findInstanceLayers(canalsFolder)
    canalLayer = groupLayers(emptyGroupLayer, "Canals", canalLayers, df, mxd)
    landUseLayers = findInstanceLayers(landUseFolder)
    landUseLayer = groupLayers(emptyGroupLayer, "Land Use", landUseLayers, df, mxd)
    conflictLayer = groupLayers(emptyGroupLayer, "Conflict Layers", [valleyLayer, roadLayer, railroadLayer, canalLayer, landUseLayer], df, mxd)

    return groupLayers(emptyGroupLayer, "Inputs", [vegLayer, networkLayer, topoLayer, conflictLayer], df, mxd)


def getIntermediatesLayers(emptyGroupLayer, intermediatesFolder, df, mxd):
    """
    Returns a group layer with all of the intermediates
    :param emptyGroupLayer: The base to build the group layer with
    :param intermediatesFolder: Path to the intermediates folder
    :param df: The dataframe we're working with
    :param mxd: The map document we're working with
    :return: Layer for intermediates
    """
    intermediate_layers = []

    findAndGroupLayers(intermediate_layers, intermediatesFolder, "Buffers", "Buffers", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "LandUse", "Land Use Intensity", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "TopographicIndex", "Topographic Index", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "BraidHandler", "Braid Handler", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "Hydrology", "Hydrology", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "VegDamCapacity", "Overall Vegetation Dam Capacity", emptyGroupLayer, df, mxd)

    veg_folder_name = "VegDamCapacity"
    veg_group_layer_name = "Overall Vegetation Dam Capacity"
    veg_folder_path = findFolder(intermediatesFolder, veg_folder_name)
    if veg_folder_path:
        veg_layers = findLayersInFolder(veg_folder_path)
        if len(veg_layers) == 2:
            desc = arcpy.Describe(veg_layers[0])
            if "Existing" in desc.nameString:
                veg_layers = [veg_layers[1], veg_layers[0]]

        intermediate_layers.append(groupLayers(emptyGroupLayer, veg_group_layer_name, veg_layers, df, mxd))

    return groupLayers(emptyGroupLayer, "Intermediates", intermediate_layers, df, mxd)


def findAndGroupLayers(layers_list, folderBase, folderName, groupLayerName, emptyGroupLayer, df, mxd):
    """
    Looks for the folder that matches what we're looking for, then groups them together. Adds that grouped layer to the
    list of grouped layers that it was given
    :param layers_list: The list of layers that we will add our grouped layer to
    :param folderBase: Path to the folder that contains the folder we want
    :param folderName: The name of the folder to look in
    :param groupLayerName: What we want to name the group layer
    :param emptyGroupLayer: The base to build the group layer with
    :param df: The dataframe we're working with
    :param mxd: The map document we're working with
    :return:
    """
    folderPath = findFolder(folderBase, folderName)
    if folderPath:
        layers = findLayersInFolder(folderPath)

        layers_list.append(groupLayers(emptyGroupLayer, groupLayerName, layers, df, mxd))


def findInstanceLayers(root_folder):
    """
    Finds every layer when buried beneath an additional layer of folders (ie, in DEM_1, DEM_2, DEM_3, etc)
    :param root_folder: The path to the folder root
    :return: A list of layers
    """
    layers = []
    for instance_folder in os.listdir(root_folder):
        instance_folder_path = os.path.join(root_folder, instance_folder)
        layers += findLayersInFolder(instance_folder_path)
    return layers


def find_dem_derivative(root_folder, dir_name):
    """
    Designed to look specifically for flow, slope, and hillshade layers
    :param root_folder: Where we look
    :param dir_name: The directory we're looking for
    :return:
    """
    layers = []
    for instance_folder in os.listdir(root_folder):
        instance_folder_path = os.path.join(os.path.join(root_folder, instance_folder), dir_name)
        layers += findLayersInFolder(instance_folder_path)
    return layers


def findLayersInFolder(folder_root):
    """
    Returns a list of all layers in a folder
    :param folder_root: Where we want to look
    :return:
    """
    layers = []
    for instance_file in os.listdir(folder_root):
        if instance_file.endswith(".lyr"):
            layers.append(os.path.join(folder_root, instance_file))
    return layers


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

    arcpy.AddMessage(folderName + " layer was not found, and so will not be in the layer package")
    return None


def groupLayers(groupLayer, groupName, layers, df, mxd, removeLayer=True):
    """
    Groups a bunch of layers together
    :param groupLayer:
    :param groupName:
    :param layers:
    :param df:
    :param mxd:
    :param removeLayer: Tells us if we should remove the layer from the map display
    :return: The layer that we put our layers in
    """
    groupLayer = arcpy.mapping.Layer(groupLayer)
    groupLayer.name = groupName
    groupLayer.description = "Made Up Description"
    arcpy.mapping.AddLayer(df, groupLayer, "BOTTOM")
    groupLayer = arcpy.mapping.ListLayers(mxd, groupName, df)[0]

    for layer in layers:
        if not isinstance(layer, arcpy.mapping.Layer):
            layer_instance = arcpy.mapping.Layer(layer)
        else:
            layer_instance = layer
        arcpy.mapping.AddLayerToGroup(df, groupLayer, layer_instance)

    if removeLayer:
        arcpy.mapping.RemoveLayer(df, groupLayer)

    return groupLayer

