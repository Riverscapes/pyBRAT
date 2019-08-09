#-------------------------------------------------------------------------------------
# Name: Segmenting Network (Batch)
#
# Purpose: Segment network for each HUC8 watershed in a batch processed project
#
# Date: March 2019
# Author: Maggie Hallerud (maggie.hallerud@aggiemail.usu.edu)
#-------------------------------------------------------------------------------------


# user defined inputs
# supportingTools - path to pyBRAT supporting tools folder
# pf_path - project folder for batch processing
supportingTools = 'C:/Users/ETAL/Desktop/pyBRAT/SupportingTools' 
pf_path = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data'


# load dependencies
import os
import sys
sys.path.append(supportingTools)
from segmentNetwork import main as segmentNetwork


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
        out_path = os.path.join(pf_path, dir, 'NHD/NHD_24k_300mReaches')
        if not os.path.exists(out_path):
            try:
                segmentNetwork(nhd_flowline_path, outpath)
            except Exception as err:
                print "Segmenting network failed for watershed " + dir + ". The exception thrown was:"
                print err
            
            
if __name__ == '__main__':
    main()
