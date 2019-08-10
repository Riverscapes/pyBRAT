#----------------------------------------------------------------------------------------------------------------------------
# Name: BRAT Project Builder (Batch)
#
# Purpose: Runs BRAT project builder tool for multiple HUC8s
#
# Notes:       - The scripts assumes data are in standard ETAL BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) all input data for each basin are located in the proper location within
#                    the basin's subdirectory:
#                           segmented network = NHD/NHD_24k_300mReaches.shp
#                           DEM = DEM/NED_DEM_10m.tif
#                           existing veg = LANDFIRE/LANDFIRE_200EVT.tif
#                           historic veg = LANDFIRE/LANDFIRE_200BPS.tif
#                           etc.
#                   If inputs are named otherwise, the code will need to be slightly modified to
#                   find the proper files. All basin inputs should have the same name.
#               - The script will execute on all subfolders in the parent folder EXCEPT
#                 those that start with a '00_*' (e.g., '00_Projectwide')
#
# Date: March 2019
# Author: Sara Bangen (sara.bangen@gmail.com)
#----------------------------------------------------------------------------------------------------------------------------

# user defined arguments:

# pf_path - path to project folder set up in standard BRAT format
# run_folder - name of the folder that will serve as the BRAT project folder
#               containing this run (will be created in each basin subdirectory
#               if it does not already exist)
# overwrite_run - True/False for whether to overwrite the run_folder if it already
#                   contains data
# pybrat_path - folder path holding the BRAT tool scripts
# proj_name - name of project (used in XML)

pf_path = r'C:\Users\ETAL\Desktop\GYE_BRAT\wrk_Data'
run_folder = 'BatchRun_01'
overwrite_run = False
pybrat_path = 'C:/Users/ETAL/Desktop/pyBRAT'
proj_name = 'GYE BRAT - Wyoming'


#  import required modules and extensions
import os
import sys
import arcpy
from shutil import rmtree

arcpy.CheckOutExtension('Spatial')
sys.path.append(pybrat_path)
from BRATProject import main as bratproj


def main(overwrite = overwrite_run):

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
        
        # define BRAT folder for basin and make if it doesn't already exist
        brat_folder = os.path.join(pf_path, dir, 'BRAT')
        if not os.path.exists(brat_folder):
            os.makedirs(brat_folder)

        # define run folder for basin & make if it doesn't exist already
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        if not os.path.exists(proj_path):
            os.makedirs(proj_path)
            
        # remove old run if overwrite is True, skip if False
        inputs_folder = os.path.join(proj_path, 'Inputs')
        if os.path.exists(inputs_folder) and overwrite is True:
            print "...............Removing old BRAT run folder"
            rmtree(proj_path)
            os.makedirs(proj_path)
        else:
            pass

        # only run if inputs folder doesn't exist
        if not os.path.exists(inputs_folder):

            # define watershed name and HUC ID from basin directory
            huc_ID = dir.split('_')[1]
            watershed_name = dir.split('_')[0]

            # find existing and historic veg for basin
            ex_veg = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_200EVT.tif')
            hist_veg = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_200BPS.tif')

            # find segmented network for basin
            network = os.path.join(pf_path, dir, 'NHD/NHD_24k_300mReaches.shp')

            # find dem for basin
            DEM = os.path.join(pf_path, dir, 'DEM/NED_DEM_10m.tif')

            # define landuse as existing veg
            landuse = ex_veg

            # find valley bottom (if present)
            if os.path.exists(os.path.join(pf_path, dir, 'VBET/Provisional_ValleyBottom_Unedited.shp')):
                valley = os.path.join(pf_path, dir, 'VBET/Provisional_ValleyBottom_Unedited.shp')
            else:
                valley = None

            # find roads (if present)
            if os.path.exists(os.path.join(pf_path, dir, 'RoadsRails/tl_2018_roads.shp')):
                road = os.path.join(pf_path, dir, 'RoadsRails/tl_2018_roads.shp')
            else:
                road = None

            # find perennial stream (if present)
            if os.path.exists(os.path.join(pf_path, dir, 'NHD/NHD_24k_Perennial.shp')):
                perennial_stream = os.path.join(pf_path, dir, 'NHD/NHD_24k_Perennial.shp')
            else:
                perennial_stream = None

            # find railroads if present
            if os.path.exists(os.path.join(pf_path, dir, 'RoadsRails/tl_2018_us_rails.shp')):
                rr = os.path.join(pf_path, dir, 'RoadsRails/tl_2018_us_rails.shp')
            else:
                rr = None

            # find canals/ditches if present
            if os.path.exists(os.path.join(pf_path, dir, 'NHD/NHDCanalsDitches.shp')):
                canal = os.path.join(pf_path, dir, 'NHD/NHDCanalsDitches.shp')
            else:
                canal = None

            # find landownership data if present
            if os.path.exists(os.path.join(pf_path, dir, 'LandOwnership/NationalSurfaceManagementAgency.shp')):
                ownership = os.path.join(pf_path, dir, 'LandOwnership/NationalSurfaceManagementAgency.shp')
            else:
                ownership = None
            # find surveyed beaver dams if present
            if os.path.exists(os.path.join(pf_path, dir, 'Dams', 'SurveyedDams.shp')):
                 beaver_dams = os.path.join(pf_path, dir, 'Dams', 'SurveyedDams.shp')
            else:
                 beaver_dams = None

            if all([os.path.exists(ex_veg), os.path.exists(hist_veg), os.path.exists(network), os.path.exists(DEM)]):
                print "Running BRAT project script for " + dir 
                try:
                    bratproj(proj_path, proj_name, huc_ID, watershed_name, ex_veg, hist_veg, network, DEM, landuse, valley, road, rr, canal, ownership, beaver_dams, perennial_stream)
                except Exception as err:
                    print "WARNING: Error with BRAT project builder for " + dir + ". The exception thrown was:"
                    print err
            else:
                print "WARNING: Script cannot be run for " + dir + " - Not all inputs exist."
                pass
        else:
            print "SKIPPING " + dir + "- run folder already populated."


if __name__ == '__main__':
    main()
