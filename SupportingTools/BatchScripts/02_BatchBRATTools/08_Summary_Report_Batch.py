#----------------------------------------------------------------------------------------------------------------------------
# Name: Collect Summary Reports (Batch)
#
# Purpose: Runs Data Capture Validation tool for multiple HUC8s
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
# Author: Maggie Hallerud (maggie.hallerud@aggiemail.usu.edu)
#----------------------------------------------------------------------------------------------------------------------------

# user defined arguments:

# pf_path - path to project folder set up in standard BRAT format
# run_folder - name of the folder that will serve as the BRAT project folder
#               containing this run (will be created in each basin subdirectory
#               if it does not already exist)
# overwrite_run - True/False for whether to overwrite the run_folder if it already
#                   contains data
# pybrat_path - folder path holding the BRAT tool scripts

pf_path = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data'
run_folder = 'BatchRun_01'
overwrite_run = False
pybrat_path = 'C:/Users/ETAL/Desktop/pyBRAT'


#  import required modules and extensions
import sys
import os
sys.path.append(pybrat_path)
from Collect_Summary_Products import main as summary


def main(overwrite = overwrite_run):

    # change directory to the parent folder path
    os.chdir(pf_path)
    
    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    for dir in dir_list:
        # find basin run folder and validation file
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        validation = os.path.join(proj_path, 'Outputs/Output_01/02_Analyses/Data_Capture_Validation.shp')

        if os.path.exists(validation):

            # define ouput file name with HUC name
            huc_name = dir.split('_')[0]
            out_name= huc_name + '_SummaryTables'
            out_path = os.path.join(proj_path, 'SummaryProducts/SummaryTables', out_name + '.xlsx')

            # only run if output path doesn't exist or overwrite is True
            if not os.path.exists(out_path) or overwrite is True:

                # find dams in inputs if present
                dams = find_file(proj_path, 'Inputs/*[0-9]*_BeaverDams/Beaver_Dam_01/*.shp')
                if len(dams > 0):
                    dams_shp = dams
                else:
                    dams_shp = None
                
                # run summary report
                print 'Running summary report for ' + dir
                try:
                    summary(proj_path, validation, dir, out_name, dams_shp, None)          
                except Exception as err:
                    print "WARNING: Validation tool failed for " + dir + ". Exception thrown was:"
                    print err
            else:
                print "SKIPPING " + dir + " - Summary report already completed."
                    
        else:
            print 'SKIPPING ' + dir + "- Validation file could not be found."


def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)
    else:
        file_path = None

    return file_path
if __name__ == "__main__":
    main()
