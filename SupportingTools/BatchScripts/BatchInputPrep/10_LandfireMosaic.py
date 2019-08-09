# -------------------------------------------------------------------------------
# Name:        LANDFIRE Mosaic
#
# Purpose:     Script mosaics LANDFIRE tiles into single projectwide raster,
#               reprojects to project coordinate system, joins original LANDFIRE
#               attributes, and calculate landuse values for the EVT
#
# Notes:        - The script assumes that downloaded tiles are in the *.tif format
#               - The scripts assumes data are in standard ETAL BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) a 'NHD' folder is directly under each individual basin folder and
#                   contains a 'WBDHU8.shp' polygon
#               - The script will execute on all subfolders in the parent folder EXCEPT
#                 those that start with a '00_*' (e.g., '00_Projectwide')
#
# Date:        March 2019
# Author:      Sara Bangen (sara.bangen@gmail.com)
# -------------------------------------------------------------------------------

# user defined inputs:

# ras_path - path to folder holding downloaded LANDFIRE tiles
# out_path - filepath to folder where output LANDFIRE data will be saved
# out_evt_with_extension - output name of EVT raster with extension (e.g., ".tif", ".img", etc.)
# out_bps_with_extension - output name of BPS raster with extension (e.g., ".tif", ".img", etc.)
# aoi_path - polygon shapefile representing project area, outputs will be clipped to this
# coord_sys - project coordinate system, to which all outputs will be reprojected
# lu_code_path - path to LANDFIRE_LUCode.py file (in batch scripts)
ras_path = r'C:\Users\ETAL\Desktop\GYE_BRAT\wrk_Data\00_Projectwide\LANDFIRE\tiles'
out_path = r'C:\Users\ETAL\Desktop\GYE_BRAT\wrk_Data\00_Projectwide\LANDFIRE'
out_evt_with_extension = 'LANDFIRE_200EVT.tif'
out_bps_with_extension = 'LANDFIRE_200BPS.tif'
aoi_path = r'C:\Users\ETAL\Desktop\GYE_BRAT\wrk_Data\00_Projectwide\ProjectBoundary\GYE_HUC8_ProjectArea_WY.shp'
coord_sys = 'NAD 1983 UTM Zone 12N'
lu_code_path = "C:\Users\ETAL\Desktop\BatchScripts"


#  import required modules and extensions
import arcpy
import os
import sys
sys.path.append(lu_code_path)
import LANDFIRE_LUCode

# set up arcpy environment
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')


def main():

    # set blank lists for EVT and BPS
    evt_list = []
    bps_list = []

    # make list of all EVT and BPS files within ras_path folder
    def search_files(directory, extension):
        extension = extension.lower()
        for dirpath, dirnames, files in os.walk(directory):
            for name in files:
                if extension and name.lower().endswith(extension):
                    #print(os.path.join(ras_path, dirpath, name))
                    if 'BPS' in name:
                        bps_list.append(os.path.join(ras_path, dirpath, name))
                    elif 'EVT' in name:
                        evt_list.append(os.path.join(ras_path, dirpath, name))
                    else:
                        pass

    search_files(directory = ras_path, extension = '.tif')

    # set up arcpy environment
    arcpy.env.overwriteOutput = 'TRUE'
    arcpy.env.resamplingMethod = 'NEAREST'

    # define output coordinate system based on user input
    outCS = arcpy.SpatialReference(coord_sys)

    # mosaic list of BPS tiles to a temporary file in the output folder with defined coordinate system
    tmp_bps_ras = arcpy.MosaicToNewRaster_management(bps_list, out_path, 'tmp_' + out_bps_with_extension, outCS, "16_BIT_SIGNED", "", "1")

    # copies all BPS values from original tiles to list
    bps_tbl_list = []
    index = 1
    for ras in bps_list:
        tbl_path = os.path.join(out_path, 'tmp_bps_tbl_' + str(index) + '.dbf')
        arcpy.CopyRows_management(ras, tbl_path)
        bps_tbl_list.append(tbl_path)
        index += 1
    print bps_tbl_list

    # copies BPS values list to .dbf format and keeps only unique values
    bps_tbl = arcpy.Merge_management(bps_tbl_list, os.path.join(out_path, 'tmp_bps_tbl.dbf'))
    arcpy.DeleteIdentical_management(bps_tbl, ['Value'])

    # builds RAT for temporary BPS
    arcpy.BuildRasterAttributeTable_management(tmp_bps_ras, "Overwrite")

    # joins fields from BPS values .dbf to temporary BPS
    tbl_fields = [f.name for f in arcpy.ListFields(bps_tbl)]
    join_fields = []
    drop = ['Count', 'Value', 'OID']
    for field in tbl_fields:
        if field not in drop:
            join_fields.append(field)
    print join_fields
    arcpy.JoinField_management(tmp_bps_ras, 'Value', bps_tbl, 'VALUE', join_fields)

    # clips temporary BPS to area of interest and saves
    arcpy.Clip_management(tmp_bps_ras, '', os.path.join(out_path, out_bps_with_extension), aoi_path, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')

    # mosaic list of EVT tiles to a temporary file in the output folder with defined coordinate system
    tmp_evt_ras = arcpy.MosaicToNewRaster_management(evt_list, out_path, 'tmp_' + out_evt_with_extension, outCS, "16_BIT_SIGNED", "", "1")

    # copies all EVT values from original tiles to list
    evt_tbl_list = []
    index = 1
    for ras in evt_list:
        tbl_path = os.path.join(out_path, 'tmp_evt_tbl_' + str(index) + '.dbf')
        arcpy.CopyRows_management(ras, tbl_path)
        evt_tbl_list.append(tbl_path)
        index += 1
    print evt_tbl_list

    # copies EVT values list to .dbf format and keeps only unique values
    evt_tbl = arcpy.Merge_management(evt_tbl_list, os.path.join(out_path, 'tmp_evt_tbl.dbf'))
    arcpy.DeleteIdentical_management(evt_tbl, ['Value'])

    # builds RAT for temporary EVT
    arcpy.BuildRasterAttributeTable_management(tmp_evt_ras, "Overwrite")

    # joins fields from evt values .dbf to temporary EVT
    tbl_fields = [f.name for f in arcpy.ListFields(evt_tbl)]
    join_fields = []
    drop = ['Count', 'Value', 'OID']
    for field in tbl_fields:
        if field not in drop:
            join_fields.append(field)
    print join_fields
    arcpy.JoinField_management(tmp_evt_ras, 'Value', evt_tbl, 'VALUE', join_fields)

    # clips temporary EVT to area of interest and saves
    arcpy.Clip_management(tmp_evt_ras, '', os.path.join(out_path, out_evt_with_extension), aoi_path, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')

    # calculates landuse values for output EVT
    LANDFIRE_LUCode.main(os.path.join(out_path, out_evt_with_extension)
                         
    # xResult = arcpy.GetRasterProperties_management(evt_ras, 'CELLSIZEX')
    # yResult = arcpy.GetRasterProperties_management(evt_ras, 'CELLSIZEY')
    # print 'Cell Size X: ' + str(xResult.getOutput(0))
    # print 'Cell Size Y: ' + str(yResult.getOutput(0))

    # clears workspace and environments
    arcpy.ResetEnvironments()
    arcpy.ClearEnvironment("workspace")

if __name__ == '__main__':
    main()
