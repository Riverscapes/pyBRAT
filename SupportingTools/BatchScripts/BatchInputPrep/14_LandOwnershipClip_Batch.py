# -------------------------------------------------------------------------------
# Name:        Land Ownership Clip (Batch)
#
# Purpose:     Script clips projectwide land ownership shapefile for each HUC8 polygon
#              shapefile.  Output shapefiles are written to a 'LandOwnership' folder
#
# Notes:       - The scripts assumes data are in standard ETAL BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) there is a a subfolder in each individaul basin folder called 'NHD'
#                   with a 'WBDHU8.shp'
#
# Date:        March 2019
# Author:      Maggie Hallerud (maggie.hallerud@aggiemail.usu.edu)
# -------------------------------------------------------------------------------

# User defined arguments:

# pf_path - path to parent folder that holds HUC8 folders
# ownership_path - path to ownership shapefile to be clipped
pf_path = r"C:\Users\ETAL\Dekstop\GYE_BRAT\wrk_Data"
ownership_path = r"C:\Users\ETAL\Dekstop\GYE_BRAT\wrk_Data\00_Projectwide\LandOwnership\BLM_National_Surface_Management_Agency\NationalSurfaceManagementAgency_ProjectArea.shp"


#  import required modules and extensions
import arcpy
import os
import re
arcpy.CheckOutExtension('Spatial')


def main():

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
        out_folder = os.path.join(pf_path, dir, 'LandOwnership')
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        huc8_shp = os.path.join(pf_path, dir, 'NHD', 'WBDHU8.shp')
        if not os.path.exists(huc8_shp):
            print 'No huc 8 shapefile named WBDHU8.shp'
        else:
            # clip roads and rails layers to the huc 8 shp
            arcpy.Clip_analysis(ownership_path, huc8_shp, os.path.join(out_folder, 'NationalSurfaceManagementAgency.shp'))


if __name__ == '__main__':
    main()
