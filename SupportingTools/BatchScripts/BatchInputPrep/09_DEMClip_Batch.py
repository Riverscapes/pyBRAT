# -------------------------------------------------------------------------------
# Name:        DEM Clip (Batch)
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

# User defined arguments:

# pf_path - path to parent folder that holds HUC8 folders
# dem_path - filepath to DEM to be clipped
# out_name - output raster name without file extension(for ETAL users using 10 m DEMS should use 'NED_DEM_10m')

#  user defined paths
pf_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data"
dem_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\DEM\NED_DEM_10m.tif"
out_name = 'NED_DEM_10m'

#  import required modules and extensions
import arcpy
import os
arcpy.CheckOutExtension('Spatial')


def dem_clip(x):

    # print subdir name to track script progress for user
    print 'Clipping DEM for: ' + str(x)

    # create output dem folder if it doesn't already exist
    dem_folder = os.path.join(pf_path, x, 'DEM')
    if not os.path.exists(dem_folder):
        os.makedirs(dem_folder)

    # read in huc8 shp and get the huc8 code
    huc8_shp = os.path.join(pf_path, x, 'NHD', 'WBDHU8.shp')

    # clip input dem by huc8_shp
    arcpy.Clip_management(dem_path, '', os.path.join(dem_folder, out_name + '.tif'), huc8_shp, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')


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
    arcpy.env.resamplingMethod = 'CUBIC'  # set resampling method to cubic in case arc does any behind the scenes dem re-sampling

    # run dem_clip function for each huc8 folder
    for dir in dir_list:
        if not os.path.exists(os.path.join(pf_path, dir, 'DEM')):
            try:
                dem_clip(dir)
            except Exception as err:
                print "Clipping DEM failed for " + dir + ". The exception thrown was:"
                print err

    # clear environment settings
    arcpy.ResetEnvironments()
    arcpy.ClearEnvironment("workspace")


if __name__ == '__main__':
    main()
