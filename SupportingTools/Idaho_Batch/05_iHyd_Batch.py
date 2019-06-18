#  define parent folder path and run folder name for directory search
pf_path = r'C:\Users\a02046349\Desktop\Idaho_BRAT\wrk_Data\00_VBET_Missing'
run_folder = 'BatchRun_01'
overwrite_run = True
ihyd_csv_path = r"C:\Users\a02046349\Desktop\Idaho_BRAT\wrk_Data\00_Projectwide\ModelParameters\Idaho_BRAT_iHyd Parameters.csv"

#  import required modules and extensions
import os
import sys
import arcpy
import glob
import shutil
import csv
from collections import defaultdict

arcpy.CheckOutExtension('Spatial')
sys.path.append('C:/Users/a02046349/Desktop/Idaho_Batch')
from iHyd_Idaho import main as iHyd


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
    for dir in dir_list[1:]:

        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        brat_table = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01/01_Intermediates/BRAT_Table.shp')

        if os.path.exists(brat_table):

            # check if iHyd has already been run by searching for 'BaseflowStreamPower.lyr'
            ihyd_lyr = find_file(proj_path, 'Outputs/Output_01/01_Intermediates/*[0-9]*_Hydrology/BaseflowStreamPower.lyr')

            # if 'BaseflowStreamPower.lyr' exists and overwrite is set to True delete the layer and existing Hydrology folder
            # prevents ending up with multiple Hydrology folders
            if ihyd_lyr is not None and overwrite is True:
                ihyd_dir = os.path.dirname(ihyd_lyr)
                shutil.rmtree(ihyd_dir)

            # if 'BaseflowStreamPower.lyr' doesn't exist or overwrite is set to true, run iHyd script
            if ihyd_lyr is None or overwrite is True:

                if dir in paramDict:
                    subDict = {k: v for k, v in paramDict.iteritems() if dir in k}
                    print "Running iHyd for " + dir
                    try:
                        region = int(subDict[dir]['RegionCode'])
                        basin_relief = int(subDict[dir]['BASIN_RELIEF'])
                        basin_elev = float(subDict[dir]['ELEV_FT'])
                        basin_slope_thirty = float(subDict[dir]['SLOPE_PCT'])
                        basin_precip = float(subDict[dir]['PRECIP_IN'])
                        basin_min_elev = float(subDict[dir]['MIN_ELEV_FT'])
                        basin_forest = float(subDict[dir]['FOREST_PCT'])
                        basin_forest_plus = float(subDict[dir]['FOREST_PLUS_PCT'])
                        basin_slope = float(subDict[dir]['BASIN_SLOPE'])
                        iHyd(brat_table, region, basin_relief, basin_elev, basin_slope_thirty, basin_precip, basin_min_elev, basin_forest, basin_forest_plus, basin_slope, None, None)
                    except Exception as err:
                        print 'iHyd check failed for ' + dir + '. Exception thrown was:'
                        print err
                else:
                    print "Parameters for this basin are not in the input csv.  Skipping " + dir

            else:

                print "iHyd has already been run.  Skipping " + dir

        else:
            print "WARNING: Script cannot be run.  BRAT table doesn't exist for " + dir


if __name__ == "__main__":
    main()
