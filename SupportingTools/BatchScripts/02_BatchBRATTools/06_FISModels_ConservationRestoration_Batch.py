#----------------------------------------------------------------------------------------------------------------------------
# Name: FIS Models & Conservation Restoration Model (Batch)
#
# Purpose: Runs Vegetation Capacity Model, Combined Capacity Model, and Conservation Restoration
#           Model for multiple HUC8s
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
# Author: Sara Bangen (sara.bangen@gmail.com)
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

pf_path = r'C:\Users\ETAL\Desktop\GYE_BRAT\wrk_Data'
run_folder = 'BatchRun_01'
overwrite_run = False
pybrat_path = 'C:/Users/ETAL/Desktop/pyBRAT'
da_thresholds_csv = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/ModelParameters/GYE_DA_Thresholds.csv'


#  import required modules and extensions
import os
import sys
import arcpy
import glob
import shutil
import csv
from collections import defaultdict

arcpy.CheckOutExtension('Spatial')
sys.path.append(pybrat_path)
from Veg_FIS import main as veg_fis
from Comb_FIS import main as comb_fis
from Conservation_Restoration import main as cons_rest


def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)
    else:
        file_path = None

    return file_path


def main(overwrite = overwrite_run):

    arcpy.env.overwriteOutput = True  # set to overwrite output

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
    with open(da_thresholds_csv, "rb") as infile:
        reader = csv.reader(infile)
        headers = next(reader)[1:]
        for row in reader:
            paramDict[row[0]] = {key: value for key, value in zip(headers, row[1:])}

    # run function for each basin
    for dir in dir_list:
        
        # define basin project path, BRAT table, and combined capacity output
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        brat_table = os.path.join(proj_path, 'Outputs/Output_01/01_Intermediates/BRAT_Table.shp')
        combined_capacity = os.path.join(proj_path, 'Outputs/Output_01/02_Analyses/Combined_Capacity_Model.shp')

        if os.path.exists(brat_table):
           
            # check if veg capacity model has already been run by searching for 'VegDamCapacity' folder
            # if directory doesn't exist or overwrite is set to true, run vegetation capacity model script
            veg_dirs = find_file(proj_path, 'Outputs/Output_01/01_Intermediates/*[0-9]*_VegDamCapacity')

            if veg_dirs is not None and overwrite is True:
                for veg_dir in veg_dirs:
                    shutil.rmtree(veg_dir)
                    
            # try running Veg FIS for basin
            if veg_dirs is None or overwrite is True:
                try:
                    print "Running vegetation capacity models for " + dir
                    veg_fis(brat_table)
                except Exception as err:
                    print 'WARNING: Vegetation capacity model failed for ' + dir + '. Exception thrown was:'
                    print err
            else:

                print "SKIPPING " + dir + "- Vegetation capacity models have already been run."
            
            
            # check if combined capacity model has already been run by searching for 'Capacity' folder
            # if directory doesn't exist or overwrite is set to true, run combined capacity model script
            capacity_dirs = find_file(proj_path, 'Outputs/Output_01/02_Analyses/*[0-9]*_Capacity')

            if capacity_dirs is not None and overwrite is True:
                for capacity_dir in capacity_dirs:
                    shutil.rmtree(capacity_dir)

            # try running Comb FIS
            if capacity_dirs is None or overwrite is True:
                
                try:
                    if dir in paramDict:
                        # find basin's DA threshold from input CSV
                        subDict = {k: v for k, v in paramDict.iteritems() if dir in k}
                        huc_threshold = float(subDict[dir]['DA_Threshold'])
                        # if DA threshold exists, run combined capacity model, else skip
                        if huc_threshold > 0:
                            print "Running combined capacity model for " + dir
                            comb_fis(proj_path, brat_table, huc_threshold, "Combined_Capacity_Model")
                        else:
                            print 'SKIPPING ' + dir + '- No DA threshold for combined capacity model.'
                except Exception as err:
                    print 'WARNING: Combined capacity model failed for ' + dir + '. Exception thrown was:'
                    print err

            else:
                print "SKIPPING " + dir + "- Combined capacity models have already been run."
            
            
            # check if management model has already been run by searching for 'Management' folder
            # if directory doesn't exist or overwrite is set to true, run combined capacity model script
            mgmt_dirs = find_file(proj_path, 'Outputs/Output_01/02_Analyses/*[0-9]*_Management')

            if mgmt_dirs is not None and overwrite is True:
                for mgmt_dir in mgmt_dirs:
                    shutil.rmtree(mgmt_dir)

            if mgmt_dirs is None or overwrite is True:
                try:
                    print "Running conservation restoration model for " + dir
                    cons_rest(proj_path, combined_capacity, "Conservation_Restoration_Model")
                except Exception as err:
                    print 'WARNING: Conservation restoration model failed for ' + dir + '. Exception thrown was:'
                    print err
            else:

                print "SKIPPING " + dir + "- Conservation restoration model has already been run."

        else:
            print "WARNING: Script cannot be run for " + dir + ".  BRAT table doesn't exist."


if __name__ == "__main__":
    main()
