# set parameters
pf_path = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data'
da_threshold_csv = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/ModelParameters/GYE_DA_Thresholds.csv'
run_folder = 'BatchRun_02'
out_name = 'Data_Capture_Validation'
overwrite_run = True
fix_list = ['YellowstoneHeadwaters_10070001']
gye_dams = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/YellowstoneHeadwaters_10070001/BRAT/BatchRun_01/Inputs/06_BeaverDams/Beaver_Dam_01/Yellowstone_Headwaters_Dams.shp'
# load dependencies
import sys
import os
import shutil
import glob
import csv
from collections import defaultdict

sys.path.append('C:/Users/a02046349/Desktop/pyBRAT')
from Data_Capture_Validation import main as validation

def main(overwrite=overwrite_run):

    os.chdir(pf_path)

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

    for dir in fix_list:
        # only try running if conservation restoration network exists
        cons_rest = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01/02_Analyses/Conservation_Restoration_Model.shp')
        if os.path.exists(cons_rest):
            """# find dams file and throw warning if it doesn't exist
            dams = os.path.join(pf_path, dir, 'Beaver_Dams/Idaho_' + dir + '_BeaverDams.shp')
            if not os.path.exists(dams):
                dams = None
                print "WARNING: Running validation without dams for " + dir
            """
            
            # check for and delete old validation layers if they exist and overwrite is True
            proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
            valid_dirs = find_file(proj_path, 'Outputs/Output_01/02_Analyses/*[0-9]*_Validation')
            if valid_dirs is not None and overwrite is True:
                for valid_dir in valid_dirs:
                    shutil.rmtree(valid_dir)

            # try running tool
            if valid_dirs is None or overwrite is True:
                print 'Running validation tool for ' + dir
                try:
                    # pull drainage area threshold from CSV
                    if dir in paramDict:
                        subDict = {k: v for k, v in paramDict.iteritems() if dir in k}
                        huc_threshold = float(subDict[dir]['HUC8Dir'])
                        if huc_threshold > 0:
                            validation(cons_rest, gye_dams, out_name, huc_threshold)
                        else:
                            print 'Skipping ' + dir + ': No DA threshold.'
                except Exception as err:
                    print "Validation tool failed for " + dir + ". Exception thrown was:"
                    print err
                    
        else:
            print "ERROR: Tool not run for " + dir + "because no conservation restoration model"



def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)
    else:
        file_path = None

    return file_path




if __name__ == "__main__":
    main()
