# -----------------------------------------------------------------------------------------
# Name:     Basin Folder (Batch) - from NHD data at the HUC8 level
#
# Purpose:  Creates basin subfolders and copies over downloaded NHD data from data
#           downloaded as HUC8 NHD folders
#           Output Folder names are compressed basin names followed by HUC ID #
#
# Note:     The downloaded data MUST be downloaded by HUC8, i.e. data from each
#           HUC8 is downloaded into a separate folder within the nhd_pth folder specified
#
# Author:   Maggie Hallerud (maggie.hallerud@aggiemail.usu.edu)
# Date:     March 2019
# -----------------------------------------------------------------------------------------

# user-defined inputs
# nhd_path - path to project NHD data
# pf_path - project folder for batch processing
# coord_sys - project coordinate system, which all data will be repojected to
nhd_path = 'C:/Users/ETAL/Downloads/GYA' 
pf_path = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data'
coord_sys = 'NAD 1983 UTM Zone 12N'


# load dependencies
import os
import re
import arcpy


def main():
    
    # define coordinate system based on user input
    outCS = arcpy.SpatialReference(coord_sys)

    # change working directory to NHD download folder
    os.chdir(nhd_path)
    
    # make list of all folders in NHD download folder
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    # loop through download folders
    for dir in dir_list:
        
        # make huc folder within project folder using name nad ID specified by WBDHU8 HUC8 boundary SHP
        dir_sep = dir.split('_')
        huc_num = dir_sep[2] # HUC8 ID from download folder name
        huc_wbd = os.path.join(dir, 'Shape', 'WBDHU8.shp') # downloaded WBDHU8
        huc_name = str(arcpy.da.SearchCursor(huc_wbd, ['Name']).next()[0]) # HUC8 full name from WBDHU8
        new_huc_name = re.sub(r'\W+', '', huc_name) # shortened HUC8 name
        huc_folder = os.path.join(pf_path, new_huc_name + '_' + str(huc_num)) # new HUC8 folder name
        if not os.path.exists(huc_folder): # make HUC8 folder unless already exists
            os.mkdir(huc_folder)

        # find needed HUC8 NHD data within download folder
        flowline_shp = os.path.join(nhd_path, dir, 'Shape', 'NHDFlowline.shp')
        area_shp = os.path.join(nhd_path, dir, 'Shape', 'NHDArea.shp')
        wbody_shp = os.path.join(nhd_path, dir, 'Shape', 'NHDWaterbody.shp')
        wbd_shp = huc_wbd

        # include only streams and canals
        quer = """ "FTYPE" = 428 OR "FTYPE" = 420 OR "FTYPE" = 566 """
        arcpy.SelectLayerByAttribute_management(flowline_shp, 'NEW_SELECTION', quer)
        arcpy.SelectLayerByAttribute_management('tmp_huc8_flowlines_lyr', 'SWITCH_SELECTION')
        huc8_flowlines = arcpy.CopyFeatures_management('tmp_huc8_flowlines_lyr', os.path.join(nhd_folder, 'NHDFlowline.shp'))        

        # reproject data and save to HUC8 directory within project folder
        if not os.path.exists(os.path.join(huc_folder, 'NHD')):
            os.mkdir(os.path.join(huc_folder, 'NHD'))
            arcpy.Project_management(flowline_shp, os.path.join(huc_folder, 'NHD', 'NHDFlowline.shp'), outCS)
            arcpy.Project_management(area_shp, os.path.join(huc_folder, 'NHD', 'NHDArea.shp'), outCS)
            arcpy.Project_management(wbody_shp, os.path.join(huc_folder, 'NHD', 'NHDWaterbody.shp'), outCS)
            arcpy.Project_management(wbd_shp, os.path.join(huc_folder, 'NHD', 'WBDHU8.shp'), outCS)

        
if __name__ == "__main__":
    main()
