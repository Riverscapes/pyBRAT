#  define parent folder path and run folder name for directory search
pf_path = r'C:\Users\a02046349\Desktop\GYE_BRAT\wrk_Data'
run_folder = 'BatchRun_02'
overwrite_run = False
fix_list = ['YellowstoneHeadwaters_10070001']

#  import required modules and extensions
import os
import sys
import arcpy
import glob
from shutil import rmtree

arcpy.CheckOutExtension('Spatial')
sys.path.append('C:/Users/a02046349/Desktop/pyBRAT')
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

    # run function for each huc8 folder
    for dir in fix_list:
        
        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
        
        if os.path.exists(proj_path):
            
            out_path = os.path.join(proj_path, 'Outputs')
            if overwrite is True and os.path.exists(out_path):
                rmtree(out_path)
            if not os.path.exists(out_path):

                projName = 'GYE_BRAT'
                watershed_name = dir.split('_')[0]
                huc_ID = dir.split('_')[1]
                
                seg_network = os.path.join(proj_path, 'Inputs/02_Network/Network_01/NHD_24k_300mReaches.shp')
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

                if os.path.exists(os.path.join(proj_path, 'Inputs/03_Topography/DEM_01/Flow/DrainArea_sqkm.tif')):
                    flow_acc = os.path.join(proj_path, 'Inputs/03_Topography/DEM_01/Flow/DrainArea_sqkm.tif')
                else:
                    flow_acc = None

                # ownership = find_file(proj_path, 'Inputs/*[0-9]*_Anthropogenic/*[0-9]*_LandOwnership/Land_Ownership_01/NationalSurfaceManagementAgency.shp')

                out_name = 'BRAT_Table.shp'

                if all([os.path.exists(proj_path), os.path.exists(seg_network), os.path.exists(in_DEM), os.path.exists(coded_veg),
                        os.path.exists(coded_hist), os.path.exists(valley_bottom), os.path.exists(road), os.path.exists(landuse),
                        os.path.exists(perennial_network), os.path.exists(ownership)]):
                    try:
                        print "Running BRAT table script for " + dir
                        brat_table(proj_path, seg_network, in_DEM, flow_acc, coded_veg, coded_hist, valley_bottom,
                                   road, railroad, canal, landuse, ownership, perennial_network, out_name,
                                   description = projName, find_clusters = True, should_segment_network = True, ownership_segment_network=True,
                                   is_verbose = True)
                    except Exception as err:
                        print "Error with " + watershed_name + " project in BRAT Table. The exception thrown was:"
                        print err
                else:
                    print "WARNING: Script cannot be run.  Not all inputs exist for " + dir
                    pass
            else:
                print 'BRAT table output already exists for ' + dir
                pass
        else:
            print "WARNING: BRAT table cannot be run.  No BRAT project folder exists for " + dir


if __name__ == '__main__':
    main()
