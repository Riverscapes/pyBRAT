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
#
# Date:        March 2019
# Author:      Sara Bangen (sara.bangen@gmail.com)
# -------------------------------------------------------------------------------

# User defined arguments:

# pf_path - path to parent folder that holds HUC8 folders
# roads_path - path to roads shapefile to be clipped
# rails_path - path to rails shapefile to be clipped

pf_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data"
roads_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\Roads\tl_2018_roads.shp"
rails_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\Rails\tl_2017_rails.shp"


def main():

    #  import required modules and extensions
    import arcpy
    import os
    import re
    arcpy.CheckOutExtension('Spatial')

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
            rails_clip = arcpy.Clip_analysis(rails_path, huc8_shp, 'in_memory/rails_clip')
            count = arcpy.GetCount_management(rails_clip)
            ct = int(count.getOutput(0))
            if ct >= 1:
                arcpy.CopyFeatures_management(rails_clip, os.path.join(out_folder, os.path.basename(rails_path)))


if __name__ == '__main__':
    main()
