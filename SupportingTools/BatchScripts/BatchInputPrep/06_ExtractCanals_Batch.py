#######################################################################
# Name: ExtractCanals_Batch
#
# Purpose: Extracts canals and ditches from NHD flowline data
#          for each HUC8 in a project area.  Will only create
#          output shapefile if canals and ditches exist
#          for the basin.

#
# Author: Maggie Hallerud
#######################################################################

# import required modules
import arcpy
import os
arcpy.CheckOutExtension('Spatial')

# user defined paths
pf_path = r'C:\Users\a02046349\Desktop\GYE_BRAT\wrk_Data' # project folder path


def main(overwrite = True):
# if overwrite = False, will not overwrite current canals and ditches shapefiles if present
# default is to overwrite

    # set up arcpy environment
    arcpy.env.workspace = 'in_memory'
    arcpy.env.overwriteOutput = True
    os.chdir(pf_path)

    # list all folders in parent folder - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    # remove folders in the list that start with '00_' since these aren't the HUC8 watersheds
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # extract canals for each huc8 NHD network and save as 'NHDCanalsDitches.shp'
    for dir in dir_list:

        # specifying input NHD and output canal shapefiles
        flowline_shp = os.path.join(pf_path, dir, 'NHD/NHDFlowline.shp')
        canal_shp = os.path.join(pf_path, dir, 'NHD/NHDCanalsDitches.shp')

        # extract canals and ditches for all watersheds if none present
        if not os.path.exists(canal_shp) or overwrite is True:
            print "Extracting canal shapefile for " + dir
            try:
                tmp_huc8_flowline = arcpy.MakeFeatureLayer_management(flowline_shp, 'tmp_huc8_flowlines_lyr')
                # select all flowlines with canal/ditch ftype (336) or that have 'Ditch' in name field
                quer = """ "FTYPE" = 336 OR "GNIS_NAME" LIKE '%Ditch%' """
                arcpy.SelectLayerByAttribute_management(tmp_huc8_flowline, 'NEW_SELECTION', quer)
                # note: removes any pipelines with name 'Ditch' since these are excluded from segmented network
                #       it's unlikely such cases occur, but just covering such instances
                quer_remove = """ "FTYPE" = 428 OR "FTYPE" = 420 OR "FTYPE" = 566"""
                arcpy.SelectLayerByAttribute_management(tmp_huc8_flowline, 'REMOVE_FROM_SELECTION', quer_remove)
                # save output if any flowlines were selected
                count = arcpy.GetCount_management(tmp_huc8_flowline)
                ct = int(count.getOutput(0))
                if ct >= 1:
                    arcpy.CopyFeatures_management(tmp_huc8_flowline, canal_shp)
            # catch errors and move to the next huc8 folder
            except Exception as err:
                print "Error with " + dir + ". Exception thrown was: "
                print err


if __name__ == "__main__":
    main()
