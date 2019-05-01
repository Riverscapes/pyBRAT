################################################################################
# Name: 03_SegmentingNetwork_Batch
# Purpose: Segment network for each HUC8 watershed in a batch processed project
# Author: Maggie Hallerud
################################################################################

# give project folder and supporting tools folder
supportingTools = 'C:/Users/Maggie/Desktop/pyBRAT/SupportingTools'
pf_path = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/new'

# load dependencies
import os
import sys
import arcpy
sys.path.append(supportingTools)
import segmentNetwork

def main():
    os.chdir(pf_path)

    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # loop through each HUC8 folder, segment network, and save as new shapefile
    for dir in dir_list:
        print "Segmenting network for " + dir
        nhd_flowline_path = os.path.join(pf_path, dir, 'NHD/NHDFlowline.shp')
        out_path = os.path.join(pf_path, dir, 'NHD/NHD_24k_300mReaches.shp')
        if os.path.exists(out_path):
            arcpy.Delete_management(out_path)
        else:
            pass

        try:
            segmentNetwork.main(nhd_flowline_path, out_path)
        except Exception as err:
            print "Segmenting network failed for watershed " + dir + ". The exception thrown was:"
            print err
            
            
if __name__ == '__main__':
    main()
    
