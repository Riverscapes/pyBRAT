#----------------------------------------------------------------------------------------------------------------------------
# Name: iHyd (Batch)
#
# Purpose: Runs iHyd tool for multiple HUC8s
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
#                       - RegionCode -- must match regions available in iHyd code
#                       - BASIN_RELIEF -- basin relief (in feet) - max basin elevation minus min basin elevation
#                       - ELEV_FT -- mean basin elevation (in feet)
#                       - SLOPE_PCT_30 -- percent of basin area with slopes greater than 30 degrees (integer)
#                       - PRECIP_IN -- mean basin precipitation (in inches)
#                       - MIN_ELEV_FT -- minimum basin elevation (in feet)
#                       - FOREST_PCT -- percent of basin area with forested landcover (integer)
#                       - FOREST_PLUS_PCT -- FOREST_PCT + 1%
#                       - BASIN_SLOPE_PCT -- mean basin slope (in percent slope)
#                       - SLOPE_PCT_50 -- percent of basin area with slopes greater than 50% (integer)
#               - This tool is based off the flow equations in the iHyd_Idaho script under Batch Scripts
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
# ihyd_script_path - folder path holding the iHyd script
# ihyd_csv_path - CSV file holding basin parameters

pf_path = r'C:\Users\ETAL\Desktop\GYE_BRAT\wrk_Data'
run_folder = 'BatchRun_01'
overwrite_run = False
ihyd_script_path = 'C:/Users/ETAL/Desktop/pyBRAT/SupportingTools/BatchScripts/02_BatchBRATTools'
ihyd_csv_path = r"C:\Users\ETAL\Desktop\GYE_BRAT\wrk_Data\00_Projectwide\ModelParameters\GYE_BRAT_iHyd_Parameters.csv"

#  import required modules and extensions
import os
import sys
import arcpy
import glob
import shutil
import csv
from collections import defaultdict

arcpy.CheckOutExtension('Spatial')
sys.path.append(ihyd_script_path)
from iHyd import main as iHyd


def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)[0]
    else:
        file_path = None

    return file_path


def main(overwrite = overwrite_run):

    arcpy.env.overwriteOutput = True  # set to overwrite output

    # change directory to the parent folder path
    os.chdir(pf_path)

    # read in csv of width parameters and convert to python dictionary
    paramDict = defaultdict(dict)
    with open(ihyd_csv_path, "rb") as infile:
        reader = csv.reader(infile)
        headers = next(reader)[1:]
        for row in reader:
            paramDict[row[0]] = {key: value for key, value in zip(headers, row[1:])}

    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # run function for each huc8 folder
    for dir in dir_list:
        
        # identify basin run folder and BRAT table output
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        brat_table = os.path.join(proj_path, 'Outputs/Output_01/01_Intermediates/BRAT_Table.shp')

        # proceed only if BRAT table output exists
        if os.path.exists(brat_table):
            
            # check if iHyd has already been run by searching for 'BaseflowStreamPower.lyr'
            ihyd_lyr = find_file(output_folder, '01_Intermediates/*[0-9]*_Hydrology/BaseflowStreamPower.lyr')

            # if 'BaseflowStreamPower.lyr' exists and overwrite is set to True delete the layer and existing Hydrology folder
            # prevents ending up with multiple Hydrology folders
            if ihyd_lyr is not None and overwrite is True:
                ihyd_dir = os.path.dirname(ihyd_lyr)
                shutil.rmtree(ihyd_dir)

            # if 'BaseflowStreamPower.lyr' doesn't exist or overwrite is set to true, run iHyd script
            if ihyd_lyr is None or overwrite is True:

                if dir in paramDict:
                    # make subdictionary with directory's values
                    subDict = {k: v for k, v in paramDict.iteritems() if dir in k}
                    print "Running iHyd for " + dir
                    try:
                        # find basin parameters in subdirectory
                        region = int(subDict[dir]['RegionCode'])
                        basin_relief = int(subDict[dir]['BASIN_RELIEF'])
                        basin_elev = float(subDict[dir]['ELEV_FT'])
                        basin_slope_thirty = float(subDict[dir]['SLOPE_PCT_30'])
                        basin_precip = float(subDict[dir]['PRECIP_IN'])
                        basin_min_elev = float(subDict[dir]['MIN_ELEV_FT'])
                        basin_forest = float(subDict[dir]['FOREST_PCT'])
                        basin_forest_plus = float(subDict[dir]['FOREST_PLUS_PCT'])
                        basin_slope = float(subDict[dir]['BASIN_SLOPE_PCT'])
                        basin_slope_fifty = float(subDict[dir]['SLOPE_PCT_50'])
                        # run iHyd for basin
                        iHyd(brat_table, region, basin_relief, basin_elev, basin_slope_thirty, basin_precip, basin_min_elev, basin_forest, basin_forest_plus, basin_slope, basin_slope_fifty, None, None)
                    except Exception as err:
                         print 'WARNING: iHyd tool failed for ' + dir + '. Exception thrown was:'
                         print err

            else:

                print "SKIPPING " + dir + "- iHyd has already been run."

        else:
            print "WARNING: Script cannot be run for " + dir + ".  BRAT table doesn't exist."


if __name__ == "__main__":
    main()
