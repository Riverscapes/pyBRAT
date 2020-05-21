##------------------------------------------------------------------------##
## Name: BRAT Deliverable Copier                                          ##
## Purpose: Copies all BRAT outputs from a local path to a Box path and   ##
##           organizes for delivering to stakeholders                     ##
## Note: To run properly, the project folder must match previously        ##
##         specified project folder formats                               ##
##                                                                        ##
## Author: Maggie Hallerud                                                ##
##         maggie.hallerud@aggiemail.usu.edu                              ##
##                                                                        ##
## Date Created: 07/2019                                                  ##
##------------------------------------------------------------------------##

# specify file paths
pf_path = 'C:/Users/a02046349/Desktop/Idaho_BRAT'
new_path = 'C:/Users/a02046349/Box/ET_AL/*******'

# load dependencies
import os
import shutil
import arcpy


def main():
    # make list of all HUC folders in project path
    os.chdir(pf_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # copy shapefiles from local to box for each HUC
    for dir in dir_list:
            print "Copying files for " + dir + "....."
            copy_shps(dir)
            copy_lpk(dir)
            copy_summaries(dir)
        
            
def copy_shps(dir):
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
	table_peren = os.path.join(output_folder, '01_Intermediates/BRAT_Table_Perennial.shp')
	comb = os.path.join(output_folder, '02_Analyses/Combined_Capacity_Model.shp')
	comb_peren = os.path.join(output_folder, '02_Analyses/Combined_Capacity_Model_Perennial.shp')
	cons = os.path.join(output_folder, '02_Analyses/Conservation_Restoration_Model.shp')
	cons_peren = os.path.join(output_folder, '02_Analyses/Conservation_Restoration_Model_Perennial.shp')
	val = os.path.join(output_folder, '02_Analyses/Data_Capture_Validation.shp')
	val_peren = os.path.join(output_folder, '02_Analyses/Data_Capture_Validation_Perennial.shp')
	table_out = os.path.join(new_path, dir, 'Outputs/Output_SHP/03_Additional_Network_Data/Intermediates/BRAT_Table_'+huc_name+'.shp')
	comb_out = os.path.join(new_path, dir, 'Outputs/Output_SHP/03_Additional_Network_Data/Combined_Capacity_Model/Combined_Capacity_'+huc_name+'.shp')
	cons_out = os.path.join(new_path, dir, 'Outputs/Output_SHP/03_Additional_Network_Data/Conservation_Restoration_Model/Conservation_Restoration_'+huc_name+'.shp')
	val_out = os.path.join(new_path, dir, 'Outputs/Output_SHP/03_Additional_Network_Data/Data_Validation/Data_Validation_'+huc_name+'.shp')
	peren_table_out = os.path.join(new_path, dir, 'Outputs/Output_SHP/01_Perennial_Network/Intermediates/BRAT_Table_Perennial_'+huc_name+'.shp')
	peren_comb_out = os.path.join(new_path, dir, 'Outputs/Output_SHP/01_Perennial_Network/Combined_Capacity_Model/Combined_Capacity_Perennial_'+huc_name+'.shp')
	peren_cons_out = os.path.join(new_path, dir, 'Outputs/Output_SHP/01_Perennial_Network/Conservation_Restoration_Model/Conservation_Restoration_Perennial_'+huc_name+'.shp')
	peren_val_out = os.path.join(new_path, dir, 'Outputs/Output_SHP/01_Perennial_Network/Data_Validation/Data_Validation_Perennial_'+huc_name+'.shp')
	in_files = [table, comb, cons, val, table_peren, comb_peren, cons_peren, val_peren]
	out_files = [table_out, comb_out, cons_out, val_out, peren_table_out, peren_comb_out, peren_cons_out, peren_val_out]
	print dir
	for i in range(0,7):
		if not os.path.exists(out_files[i]):
			try:
				arcpy.CopyFeatures_management(in_files[i], out_files[i])
			except Exception as err:
				print err


def copy_lpk(dir):
        batch2 = os.path.join(pf_path, dir, 'BRAT/BatchRun_02')
        if os.path.exists(batch2):
                proj_path = batch2
        else:
                proj_path = os.path.join(pf_path, dir, 'BRAT/BatchRun_01')
        old_lpk = os.path.join(proj_path, 'SummaryProducts/LPK')
        new_lpk = os.path.join(new_path, dir, 'Outputs/Output_LPK')
        try:
                shutil.copytree(old_lpk, new_lpk)
        except Exception as err:
                print err


def copy_summaries(dir):
        huc_name = dir.split('_')[0]
        batch2 = os.path.join(pf_path, dir, 'BRAT/BatchRun_02')
        if os.path.exists(batch2):
                proj_path = batch2
        else:
                proj_path = os.path.join(pf_path, dir, 'BRAT/BatchRun_01')
        old_table = os.path.join(proj_path, 'SummaryProducts/SummaryTables', huc_name + '_SummaryTables_Perennial.xlsx')
        new_table = os.path.join(new_path, dir, 'Summary_Products', huc_name + '_SummaryTables_Perennial.xlsx')
        old_plot = os.path.join(proj_path, dir, 'SummaryProducts/SummaryTables/regression_plot.png')
        new_plot = os.path.join(new_path, dir, 'Summary_Products', huc_name + '_Observed_vs_Predicted_Plot.png')
        old_plot_2 = os.path.join(proj_path, dir, 'SummaryProducts/SummaryTables/quantile_regression_plot.png')
        new_plot_2 = os.path.join(new_path, dir, 'Summary_Products', huc_name + '_Quantile_Regression_Plot.png')
        old_files = [old_table, old_plot, old_plot_2]
        new_files = [new_table, new_plot, new_plot_2]
        for i in range(0,2):
                if os.path.exists(old_files[i]):
                        try:
                                shutil.copy(old_files[i], new_files[i])
                        except Exception as err:
                                print err
                else:
                        print "..... No file named " + old_files[i]


def check_kmzs(file_pattern, full):
        for dir in dir_list:
                if full:
                        folder = os.path.join(new_path, dir, 'Outputs/Output_KMZ/02_Additional_Network_Data')
                else:
                        folder = os.path.join(new_path, dir, 'Outputs/Output_KMZ/01_Perennial_Network')
                check = os.path.join(folder, file_pattern)
                if not os.path.exists(check):
                        print dir


if __name__ == "__main__":
        main()
