# -------------------------------------------------------------------------------
# Name:        PRISM Clip (Batch)
#
# Purpose:     Script clips project-scale DEM to individual HUC8 polygon shapefiles.
#              The individual clipped DEMs are written to a 'DEM' subfolder (which
#              is created if it doens't already exist) under the corresponding HUC8 folder
#
# Notes:       - The scripts assumes data are in standard ETAL BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) a 'NHD' folder is directly under each individual basin folder and
#                   contains a 'WBDHU8.shp' polygon
#               - The script will execute on all subfolders in the parent folder EXCEPT
#                 those that start with a '00_*' (e.g., '00_Projectwide')

# Author:      Sara Bangen (sara.bangen@gmail.com)
# -------------------------------------------------------------------------------

# user defined arguments:
# pf_path - path to project folder holding all HUC8 subdirectories
pf_path = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data'


# import dependencies
import arcpy
import os
arcpy.CheckOutExtension('Spatial')
from arcpy.sa import *


def main():
    arcpy.env.overwriteOutput=True
    
    os.chdir(pf_path)
    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    for dir in dir_list:
        dem = os.path.join(pf_path, dir, 'DEM/NED_DEM_10m.tif')
        huc = os.path.join(pf_path, dir, 'NHD/WBDHU8.shp')
        try:
            print 'Checking DEM for ' + dir + '.....'

	    # convert DEM to polygon
            dem_cover = os.path.join(pf_path, dir, 'DEM/DEM_area.shp')
            dem_reclass = arcpy.sa.Reclassify(dem, 'Value', RemapRange([[0, 10000, 1]]))
            arcpy.RasterToPolygon_conversion(dem_reclass, dem_cover, 'SIMPLIFY', 'VALUE')

            # get HUC8 area
            huc_area = []
            with arcpy.da.SearchCursor(huc, field_names='SHAPE@AREA') as huc_cursor:
                for row in huc_cursor:
                    huc_area = huc_cursor[0]

            # get DEM area
            dem_area = []
            with arcpy.da.SearchCursor(dem_cover, field_names='SHAPE@AREA') as dem_cursor:
                for row in dem_cursor:
                    dem_area.append(row[0])

            # Check for large difference between DEM area and watershed area
            if abs(dem_area - huc_area) > 100000:
                print '         HUC area: ' + str(sum(huc_area))
                print '         DEM area: ' + str(sum(dem_area))
            # delete DEM shapefile
            arcpy.Delete_management(dem_cover)
        except Exception as err:
            print err


if __name__ == "__main__":
    main()
