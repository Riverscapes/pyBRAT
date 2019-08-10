#----------------------------------------------------------------------------------------------------------------------------
# Name: Data Capture Validation (Batch)
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
#               - The tool expects an input CSV with the following columns and calculated values for each basin:
#                       - HUC8Dir -- must match basin sub-directory exactly (e.g., BigChicoCreekSacramentoRiver_18020157)
#                       - DA_Threshold -- values corresponding to the drainage area thresholds used in the Combined FIS (see website - http://brat.riverscapes.xyz/Documentation/Tutorials/7-BRATCombinedFIS.html)
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
# da_thresholds_csv - CSV file holding basin drainage area thresholds
# check_dams_snapped - True/False for whether to check if dams snapped to network and were used in validation

pf_path = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data'
run_folder = 'BatchRun_01'
overwrite_run = False
pybrat_path = 'C:/Users/ETAL/Desktop/pyBRAT'
da_threshold_csv = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/ModelParameters/GYE_DA_Thresholds.csv'
check_dams_snapped = False


# load dependencies
import sys
import os
import shutil
import glob
import csv
from collections import defaultdict

sys.path.append(pybrat_path)
from Data_Capture_Validation import main as validation


def main(overwrite=overwrite_run):

    # change directory to the parent folder path
    os.chdir(pf_path)

    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # read in csv of width parameters and convert to python dictionary
    paramDict = defaultdict(dict)
    with open(da_threshold_csv, "rb") as infile:
        reader = csv.reader(infile)
        headers = next(reader)[:1]
        for row in reader:
            paramDict[row[0]] = {key: value for key, value in zip(headers, row[1:])}

    # run function for each basin
    for dir in dir_list:

        # define basin run folder and basin output folder
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        output_folder = os.path.join(proj_path, 'Outputs/Output_01')
        
        # only try running if conservation restoration network exists
        cons_rest = os.path.join(output_folder, '02_Analyses/Conservation_Restoration_Model.shp')
        if os.path.exists(cons_rest):
            # find dams file and throw warning if it doesn't exist
            dams = os.path.join(pf_path, dir, 'Beaver_Dams/SurveyedDams.shp')
            if not os.path.exists(dams):
                dams = None
            
            # check for and delete old validation layers if they exist and overwrite is True
            valid_dirs = find_file(output_folder, '02_Analyses/*[0-9]*_Validation')
            if valid_dirs is not None and overwrite is True:
                for valid_dir in valid_dirs:
                    shutil.rmtree(valid_dir)

            # try running tool if validation layers don't exist or overwrite is True
            if valid_dirs is None or overwrite is True:
                print 'Running validation tool for ' + dir
                try:
                    # pull drainage area threshold from CSV
                    if dams is not None:
                        if dir in paramDict:
                            # find basin's DA threshold from input CSV
                            subDict = {k: v for k, v in paramDict.iteritems() if dir in k}
                            huc_threshold = float(subDict[dir]['HUC8Dir'])
                            if huc_threshold > 0:
                                validation(cons_rest, 'Data_Capture_Validation', dams, huc_threshold)
                            else:
                                print '........WARNING: Running validation without DA threshold.'
                                validation(cons_rest, 'Data_Capture_Validation', dams, None)
                        # check that dams snapped to network and 'Snapped' field added
                        if check_dams_snapped:
                            try:
                                print '........Checking that dams snapped'
                                dam_folders = find_file(proj_path, 'Inputs/*[0-9]*_BeaverDams/Beaver_Dam_01/Idaho_'+dir+'_BeaverDams.shp')
                                if dam_folders:
                                    print '........     ' + str(len(dam_folders)) + ' input dam folder(s)' 
                                    for f in dam_folders:
                                        print '........     Checking ' + os.path.basename(os.path.dirname(f))
                                        dam_fields = [f.name for f in arcpy.ListFields(dam_input)]
                                        if 'Snapped' not in dam_fields:
                                            print '........WARNING: Dams not snapped to network. Consider re-running data capture validation for this basin."
                            except Exception as err:
                                print "........WARNING: Checking dams snapped failed for " + dir ". Consider checking manually."
                                        
                except Exception as err:
                    print 'WARNING: Data capture validation failed for ' + dir + '. Exception thrown was:' 
                    print err
                
            else:
                print 'SKIPPING ' + dir +'- Validation already completed.'     

        else:
            print "WARNING: Script cannot be run for " + dir + ". Conservation restoration model does not exist."



def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)
    else:
        file_path = None

    return file_path




if __name__ == "__main__":
    main()
