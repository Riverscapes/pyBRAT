#  define parent folder path and run folder name for directory search
pf_path = r'C:\Users\a02046349\Desktop\Idaho_BRAT\wrk_Data'
#run_folder = 'BatchRun_01'
overwrite = True
da_thresholds_csv = 'C:/Users/a02046349/Desktop/Idaho_BRAT/wrk_Data/00_Projectwide/ModelParameters/Idaho_DA_Thresholds.csv'
conflict_pts_proj = 'C:/Users/a02046349/Desktop/From_IDFG/ConflictPoints_EditedThinned.shp'
conflict_pts_flooding = 'C:/Users/a02046349/Desktop/From_IDFG/ConflictPoints_EditedThinned_Flooding.shp'
conflict_pts_trees = 'C:/Users/a02046349/Desktop/From_IDFG/ConflictPoints_EditedThinned_TreeCutting.shp'

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
import Risk_Validation
reload(Risk_Validation)

def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)
    else:
        file_path = None

    return file_path


def clip_conflict_points(dir, conflict_pts_proj, out_name=None):
    print '.....Clipping conflict points to ' + dir
    huc_boundary = os.path.join(pf_path, dir, 'NHD/WBDHU8.shp')
    out_folder = os.path.join(pf_path, dir, "ConflictPoints")
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    if out_name is None:
        base_name = os.path.basename(conflict_pts_proj).split('.')[0]
        out_path = os.path.join(out_folder, base_name+'_clip.shp')
    else:
        out_path = os.path.join(out_folder, out_name + ".shp")
    if not os.path.exists(out_path):
        arcpy.Clip_analysis(conflict_pts_proj, huc_boundary, out_path)
    return out_path
    
    
def main():

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
    for dir in dir_list:
        # clip conflict points
        huc_all_conflict = clip_conflict_points(dir, conflict_pts_proj)
        huc_flood_conflict = clip_conflict_points(dir, conflict_pts_flooding, "Flooding_Conflict_Pts")
        huc_tree_conflict = clip_conflict_points(dir, conflict_pts_trees, "TreeCutting_Conflict_Pts")

        batch2 = os.path.join(pf_path, dir, "BRAT", "BatchRun_02")
        if os.path.exists(batch2):
            proj_path = batch2
        else:
            proj_path = os.path.join(pf_path, dir, "BRAT", "BatchRun_01")
        # check for output_02 folder
        #proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        output2_folder = os.path.join(proj_path, "Outputs/Output_02")
        if os.path.exists(output2_folder):
            out_folder = output2_folder
        else:
            out_folder = os.path.join(proj_path, "Outputs/Output_01")
        cons_rest = os.path.join(out_folder, '02_Analyses/Conservation_Restoration_Model.shp')

        if os.path.exists(cons_rest):
           
            # check if risk validation has already been run by searching for output shapefile
            # if directory doesn't exist or overwrite is set to true, run risk validation script
            risk_val_out = os.path.join(out_folder, '02_Analyses/Risk_Validation.shp')
            if not os.path.exists(risk_val_out) or overwrite is True:

                print "Running risk validation for " + dir

                try:
                    if dir in paramDict:
                        subDict = {k: v for k, v in paramDict.iteritems() if dir in k}
                        huc_threshold = float(subDict[dir]['DA_Threshold'])
                        print ".....all conflict points"
                        Risk_Validation.main(cons_rest, 'Risk_Validation_All', huc_all_conflict, da_threshold=huc_threshold, out_csv="RiskTable_AllConflicts")
                        print ".....flooding conflict points"
                        Risk_Validation.main(cons_rest, 'Risk_Validation_Flooding', huc_flood_conflict, da_threshold=huc_threshold, out_csv="RiskTable_FloodConflicts")
                        print ".....tree cutting conflict points"
                        Risk_Validation.main(cons_rest, 'Risk_Validation_TreeCutting', huc_tree_conflict, da_threshold=huc_threshold, out_csv="RiskTable_TreeConflicts")
                    else:
                        print "--WARNING! Running without da threshold--"
                        risk_val(cons_rest, 'Risk_Validation', huc_conflict_pts, da_threshold=None)
                    
                except Exception as err:
                    print 'RISK VALIDATION FAILED FOR ' + dir + '. Exception thrown was:'
                    print err
            else:

                print "Risk validation has already been run.  Skipping " + dir

        else:
            print "WARNING: Script cannot be run. Conservation restoration output doesn't exist for " + dir


if __name__ == "__main__":
    main()
