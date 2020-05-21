##------------------------------------------------------------------------##
## Name: Check BRAT Project Status                                        ##
## Purpose: Checks existence of all major BRAT output files for all BRAT  ##
##           projects in a project directory.                             ##
## Note: To run properly, the project folder must match previously        ##
##         specified project folder formats                               ##
##                                                                        ##
## Author: Maggie Hallerud                                                ##
##         maggie.hallerud@aggiemail.usu.edu                              ##
##                                                                        ##
## Date Created: 07/2019                                                  ##
##------------------------------------------------------------------------##

pf_path = 'C:/Users/a02046349/Desktop/Idaho_BRAT/wrk_Data'

import os
import arcpy

def check_status():

    os.chdir(pf_path)

    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)
            
    for dir in dir_list:
            print "Checking " + dir + "................"
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
                output_folder = os.path.join(proj_path, 'Outputs/Output_01')
            huc_name = dir.split('_')[0]
            table = os.path.join(output_folder, '01_Intermediates/BRAT_Table.shp')
            comb_cap = os.path.join(output_folder, '02_Analyses/Combined_Capacity_Model.shp')
            cons_rest = os.path.join(output_folder, '02_Analyses/Conservation_Restoration_Model.shp')
            valid = os.path.join(output_folder, '02_Analyses/Data_Capture_Validation.shp')
            summary = os.path.join(proj_path, 'SummaryProducts/SummaryTables', huc_name + '_SummaryTables_Full.xlsx')
            sumperen = os.path.join(proj_path, 'SummaryProducts/SummaryTables', huc_name + '_SummaryTables_Perennial.xlsx')
            layer_package = os.path.join(proj_path, 'SummaryProducts/LPK', 'BRAT_' + dir + '_Perennial.lpk')
            reg_plot = os.path.join(proj_path, 'SummaryProducts/SummaryTables/regression_plot.png')
            quant_plot = os.path.join(proj_path, 'SummaryProducts/SummaryTables/quantile_regression_plot.png')
            if not os.path.exists(table):
                    print '		BRAT Table missing'
            if not os.path.exists(comb_cap):
                    print '		Combined Capacity missing'
            if not os.path.exists(cons_rest):
                    print '		Conservation Restoration missing'
            if not os.path.exists(valid):
                    print '		Validation missing'
            if not os.path.exists(summary):
                    print '		Summary Report full network missing'
            if not os.path.exists(sumperen):
                    print '		Summary Report perennial network missing'
            if not os.path.exists(layer_package):
                    print '		Layer Package missing'
            if not os.path.exists(reg_plot):
                    print '             Regression plot missing'
            if not os.path.exists(quant_plot):
                    print '             Quantile regression plot missing'



def remove_clipped_files():
    # get list of watershed directories for project
    os.chdir(pf_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    for dir in dir_list:
        print "Deleting clipped files for " + dir
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)

        # grab list of all files in project folder
        all_files = []
        all_files = [os.path.join(r,file) for r,d,f in os.walk(proj_path) for file in f]

        # pull clipped files based on name
        clipped = []
        for f in all_files:
            if f.endswith('_clipped.shp'): #or f.endswith('_clipped.lyr'):
                clipped.append(f)

        # delete clipped files one by one
        for f in clipped:
            print f
            try:
                arcpy.Delete_management(f)
            except Exception as err:
                print "Could not delete " + f
                print err
    
