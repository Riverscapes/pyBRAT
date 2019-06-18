#  define parent folder path and run folder name for directory search
pf_path = 'C:/Users/a02046349/Desktop/Idaho_BRAT/wrk_Data'
mxd_path = 'C:/Users/a02046349/Desktop/lpk.mxd'
run_folder = 'BatchRun_01'
overwrite_run = False
fix_list = ['Yaak_17010103']

#  import required modules and extensions
import os
import sys
import arcpy
import glob

arcpy.CheckOutExtension('Spatial')
sys.path.append('C:/Users/a02046349/Desktop/pyBRAT')
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
    for dir in fix_list:
        print dir
        
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        output_folder = os.path.join(proj_path, 'Outputs', 'Output_01')
        layer_package_name = 'BRAT_' + dir
        layer_package_path = os.path.join(output_folder, layer_package_name + ".lpk")
        clipping_network_path = os.path.join(pf_path, dir, 'NHD', 'NHD_24k_Perennial_CanalsDitches.shp')
        if os.path.exists(clipping_network_path):
            print 'Clipping network exists'
            clipping_network = clipping_network_path
            layer_package_name = 'BRAT_' + dir + '_Perennial'
        else:
            clipping_network = None

        veg = os.path.join(proj_path, 'Inputs/01_Vegetation/01_ExistingVegetation/Ex_Veg_01/LANDFIRE_200EVT.tif')
        if os.path.exists(veg):
            LANDFIRE_2016 = True
        else:
            LANDFIRE_2016 = False
            
        # should include check for whether layer package already exists or not plus whether overwrite is True
        #if not os.path.exists(layer_package_path) or overwrite is True:
        if not os.path.exists(layer_package_path):
                try:
                    check_lyr_names(proj_path)
                    print "Generating layer package for " + dir
                    lyrpkg(output_folder, layer_package_name, mxd_path, clipping_network_path, LANDFIRE_2016)
                    print ".....Deleting clipped files for " + dir
                    network_clip = find_file(proj_path, 'Inputs/*[0-9]*_Network/Network_01/NHD_24k_300mReaches_clipped.shp')
                    brat_table_clip = os.path.join(proj_path, 'Outputs/Output_01/01_Intermediates/BRAT_Table_clipped.shp')
                    cons_rest_clip = os.path.join(proj_path, 'Outputs/Output_01/02_Analyses/Conservation_Restoration_Model_clipped.shp')
                    valid_clip = os.path.join(proj_path, 'Outputs/Output_01/02_Analyses/Data_Capture_Validation_clipped.shp')
                    clip_files = [network_clip, brat_table_clip, cons_rest_clip, valid_clip]
                    for file in clip_files:
                        if os.path.exists(file):
                            arcpy.Delete_management(file)

                except Exception as err:
                    print "Error with " + dir + ". The exception thrown was:"
                    print err
        else:
            print "Waiting to fix veg layers"
            #print "Layer package already exists.  Skipping " + dir




if __name__ == '__main__':
    main()
