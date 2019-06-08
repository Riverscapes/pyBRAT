# -------------------------------------------------------------------------------
# Name:        Roads Rails Clip (Batch)
#
# Purpose:     Script clips projectwide road and rails shapefile for each HUC8 polygon
#              shapefile.  Output shapefiles are written to a 'RoadsRails' folder
#
# Notes:       - The scripts assumes data are in standard ETAL BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) there is a a subfolder in each individaul basin folder called 'NHD'
#                   with a 'WBDHU8.shp'
#              - Rails shapefile will only be output if rails exist in watershed

# Author:      Sara Bangen (sara.bangen@gmail.com)
# -------------------------------------------------------------------------------

#  import required modules and extensions
import arcpy
import os
import re

# User defined arguments:

# pf_path - path to parent folder that holds HUC8 folders
# roads_path - path to roads shapefile to be clipped
# rails_path - path to rails shapefile to be clipped

pf_path = r"C:\Users\a02046349\Desktop\GYE_BRAT\wrk_Data"
roads_path = os.path.join(pf_path, '00_Projectwide/RoadsRails/tl_2018_roads.shp')
rails_path = "C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/RoadsRails/tl_2018_us_rails.shp"
coord_sys = 'NAD 1983 UTM Zone 12 N'

def main():

    # load required extension
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = 'in_memory'

    proj_road_folder = os.path.join(pf_path, '00_Projectwide/RoadsRails')
    if not os.path.exists(proj_road_folder):
        os.mkdir(proj_road_folder)

    # reprojecting original datasets
    print "Reprojecting original railroad data set..."
    outCS = arcpy.SpatialReference(coord_sys)
    out_path = os.path.join(proj_road_folder, 'tl_2018_us_rails.shp')
    #proj_rails = arcpy.Project_management(rails_path, out_path, outCS) 
    proj_rails = rails_path
    
    # change directory to the parent folder path
    os.chdir(pf_path)
    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)
    # set arcpy environment settings
    arcpy.env.overwriteOutput = 'TRUE'  # overwrite output

    # for each folder in the list....
    for dir in dir_list:
        print dir
        try:
            # create output folder
            out_folder = os.path.join(pf_path, dir, 'RoadsRails')
            if not os.path.exists(out_folder):
                os.makedirs(out_folder)

            huc8_shp = os.path.join(pf_path, dir, 'NHD', 'WBDHU8.shp')
            if not os.path.exists(huc8_shp):
                print 'No huc 8 shapefile named WBDHU8.shp'
            else:
                # clip roads to the huc 8 shp
                arcpy.Clip_analysis(roads_path, huc8_shp, os.path.join(out_folder, os.path.basename(roads_path)))
                # clip rails to the huc 8 shp and save only if rails exist
                rails_clip = arcpy.Clip_analysis(proj_rails, huc8_shp, 'in_memory/rails_clip')
                count = arcpy.GetCount_management(rails_clip)
                ct = int(count.getOutput(0))
                if ct >= 1:
                    arcpy.CopyFeatures_management(rails_clip, os.path.join(out_folder, os.path.basename(rails_path)))
        except Exception as error:
            print err


if __name__ == '__main__':
    main()
