# -------------------------------------------------------------------------------
# Name:        Basin Folder (Batch)
#
# Purpose:     Script creates basin subfolders from HUC8 polygon shapefile.
#              Folder names are compressed basin name followed by HUC8 ID (e.g., CoeurdAleneLake_17010303)
#
# Author:      Sara Bangen (sara.bangen@gmail.com)
# -------------------------------------------------------------------------------

# User defined arguments:

# out_path - path to parent folder where all HUC8 subfolders will be created
# huc8_aoi_path - filepath to project area HUC8 shapefile

out_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data"
huc8_aoi_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\ProjectBoundary\WBDHU8_ProjectArea.shp"

#  import required modules and extensions
import arcpy
import os
import re
arcpy.CheckOutExtension('Spatial')


def main():

    #  environment settings
    arcpy.env.workspace = 'in_memory' # set workspace to temporary workspace
    arcpy.env.overwriteOutput = True  # set to overwrite output

    # copy nhd layers we need for brat into temporary workspace
    huc8s = arcpy.CopyFeatures_management(huc8_aoi_path, 'in_memory/huc8s')

    # create list of all huc 8 ids
    huc8s_list = [row[0] for row in arcpy.da.SearchCursor(huc8s, 'HUC8')]

    # for each huc 8 id in the list....
    for huc8 in huc8s_list:
        # compress HUC8 name
        huc8_shp = arcpy.Select_analysis(huc8s, 'in_memory/huc8_' + str(huc8), "HUC8 = '%s'" % str(huc8))
        huc8_name = str(arcpy.da.SearchCursor(huc8_shp, ['NAME']).next()[0])
        huc8_name_new = re.sub(r'\W+', '', huc8_name)

        # print subdir name to track script progress for user
        print 'Creating subfolder for: ' + str(huc8_name)

        # create HUC8 subfolder if it doesn't already exist
        huc8_folder = os.path.join(out_path, huc8_name_new + '_' + str(huc8))
        if not os.path.exists(huc8_folder):
            os.makedirs(huc8_folder)


if __name__ == '__main__':
    main()
