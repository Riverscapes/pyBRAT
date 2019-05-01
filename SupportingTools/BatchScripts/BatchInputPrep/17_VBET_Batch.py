
rcat_folder= 'C:/Users/Maggie/Desktop/RCAT'
pf_path = 'C:/Users/Maggie/Box/ET_AL/Projects/USA/GYE/BRAT_FY18_19/wrk_Data/BatchRun01'
batch_folder_name = 'BatchRun_01'

import os
import arcpy
import sys
sys.path.append(rcat_folder)
import VBETProject, VBET


def main():
    arcpy.env.overwriteOutput = True
    os.chdir(pf_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    for dir in dir_list:
        print "Running VBET Project for " + dir
        vbet_folder = os.path.join(pf_path, dir, 'VBET')
        if not os.path.exists(vbet_folder):
            os.mkdir(vbet_folder)
        batch_folder = os.path.join(pf_path, dir, 'VBET', batch_folder_name)
        if not os.path.exists(batch_folder):
            os.mkdir(batch_folder)
        dem = os.path.join(pf_path, dir, 'DEM/NED_DEM_10m.tif')
        network = os.path.join(pf_path, dir, 'NHD/NHDFlowline.shp')
        try:
            VBETProject.main(batch_folder, dem, network, None)
        except Exception as err:
            print 'VBET Project failed for ' + dir
            print 'ERROR THROWN:'
            print err
            

if __name__ == "__main__":
    main()
    
