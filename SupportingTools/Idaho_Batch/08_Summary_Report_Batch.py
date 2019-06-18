# specify folder paths
pf_path = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data'
run_folder = 'BatchRun_02'
base_out_name = 'SummaryTables_Perennial'
overwrite_run = True
output_folder = None
clip_network = True

import sys
import os
sys.path.append('C:/Users/a02046349/Desktop/pyBRAT')
from Collect_Summary_Products import main as summary
fix_list = ['YellowstoneHeadwaters_10070001']

def main(overwrite = overwrite_run):

    os.chdir(pf_path)

    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    for dir in fix_list:
        # only run if validation output exists
        valid = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01/02_Analyses/Data_Capture_Validation.shp')

        if os.path.exists(valid):

            # clip to perennial canals
            peren_valid = valid.split('.')[0] + '_Perennial.shp' 
            if clip_network:
                print '.......... Clipping to perennial'
                peren = os.path.join(pf_path, dir, 'NHD', 'NHD_24k_Perennial_CanalsDitches.shp')
                arcpy.Clip_analysis(valid, peren, peren_valid)
                valid = peren_valid

            # run summary_report
            proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
            huc_name = dir.split('_')[0]
            out_name= huc_name + '_' + base_out_name
            if output_folder is None:
                out_path = os.path.join(pf_path, dir, 'BRAT', run_folder, 'SummaryProducts', 'SummaryTables', out_name)
            else:
                out_path = os.path.join(output_folder, out_name)
            if not os.path.exists(out_path) or overwrite is True:
                try:
                    print 'Running summary report for ' + dir + '........'
                    summary(proj_path, valid, dir, out_name, output_folder)
                except Exception as err:
                    print 'Summary report failed for ' + dir
                    print err
            else:
                print 'Summary tables already exist for ' + dir

            if os.path.exists(peren_valid):
                arcpy.Delete_management(peren_valid)


if __name__ == "__main__":
    main()
