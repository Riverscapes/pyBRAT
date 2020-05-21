##------------------------------------------------------------------------##
## Name: BRAT Batch Merge and Clip to Regions                             ##
## Purpose: Merges BRAT outputs across large project area and clips to    ##
##           each region in the provided regions shapefile                ##
## Note: To run properly, the project folder must match previously        ##
##         specified project folder formats                               ##
##                                                                        ##
## Author: Maggie Hallerud                                                ##
##         maggie.hallerud@aggiemail.usu.edu                              ##
##                                                                        ##
## Date Created: 07/2019                                                  ##
##------------------------------------------------------------------------##


# set input parameters
regions_shp = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/ProjectBoundary/GYE_MapBoundary.shp'
out_folder = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/00_Final'
#qa_qc_csv = 'C:/Users/a02046349/Desktop/Idaho_BRAT/wrk_Data/00_Projectwide/ModelParameters/Idaho_BRAT_QA_QC.csv'
pf_path = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data'
run_folder = 'BatchRun_03'
overwrite = True
clip = False

# load dependencies
import sys
import arcpy
import os
from collections import defaultdict
import csv
import glob


def main():
    arcpy.env.overwriteOutput=True
    
    """# read in csv of qa/qc status parameters and convert to python dictionary
    paramDict = defaultdict(dict)
    with open(qa_qc_csv, "rb") as infile:
        reader = csv.reader(infile)
        headers = next(reader)[1:]
        for row in reader:
            paramDict[row[0]] = {key: value for key, value in zip(headers, row[1:])}"""

    # get list of watershed folders
    os.chdir(pf_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    """# get list of watersheds ready to merge
    merge_list = []
    count = 0
    for dir in dir_list:
        if dir in paramDict:
            subDict = {k: v for k, v in paramDict.iteritems() if dir in k}
            verdict = str(subDict[dir]['outcome'])
            if verdict == "Elevate to Final run":
                merge_list.append(dir)
                count += 1"""
            
    # set output names
    proj_brat_table = os.path.join(out_folder, 'BRAT_Table_full_FINAL.shp')
    proj_comb_fis = os.path.join(out_folder, 'Combined_Capacity_Model_full_FINAL.shp')
    proj_cons_rest = os.path.join(out_folder, 'Conservation_Restoration_Model_full_FINAL.shp')
    proj_validation = os.path.join(out_folder, 'Data_Capture_Validation_full_FINAL.shp')
    proj_dams = os.path.join(out_folder, 'GYA_BeaverDams_FINAL.shp')

    
    # merge BRAT table, conservation restoration, validation, and dam survey outputs
    try:
        merge_all_files('01_Intermediates/BRAT_Table.shp', proj_brat_table, dir_list, overwrite, clip)
    except Exception as err:
        print 'BRAT table merge failed. Error thrown was:'
        print err

    try:
        merge_all_files('02_Analyses/Combined_Capacity_Model.shp', proj_comb_fis, dir_list, overwrite, clip)
    except Exception as err:
        print 'Conservation merge failed. Error thrown was:'
        print err

    try:
        merge_all_files('02_Analyses/Conservation_Restoration_Model.shp', proj_cons_rest, dir_list, overwrite, clip)
    except Exception as err:
        print 'Conservation merge failed. Error thrown was:'
        print err
    
    try:
        merge_all_files('02_Analyses/Data_Capture_Validation.shp', proj_validation, dir_list, overwrite, clip)
    except Exception as err:
        print 'Validation merge failed. Error thrown was:'
        print err
    
    try:
        print 'Skip'#merge_all_files('Inputs/*[0-9]*_BeaverDams/Beaver_Dam_01/*.shp', proj_dams, dir_list, overwrite, clip=False, input_folder=True)
    except Exception as err:
        print 'Dam census merge failed. Error thrown was:'
        print err
    
    # clip final projectwide outputs to regions of interest
    try:
        clip_to_regions(regions_shp, proj_brat_table, overwrite)
    except Exception as err:
        print 'Clipping BRAT table to regions failed. Error thrown was:'
        print err
    try:
        clip_to_regions(regions_shp, proj_cons_rest, overwrite)
    except Exception as err:
        print 'Clipping conservation restoration model to regions failed. Error thrown was:'
        print err
     
    try:
        clip_to_regions(regions_shp, proj_validation, overwrite)
    except Exception as err:
        print 'Clipping validation to regions failed. Error thrown was:'
        print err
    
    try:
        clip_to_regions(regions_shp, proj_dams, overwrite)
    except Exception as err:
        print 'Clipping dam census to regions failed. Error thrown was:'
        print err
    


def merge_all_files(filepath_pattern, final_out_path, dir_list, overwrite, clip, input_folder=False):
    if not os.path.exists(final_out_path) or overwrite is True:
        print "Merging for final " + os.path.basename(final_out_path) + ":"
        # grab file from each watershed's project folder matching given file pattern
        files_list = []
        for dir in dir_list:
            """#print '....................' + dir
            #check for batch2 folder
            batch2 = os.path.join(pf_path, dir, 'BRAT/BatchRun_02')
            if os.path.exists(batch2):
                proj_path = batch2
            else:
                proj_path = os.path.join(pf_path, dir, 'BRAT/BatchRun_01')
            #check for output2 folder
            output2 = os.path.join(proj_path, 'Outputs/Output_02')
            if os.path.exists(output2):
                output_folder = output2
            else:
                output_folder = os.path.join(proj_path, 'Outputs/Output_01')"""

            proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
            output_folder = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01')
            # find relevant file based on out folder and file pattern
            if input_folder:
                folder = proj_path
            else:
                folder = output_folder
            
            dir_file = find_file(folder, filepath_pattern)
            #dir_file = os.path.join(pf_path, dir, 'Beaver_Dams/Idaho_'+dir+'_BeaverDams.shp')
            if os.path.exists(dir_file):
                if clip is True:
                    out_name = os.path.basename(dir_file)
                    out_path = os.path.join(os.path.dirname(dir_file), out_name.split('.')[0]+'_Perennial.shp')
                    if not os.path.exists(out_path):
                        print '.....Clipping '+ dir
                        perennial = os.path.join(pf_path, dir, 'NHD/NHD_24k_Perennial_CanalsDitches.shp')
                        arcpy.Clip_analysis(dir_file, perennial, out_path)
                    files_list.append(out_path)
                else:
                    files_list.append(dir_file)
        # merge all files matching file pattern
        print '.....Merging all files'
        arcpy.Merge_management(files_list, final_out_path)
    else:
        print 'SKIPPING ' + os.path.basename(final_out_path) + ': already exists'


def clip_to_regions(regions_shp, project_output, overwrite):
    # make temp and list of management units
    regions = arcpy.CopyFeatures_management(regions_shp, 'in_memory/regions')
    regions_list = [row[0] for row in arcpy.da.SearchCursor(regions, 'NAME')]

    # clip projectwide output to each polygon in regions shapefile and name by region's name
    for region in regions_list:
        print 'Clipping projectwide ' + os.path.basename(project_output) + ' to ' + region
        # select shapefile of unit and make temp shapefile
        unit_shp = arcpy.Select_analysis(regions, 'in_memory/' + str(region.replace(' ', '')), "NAME = '%s'" % str(region))
        region_out = project_output.split('.')[0] + '_' + str(region.replace(' ', '')) + '.shp'
        if not os.path.exists(region_out) or overwrite is True:
            try:
                arcpy.Clip_analysis(project_output, unit_shp, region_out)
            except Exception as err:
                print 'Clipping ' + os.path.basename(project_output) + ' failed for ' + region + '. Error thrown was:'
                print err
        else:
            print 'SKIPPING ' + os.path.basename(region_out) + ': already exists'

        

def find_file(proj_path, file_pattern):
    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)[0]
    else:
        file_path = ''

    return file_path


if __name__ == "__main__":
    main()
