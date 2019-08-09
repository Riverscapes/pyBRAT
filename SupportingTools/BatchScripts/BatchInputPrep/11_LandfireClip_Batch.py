# -------------------------------------------------------------------------------
# Name:        LANDFIRE Clip (Batch_
#
# Purpose:     Script clips projectwide LANDFIRE EVT (existing vegetation) and BPS
#               (historic vegetation) to individual HUC8 boundaries. The HUC8-level
#               LANDFIRE rasters are saved to a LANDFIRE subfolder within each HUC8
#               directory.
#
# Notes:        - The scripts assumes data are in standard ETAL BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) a 'NHD' folder is directly under each individual basin folder and
#                   contains a 'WBDHU8.shp' polygon
#               - The script will execute on all subfolders in the parent folder EXCEPT
#                 those that start with a '00_*' (e.g., '00_Projectwide')
#
# Date:        March 2019
# Author:      Maggie Hallerud (maggie.hallerud@aggiemail.usu.edu)
# -------------------------------------------------------------------------------

# user defined inputs:

# evt_path - path to projectwide EVT
# bps_path - path to projectwide BPS
# pf_path - path to project folder for batch processing
# out_evt_name - name for output EVT files
# out_bps_name - name for output BPS files
evt_path = r"C:\Users\a02046349\Desktop\GYE_BRAT\wrk_Data\00_Projectwide\LANDFIRE\LANDFIRE_200EVT.tif"
bps_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\LANDFIRE\LANDFIRE_140BPS.tif"
pf_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data"
out_evt_name = "LANDFIRE_200EVT"
out_bps_name = "LANDFIRE_200BPS"


#  import required modules and extensions
import arcpy
import os
arcpy.CheckOutExtension('Spatial')


def ras_clip(x, type):
    print 'Clipping LANDFIRE ' + type + ' for: ' + str(x)
    # set output names and base raster paths
    if type == 'EVT':
        ras_path = evt_path
        out_name = out_evt_name + '.tif'
    else:
        ras_path = bps_path
        out_name = out_bps_name + '.tif'

    # create output LANDFIRE folder if it doesn't already exist
    out_folder = os.path.join(pf_path, x, 'LANDFIRE')
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # read in huc8 shp
    huc8_shp = os.path.join(pf_path, x, 'NHD', 'WBDHU8.shp')

    # clip input landfire raster by huc8_shp
    arcpy.Clip_management(ras_path, '', os.path.join(out_folder, out_name), huc8_shp, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')


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
    arcpy.env.resamplingMethod = 'NEAREST'  # set resampling method to nearest in case arc does any behind the scenes dem re-sampling

    # run dem_clip function for each huc8 folder
    for dir in dir_list:
        ras_clip(dir, 'EVT')
        ras_clip(dir, 'BPS')

    # reset arcpy environment
    arcpy.ResetEnvironments()
    arcpy.ClearEnvironment("workspace")

if __name__ == '__main__':
    main()
