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
import sys
from SupportingFunctions import make_folder, make_layer


def main(proj_path, ex_veg, hist_veg, network, DEM, landuse, valley, road, rr, canal, ownership):
    """Create a BRAT project and populate the inputs"""
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = proj_path

    if not os.path.exists(proj_path):
        os.mkdir(proj_path)

    inputs_folder = make_folder(proj_path, "Inputs")

    vegetation_folder = make_folder(inputs_folder, "01_Vegetation")
    network_folder = make_folder(inputs_folder, "02_Network")
    topo_folder = make_folder(inputs_folder, "03_Topography")
    anthropogenic_folder = make_folder(inputs_folder, "04_Anthropogenic")

    ex_veg_folder = make_folder(vegetation_folder, "01_ExistingVegetation")
    hist_veg_folder = make_folder(vegetation_folder, "02_HistoricVegetation")

    valley_bottom_folder = make_folder(anthropogenic_folder, "01_ValleyBottom")
    road_folder = make_folder(anthropogenic_folder, "02_Roads")
    railroad_folder = make_folder(anthropogenic_folder, "03_Railroads")
    canals_folder = make_folder(anthropogenic_folder, "04_Canals")
    land_use_folder = make_folder(anthropogenic_folder, "05_LandUse")
    land_ownership_folder = make_folder(anthropogenic_folder, "06_LandOwnership")

    source_code_folder = os.path.dirname(os.path.abspath(__file__))
    symbology_folder = os.path.join(source_code_folder, 'BRATSymbology')

    # Gets all of our symbology variables set up
    ex_veg_suitability_symbology = os.path.join(symbology_folder, "Existing_Veg_Suitability.lyr")
    ex_veg_riparian_symbology = os.path.join(symbology_folder, "Existing_Veg_Riparian.lyr")
    ex_veg_evt_type_symbology = os.path.join(symbology_folder, "Existing_Veg_EVT_Type.lyr")
    ex_veg_evt_class_symbology = os.path.join(symbology_folder, "Existing_Veg_EVT_Class.lyr")
    ex_veg_class_name_symbology = os.path.join(symbology_folder, "Existing_Veg_ClassName.lyr")

    hist_veg_group_symbology = os.path.join(symbology_folder, "Historic_Veg_BPS_Type.lyr")
    hist_veg_bps_name_symbology = os.path.join(symbology_folder, "Historic_Veg_BPS_Name.lyr")
    hist_veg_suitability_symbology = os.path.join(symbology_folder, "Historic_Veg_Suitability.lyr")
    hist_veg_riparian_symbology = os.path.join(symbology_folder, "Historic_Veg_Riparian.lyr")

    network_symbology = os.path.join(symbology_folder, "Network.lyr")
    landuse_symbology = os.path.join(symbology_folder, "Land_Use_Raster.lyr")
    land_ownership_symbology = os.path.join(symbology_folder, "SurfaceManagementAgency.lyr")
    canals_symbology = os.path.join(symbology_folder, "Canals.lyr")
    roads_symbology = os.path.join(symbology_folder, "Roads.lyr")
    railroads_symbology = os.path.join(symbology_folder, "Railroads.lyr")
    valley_bottom_symbology = os.path.join(symbology_folder, "ValleyBottom.lyr")
    valley_bottom_outline_symbology = os.path.join(symbology_folder, "ValleyBottom_Outline.lyr")
    flow_direction_symbology = os.path.join(symbology_folder, "Network_FlowDirection.lyr")

    # add the existing veg inputs to project
    ex_veg_destinations = copy_multi_input_to_folder(ex_veg_folder, ex_veg, "Ex_Veg", is_raster=True)
    make_input_layers(ex_veg_destinations, "Existing Vegetation Suitability for Beaver Dam Building", symbology_layer=ex_veg_suitability_symbology, is_raster=True, file_name="ExVegSuitability")
    make_input_layers(ex_veg_destinations, "Existing Riparian", symbology_layer=ex_veg_riparian_symbology, is_raster=True, check_field="EVT_PHYS")
    make_input_layers(ex_veg_destinations, "Veg Type - EVT Type", symbology_layer=ex_veg_evt_type_symbology, is_raster=True, check_field="EVT_PHYS")
    make_input_layers(ex_veg_destinations, "Veg Type - EVT Class", symbology_layer=ex_veg_evt_class_symbology, is_raster=True)
    # make_input_layers(ex_veg_destinations, "Veg Type - EVT Class Name", symbology_layer=ex_veg_class_name_symbology, is_raster=True)


    # add the historic veg inputs to project
    hist_veg_destinations = copy_multi_input_to_folder(hist_veg_folder, hist_veg, "Hist_Veg", is_raster=True)
    make_input_layers(hist_veg_destinations, "Historic Vegetation Suitability for Beaver Dam Building", symbology_layer=hist_veg_suitability_symbology, is_raster=True, file_name="HistVegSuitability")
    make_input_layers(hist_veg_destinations, "Veg Type - BPS Type", symbology_layer=hist_veg_group_symbology, is_raster=True, check_field="GROUPVEG")
    make_input_layers(hist_veg_destinations, "Veg Type - BPS Name", symbology_layer=hist_veg_bps_name_symbology, is_raster=True)
    make_input_layers(hist_veg_destinations, "Historic Riparian", symbology_layer=hist_veg_riparian_symbology, is_raster=True, check_field="GROUPVEG")


    # add the network inputs to project
    network_destinations = copy_multi_input_to_folder(network_folder, network, "Network", is_raster=False)
    make_input_layers(network_destinations, "Network", symbology_layer=network_symbology, is_raster=False)
    make_input_layers(network_destinations, "Flow Direction", symbology_layer=flow_direction_symbology, is_raster=False)

    # add the DEM inputs to the project
    copy_multi_input_to_folder(topo_folder, DEM, "DEM", is_raster=True)
    make_topo_layers(topo_folder)

    # add landuse raster to the project
    if landuse is not None:
        landuse_destinations = copy_multi_input_to_folder(land_use_folder, landuse, "Land_Use", is_raster=True)
        make_input_layers(landuse_destinations, "Land Use Raster", symbology_layer=landuse_symbology, is_raster=True)

    # add the conflict inputs to the project
    if valley is not None:
        vally_bottom_destinations = copy_multi_input_to_folder(valley_bottom_folder, valley, "Valley", is_raster=False)
        make_input_layers(vally_bottom_destinations, "Valley Bottom Fill", symbology_layer=valley_bottom_symbology, is_raster=False)
        make_input_layers(vally_bottom_destinations, "Valley Bottom Outline", symbology_layer=valley_bottom_outline_symbology, is_raster=False)

    # add road layers to the project
    if road is not None:
        road_destinations = copy_multi_input_to_folder(road_folder, road, "Roads", is_raster=False)
        make_input_layers(road_destinations, "Roads", symbology_layer=roads_symbology, is_raster=False)

    # add railroad layers to the project
    if rr is not None:
        rr_destinations = copy_multi_input_to_folder(railroad_folder, rr, "Railroads", is_raster=False)
        make_input_layers(rr_destinations, "Railroads", symbology_layer=railroads_symbology, is_raster=False)

    # add canal layers to the project
    if canal is not None:
        canal_destinations = copy_multi_input_to_folder(canals_folder, canal, "Canals", is_raster=False)
        make_input_layers(canal_destinations, "Canals", symbology_layer=canals_symbology, is_raster=False)

    # add land ownership layers to the project
    if ownership is not None:
        ownership_destinations = copy_multi_input_to_folder(land_ownership_folder, ownership, "Land Ownership", is_raster=False)
        make_input_layers(ownership_destinations, "Land Ownership", symbology_layer=land_ownership_symbology, is_raster=False)

