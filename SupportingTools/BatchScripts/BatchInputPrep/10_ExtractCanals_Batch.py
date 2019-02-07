#######################################################################
# Name: ExtractCanals_Batch
#
# Purpose: Extract canals as shapefile from NHD flowline data for
#            each HUC8 in a project area.
# Author: Maggie Hallerud
#######################################################################

# import required modules
import arcpy
import os

# user defined paths
pf_path = 'C:/Users/Maggie/Desktop/GYA/wrk_Data'
arcpy.CheckOutExtension('Spatial')

def main():
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

    # extract canals for each huc8 NHD network and save as 'NHDCanals.shp'
    for dir in dir_list:
        # tracking progress
        print "Extracting canal shapefile for " + dir
        # specifying input NHD and output canal shapefiles
        flowline_shp = os.path.join(pf_path, dir, 'NHD/NHDFlowline.shp')
        canal_shp = os.path.join(pf_path, dir, 'NHD/NHDCanals.shp')
        # run extract canals for all watersheds if none present
        if not os.path.exists(canal_shp):
            try:
                tmp_huc8_flowline = arcpy.MakeFeatureLayer_management(flowline_shp, 'tmp_huc8_flowlines_lyr')
                quer = """ "FTYPE" = 336 """
                arcpy.SelectLayerByAttribute_management(tmp_huc8_flowline, 'NEW_SELECTION', quer)
                arcpy.CopyFeatures_management(tmp_huc8_flowline, canal_shp)
            # catch errors and move to the next huc8 folder
            except Exception as err:
                print "Error with " + dir + ". Exception thrown was: "
                print err



if __name__ == "__main__":
    main()
