#  define parent folder path and run folder name for directory search
pf_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_CodeTest\StratMap'
mxd_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_PriorityRuns\lpk.mxd"
run_folder = 'BatchRun_02'
overwrite_run = False

#  import required modules and extensions
import os
import sys
import arcpy

arcpy.CheckOutExtension('Spatial')
sys.path.append('C:/etal/LocalCode/pyBRAT/TNC_Changes')
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

        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        output_folder = os.path.join(proj_path, 'Outputs', 'Output_01')
        layer_package_name = 'BRAT_' + dir
        layer_package_path = os.path.join(output_folder, layer_package_name + ".lpk")
        clipping_network_path = os.path.join(pf_path, dir, 'NHD', 'NHD_24k_Perennial_CanalsDitches.shp')
        if os.path.exists(clipping_network_path):
            print 'Clipping network exists'
            clipping_network = clipping_network_path
        else:
            clipping_network = None

        # should include check for whether layer package already exists or not plus whether overwrite is True
        if not os.path.exists(layer_package_path) or overwrite is True:

            try:
                check_lyr_names(proj_path)
                print "Generating layer package for " + dir
                lyrpkg(output_folder, layer_package_name, mxd_path, clipping_network)
            except Exception as err:
                print "Error with " + dir + ". The exception thrown was:"
                print err
        else:
            print "Layer package already exists.  Skipping " + dir



if __name__ == '__main__':
    main()
