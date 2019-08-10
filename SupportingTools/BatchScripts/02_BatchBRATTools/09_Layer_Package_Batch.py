#----------------------------------------------------------------------------------------------------------------------------
# Name: Layer Package (Batch)
#
# Purpose: Runs Layer Package Generator (Standalone) tool for multiple HUC8s
#
# Notes:       - The scripts assumes data are in standard BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) BRAT table output is located in standard location within basin run folder
#                   If inputs are named otherwise, the code will need to be slightly modified to
#                   find the proper files. All basin inputs should have the same name.
#               - The script will execute on all subfolders in the parent folder EXCEPT
#                 those that start with a '00_*' (e.g., '00_Projectwide')
#
# Date: March 2019
# Author: Sara Bangen (sara.bangen@gmail.com)
#----------------------------------------------------------------------------------------------------------------------------

# user defined arguments:

# pf_path - path to project folder set up in standard BRAT format
# run_folder - name of the folder that will serve as the BRAT project folder
#               containing this run (will be created in each basin subdirectory
#               if it does not already exist)
# overwrite_run - True/False for whether to overwrite the run_folder if it already
#                   contains data
# mxd_path - empty ArcMap document that will be used to generate layer packages
# lpg_path - folder path holding the Layer_Package_Generator_standalone tool script

pf_path = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data'
run_folder = 'BatchRun_03'
overwrite_run = False
mxd_path = 'C:/Users/ETAL/Desktop/lpk.mxd'
lpg_path = 'C:/Users/ETAL/Desktop/pyBRAT/SupportingTools/BatchScripts/02_BatchBRATTools'


#  import required modules and extensions
import os
import sys
import arcpy
import glob

arcpy.CheckOutExtension('Spatial')
sys.path.append(lpg_path)
from Layer_Package_Generator_Standalone import main as lyrpkg


# function check is there are any layer file with spaces in the filename
# if there are, delete them before running the layer package generator
# since filenames with spaces will throw an error and crash tool
def check_lyr_names(proj_path):
    print "Checking for spaces in layer file paths..."
    problem_lyrs = []
    walk = arcpy.da.Walk(proj_path, datatype = "Layer")
    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            if " " in filename:
                problem_lyrs.append(os.path.join(dirpath, filename))
    if len(problem_lyrs) > 0:
        print "Deleting layer file(s) with spaces in path..."
        for problem_lyr in problem_lyrs:
            os.remove(problem_lyr)


def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)[0]
    else:
        file_path = None

    return file_path


def main(overwrite = overwrite_run):

    # change directory to the parent folder path
    os.chdir(pf_path)
    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # run function for each huc8 folder
    for dir in dir_list:
        print dir
       
        # define inputs
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        output_folder = os.path.join(proj_path, 'Outputs', 'Output_01')
        layer_package_name = 'BRAT_' + dir
        layer_package_path = os.path.join(output_folder, layer_package_name + ".lpk")
        clipping_network_path = os.path.join(pf_path, dir, 'NHD', 'NHD_24k_Perennial_CanalsDitches.shp')

        # use clipping network if present
        if os.path.exists(clipping_network_path):
            print 'Clipping network exists'
            clipping_network = clipping_network_path
            layer_package_name = 'BRAT_' + dir + '_Perennial'
        else:
            clipping_network = None
            
        # should include check for whether layer package already exists or not plus whether overwrite is True
        #if not os.path.exists(layer_package_path) or overwrite is True:
        if not os.path.exists(layer_package_path) or overwrite is True:
                try:
                    check_lyr_names(proj_path)
                    print "Generating layer package for " + dir
                    lyrpkg(output_folder, layer_package_name, mxd_path, clipping_network_path)
                    print ".....Deleting clipped files for " + dir
                    network_clip = find_file(proj_path, 'Inputs/*[0-9]*_Network/Network_01/NHD_24k_300mReaches_clipped.shp')
                    buffer_100m = os.path.join(output_folder, '01_Intermediates/01_Buffers/buffer_30m_clipped.shp')
                    buffer_30m = os.path.join(output_folder, '01_Intermediates/01_Buffers/buffer_100m_clipped.shp')

                except Exception as err:
                    print "Error with " + dir + ". The exception thrown was:"
                    print err
        else:
            print "Layer package already exists.  Skipping " + dir


if __name__ == '__main__':
    main()
