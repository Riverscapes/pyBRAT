#----------------------------------------------------------------------------------------------------------------------------
# Name: BRAT Table (Batch)
#
# Purpose: Runs BRAT table tool for multiple HUC8s
#
# Notes:       - The scripts assumes data are in standard BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) All input data for each basin are located in the proper location within
#                    the basin's BRAT project path, created from the BRAT project builder tool.
#                   File names are assumed to follow ETAL standards, i.e:
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
# proj_name - name of project (used in XML)#  define parent folder path and run folder name for directory search
# find_clusters - True/False for whether to find clusters of braided network
# should_segment_network - True/False for whether to segment network where they intersect with roads (recommended against - see website: http://brat.riverscapes.net/Documentation/Tutorials/4-BRATTableTool.html)
# segment_by_ownership - True/False for whether to segment network where it intersects with different land ownership categories (recommended against - see website: http://brat.riverscapes.net/Documentation/Tutorials/4-BRATTableTool.html)

pf_path = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data'
run_folder = 'BatchRun_01'
overwrite_run = False
pybrat_path = 'C:/Users/ETAL/Desktop/pyBRAT'
proj_name = 'GYE BRAT - Wyoming'
find_clusters = True
should_segment_network = False
segment_by_ownership = False


#  import required modules and extensions
import os
import sys
import arcpy
import glob
from shutil import rmtree

arcpy.CheckOutExtension('Spatial')
sys.path.append(pybrat_path)
from BRAT_table import main as brat_table
arcpy.env.overwriteOutput = True
arcpy.env.outputZFlag="Disabled"


def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)[0]
    else:
        file_path = None

    return file_path


def main(overwrite = overwrite_run):
    
    # change directory to the parent folder path
    os.chdir(pf_path)
    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # run BRAT table function for each huc8 folder
    for dir in dir_list:
  
        # only try running if BRAT run folder exists
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)        
        if os.path.exists(proj_path):
            # check for BRAT table output, delete if overwrite is True 
            out_path = os.path.join(proj_path, 'Outputs')
            if os.path.exists(out_path):
                if overwrite is True:
                    print "...............Deleting previous BRAT table run"
                    rmtree(out_path)
            
            if not os.path.exists(out_path):

                # define watershed name and HUC ID from directory name
                watershed_name = dir.split('_')[0]
                huc_ID = dir.split('_')[1]

                # gather inputs from basin's run folder
                seg_network = os.path.join(proj_path, 'Inputs/02_Network/Network_01/NHD_24k_300mReaches_edited.shp')
                in_DEM = find_file(proj_path, 'Inputs/03_Topography/DEM_01/*.tif')
                coded_veg = find_file(proj_path, 'Inputs/01_Vegetation/01_ExistingVegetation/Ex_Veg_01/*.tif')
                coded_hist = find_file(proj_path, 'Inputs/01_Vegetation/02_HistoricVegetation/Hist_Veg_01/*.tif')
                perennial_network = find_file(proj_path, 'Inputs/*[0-9]*_PerennialStream/PerennialStream_01/NHD_24k_Perennial.shp')
                valley_bottom = find_file(proj_path, 'Inputs/*[0-9]*_Anthropogenic/*[0-9]*_ValleyBottom/Valley_01/Provisional_ValleyBottom_Unedited.shp')
                road = find_file(proj_path, 'Inputs/*[0-9]*_Anthropogenic/*[0-9]*_Roads/Roads_01/tl_2018_roads.shp')
                railroad = find_file(proj_path, 'Inputs/*[0-9]*_Anthropogenic/*[0-9]*_Railroads/Railroads_01/tl_2018_us_rails.shp')
                canal = find_file(proj_path, 'Inputs/*[0-9]*_Anthropogenic/*[0-9]*_Canals/Canals_01/NHDCanalsDitches.shp')
                landuse = find_file(proj_path, 'Inputs/*[0-9]*_Anthropogenic/*[0-9]*_LandUse/Land_Use_01/*.tif')
                ownership = find_file(proj_path, 'Inputs/*[0-9]*_Anthropogenic/*[0-9]*_LandOwnership/Land_Ownership_01/NationalSurfaceManagementAgency.shp')

                # use flow raster if previously calculated
                if os.path.exists(os.path.join(proj_path, 'Inputs/03_Topography/DEM_01/Flow/DrainArea_sqkm.tif')):
                    flow_acc = os.path.join(proj_path, 'Inputs/03_Topography/DEM_01/Flow/DrainArea_sqkm.tif')
                else:
                    flow_acc = None

                # check for required inputs
                if all([os.path.exists(proj_path), os.path.exists(seg_network), os.path.exists(in_DEM), os.path.exists(coded_veg),
                        os.path.exists(coded_hist)]):
                    # try running BRAT table script, if error print and move to next basin
                    try:
                        print "Running BRAT table script for " + dir
                        brat_table(proj_path, seg_network, in_DEM, flow_acc, coded_veg, coded_hist, valley_bottom,
                                   road, railroad, canal, landuse, ownership, perennial_network, out_name = 'BRAT_Table.shp',
                                   description = proj_name, find_clusters=find_clusters, should_segment_network=should_segment_network,
                                   segment_by_ownership=segment_by_ownership, is_verbose=True)
                    except Exception as err:
                        print "WARNING: Error with BRAT Table for " + dir + ". The exception thrown was:"
                        print err
                else:
                    print "WARNING: Script cannot be run.  Not all inputs exist for " + dir
                    pass
            else:
                print "SKIPPING " + dir + "- BRAT table output already exists."
                pass
        else:
            print "WARNING: BRAT table cannot be run for " + dir + " -  BRAT project folder doesn't exist."


if __name__ == '__main__':
    main()
