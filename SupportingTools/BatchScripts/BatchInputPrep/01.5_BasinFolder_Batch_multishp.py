# --------------------------------------------------------------------------
# Name: Basin Folder 2 (Batch)
# Purpose: Mostly copied from Sara Bangen's 01_BasinFolder_Batch & 02_NHDClip_Batch
#          Adapted to create basin subfolders, clip and copy over NHD data downloaded
#             by watershed rather than by project area          
#
# Author: Maggie Hallerud
# --------------------------------------------------------------------------


nhd_path = 'C:/Users/Maggie/Downloads/GYA'
pf_path = 'C:/Users/Maggie/Desktop/GYA/wrk_Data'
coord_sys = 'NAD 1983 UTM Zone 12N'

import os
import re
import arcpy


def main(nhd_path, pf_path, coord_sys):
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = 'in_memory'
    outCS = arcpy.SpatialReference(coord_sys)
    os.chdir(nhd_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    os.mkdir(os.path.join(pf_path, '00_Projectwide')
    for dir in dir_list:
        # make huc folder
        dir_sep = dir.split('_')
        huc_num = dir_sep[2]
        huc_wbd = os.path.join(dir, 'Shape', 'WBDHU8.shp')
        huc_name = str(arcpy.da.SearchCursor(huc_wbd, ['Name']).next()[0])
        new_huc_name = re.sub(r'\W+', '', huc_name)
        huc_folder = os.path.join(pf_path, new_huc_name + '_' + str(huc_num))
        if not os.path.exists(huc_folder):
            os.makedirs(huc_folder)

        # pull required NHD data
        flowline_shp = os.path.join(nhd_path, dir, 'Shape', 'NHDFlowline.shp')
        area_shp = os.path.join(nhd_path, dir, 'Shape', 'NHDArea.shp')
        wbody_shp = os.path.join(nhd_path, dir, 'Shape', 'NHDWaterbody.shp')
        wbd_shp = huc_wbd

        # include only streams and canals
        arcpy.MakeFeatureLayer_management(flowline_shp, 'tmp_huc8_flowlines_lyr')
        quer = """ "FTYPE" = 428 OR "FTYPE" = 420 OR "FTYPE" = 566 """
        arcpy.SelectLayerByAttribute_management('tmp_huc8_flowline_lyr', 'NEW_SELECTION', quer)
        arcpy.SelectLayerByAttribute_management('tmp_huc8_flowlines_lyr', 'SWITCH_SELECTION')
        huc8_flowlines = arcpy.CopyFeatures_management('tmp_huc8_flowlines_lyr', os.path.join(nhd_folder, 'NHDFlowline.shp'))        

        # reproject data and save to project folder
        if not os.path.exists(os.path.join(huc_folder, 'NHD')):
            os.mkdir(os.path.join(huc_folder, 'NHD'))
            arcpy.Project_management(flowline_shp, os.path.join(huc_folder, 'NHD', 'NHDFlowline.shp'), outCS)
            arcpy.Project_management(area_shp, os.path.join(huc_folder, 'NHD', 'NHDArea.shp'), outCS)
            arcpy.Project_management(wbody_shp, os.path.join(huc_folder, 'NHD', 'NHDWaterbody.shp'), outCS)
            arcpy.Project_management(wbd_shp, os.path.join(huc_folder, 'NHD', 'WBDHU8.shp'), outCS)

        
if __name__ == "__main__":
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])
