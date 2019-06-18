#  define parent folder path and run folder name for directory search
pf_path = r'C:\Users\a02046349\Desktop\GYE_BRAT\wrk_Data'
run_folder = 'BatchRun_02'
overwrite_run = False
da_thresholds_csv = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/ModelParameters/GYE_DA_Thresholds.csv'
fix_list = ['YellowstoneHeadwaters_10070001']

#  import required modules and extensions
import os
import sys
import arcpy
import glob
import shutil
import csv
from collections import defaultdict

arcpy.CheckOutExtension('Spatial')
sys.path.append('C:/Users/a02046349/Desktop/pyBRAT')
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

    # run function for each huc8 folder
    for dir in fix_list:

        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        brat_table = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01/01_Intermediates/BRAT_Table.shp')
        combined_capacity = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01/02_Analyses/Combined_Capacity_Model.shp')

        if os.path.exists(brat_table):
            """
            # check if veg capacity model has already been run by searching for 'VegDamCapacity' folder
            # if directory doesn't exist or overwrite is set to true, run vegetation capacity model script
            veg_dirs = find_file(proj_path, 'Outputs/Output_01/01_Intermediates/*[0-9]*_VegDamCapacity')

            if veg_dirs is not None and overwrite is True:
                for veg_dir in veg_dirs:
                    shutil.rmtree(veg_dir)

            if veg_dirs is None or overwrite is True:

                print "Running vegetation capacity models for " + dir

                try:
                    veg_fis(brat_table)
                except Exception as err:
                    print 'Vegetation capacity model failed for ' + dir + '. Exception thrown was:'
                    print err
            else:

                print "Vegetation capacity models have already been run.  Skipping " + dir
            
            """
            # check if combined capacity model has already been run by searching for 'Capacity' folder
            # if directory doesn't exist or overwrite is set to true, run combined capacity model script
            capacity_dirs = find_file(proj_path, 'Outputs/Output_01/02_Analyses/*[0-9]*_Capacity')

            if capacity_dirs is not None and overwrite is True:
                for capacity_dir in capacity_dirs:
                    shutil.rmtree(capacity_dir)

            if capacity_dirs is None or overwrite is True:

                print "Running combined capacity models for " + dir

                try:
                    if dir in paramDict:
                        subDict = {k: v for k, v in paramDict.iteritems() if dir in k}
                        huc_threshold = float(subDict[dir]['DA_Threshold'])
                        if huc_threshold > 0:
                            comb_fis(proj_path, brat_table, huc_threshold, "Combined_Capacity_Model")
                        else:
                            print 'Skipping ' + dir + ': No DA threshold.'
                    else:
                        comb_fis(proj_path, brat_table, 1000.0, "Combined_Capacity_Model")
                except Exception as err:
                    print 'Combined capacity model failed for ' + dir + '. Exception thrown was:'
                    print err

            else:
                print "Combined capacity models have already been run.  Skipping " + dir
            
            
            # check if management model has already been run by searching for 'Management' folder
            # if directory doesn't exist or overwrite is set to true, run combined capacity model script
            mgmt_dirs = find_file(proj_path, 'Outputs/Output_01/02_Analyses/*[0-9]*_Management')

            if mgmt_dirs is not None and overwrite is True:
                for mgmt_dir in mgmt_dirs:
                    shutil.rmtree(mgmt_dir)

            if mgmt_dirs is None or overwrite is True:

                print "Running conservation restoration model for " + dir

                try:
                    cons_rest(proj_path, combined_capacity, "Conservation_Restoration_Model")
                except Exception as err:
                    print 'Combined capacity model failed for ' + dir + '. Exception thrown was:'
                    print err
            else:

                print "Conservation restoration model has already been run.  Skipping " + dir

        else:
            print "WARNING: Script cannot be run.  BRAT table doesn't exist for " + dir


if __name__ == "__main__":
    main()