def copy_multi_input_to_folder(folder_path, multi_input, sub_folder_name, is_raster):
    """
    Copies multi input ArcGIS inputs into the folder that we want them in
    :param folder_path: The root folder, where we'll put a bunch of sub folders
    :param multi_input: A string, with paths to the inputs seperated by semicolons
    :param sub_folder_name: The name for each subfolder (will have a number after it)
    :param is_raster: Tells us if the thing is a raster or not
    :return:
    """
    split_input = multi_input.split(";")
    i = 1
    destinations = []
    for input_path in split_input:
        new_sub_folder = make_folder(folder_path, sub_folder_name + "_" + str(i))
        destination_path = os.path.join(new_sub_folder, os.path.basename(input_path))

        if is_raster:
            arcpy.CopyRaster_management(input_path, destination_path)
        else:
            arcpy.Copy_management(input_path, destination_path)
        destinations.append(destination_path)
        i += 1
    return destinations


def make_topo_layers(topo_folder):
    """
    Writes the layers
    :param topo_folder: We want to make layers for the stuff in this folder
    :return:
    """
    source_code_folder = os.path.dirname(os.path.abspath(__file__))
    symbology_folder = os.path.join(source_code_folder, 'BRATSymbology')
    dem_symbology = os.path.join(symbology_folder, "DEM.lyr")
    slope_symbology = os.path.join(symbology_folder, "Slope.lyr")
    hillshade_symbology = os.path.join(symbology_folder, "Hillshade.lyr")

    for folder in os.listdir(topo_folder):
        dem_folder_path = os.path.join(topo_folder, folder)
        dem_file = None
        for file_name in os.listdir(dem_folder_path):
            if file_name.endswith(".tif"):
                dem_file = os.path.join(dem_folder_path, file_name)
                make_layer(dem_folder_path, dem_file, "DEM", dem_symbology, is_raster=True)

        hillshade_folder = make_folder(dem_folder_path, "Hillshade")
        hillshade_file = os.path.join(hillshade_folder, "Hillshade.tif")
        arcpy.HillShade_3d(dem_file, hillshade_file)
        make_layer(hillshade_folder, hillshade_file, "Hillshade", hillshade_symbology, is_raster=True)

        slope_folder = make_folder(dem_folder_path, "Slope")
        slope_file = os.path.join(slope_folder, "Slope.tif")
        out_slope = arcpy.sa.Slope(dem_file)
        out_slope.save(slope_file)
        make_layer(slope_folder, slope_file, "Slope", slope_symbology, is_raster=True)


def make_input_layers(destinations, layer_name, is_raster, symbology_layer=None, file_name=None, check_field=None):
    """
    Makes the layers for everything in the folder
    :param destinations: A list of paths to our input
    :param layer_name: The name of the layer
    :param is_raster: Whether or not it's a raster
    :param symbology_layer: The base for the symbology
    :param file_name: The name for the file (if it's different from the layerName)
    :param check_field: The name of the field that the symbology is based on
    :return:
    """
    if file_name is None:
        file_name = layer_name
    for destination in destinations:
        dest_dir_name = os.path.dirname(destination)
        if check_field:
            fields = [f.name for f in arcpy.ListFields(destination)]
            if check_field not in fields:
                # Stop execution if the field we're checking for is not in the layer base
                return
        make_layer(dest_dir_name, destination, layer_name, symbology_layer=symbology_layer, is_raster=is_raster, file_name=file_name)


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
        sys.argv[10],
        sys.argv[11])
