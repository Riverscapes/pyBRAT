#  define parent folder path and run folder name for directory search
pf_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_CodeTest\iHyd'
run_folder = 'BatchRun_02'
overwrite_run = True

#  import required modules and extensions
import os
import sys
import arcpy
import glob
import shutil

arcpy.CheckOutExtension('Spatial')
sys.path.append('C:/etal/LocalCode/pyBRAT/TNC_Changes')
from Veg_FIS import main as veg_fis
from Comb_FIS import main as comb_fis
from Conservation_Restoration import main as cons_rest


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

    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # run function for each huc8 folder
    for dir in dir_list:

        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        brat_table = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01/01_Intermediates/BRAT_Table.shp')
        combined_capacity = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01/02_Analyses/Combined_Capacity_Model.shp')

        if os.path.exists(brat_table):
            # check if update drainage area has already been run by searching for 'Orig_DA' field
            # if 'Orig_DA' not in brat table fields or overwrite is set to true, run update drainage area script
            fields = [f.name for f in arcpy.ListFields(brat_table)]

            if overwrite is True:

                print "Running FIS models for " + dir

                try:
                    veg_fis(brat_table)
                except Exception as err:
                    print 'Vegetation model failed for ' + dir + '. Exception thrown was:'
                    print err

                try:
                    comb_fis(proj_path, brat_table, 500.0, "Combined_Capacity_Model")
                except Exception as err:
                    print 'Combined capacity model failed for ' + dir + '. Exception thrown was:'
                    print err

                try:
                    cons_rest(proj_path, combined_capacity, "Conservation_Restoration_Model")
                except Exception as err:
                    print 'Combined capacity model failed for ' + dir + '. Exception thrown was:'
                    print err

            # else:
            #
            #     print "DA values have already been updated.  Skipping " + dir
                
            # # check if braid handler has already been run by searching for 'AnabranchTypes.lyr'
            # # if layer doesn't exist or overwrite is set to true, run update braid handler script
            # anabranch_lyr = find_file(proj_path, 'Outputs/Output_01/01_Intermediates/*[0-9]*_AnabranchHandler/AnabranchTypes.lyr')
            #
            # # if anabranch_lyr exists and overwrite is set to True delete the layer and AnabranchHandler folder
            # # prevents ending up with multiple AnabranchHandler folders
            # if anabranch_lyr is not None and overwrite is True:
            #     anabranch_dir = os.path.dirname(anabranch_lyr)
            #     shutil.rmtree(anabranch_dir)
            #
            # if anabranch_lyr is None or overwrite is True:
            #     print "Running braid handler for " + dir
            #     try:
            #         braid_handler(brat_table)
            #     except Exception as err:
            #         print 'BRAT braid handler failed for ' + dir + '. Exception thrown was:'
            #         print err
            # else:
            #
            #     print "Anabranch handler layer already exists.  Skipping " + dir
        else:
            print "WARNING: Script cannot be run.  BRAT table doesn't exist for " + dir


if __name__ == "__main__":
    main()
