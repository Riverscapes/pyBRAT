#  define parent folder path and run folder name for directory search
pf_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_PriorityRuns'
run_folder = 'BatchRun_02'
overwrite_run = False

#  import required modules and extensions
import os
import sys
import arcpy

arcpy.CheckOutExtension('Spatial')
sys.path.append('C:/etal/LocalCode/pyBRAT/TNC_Changes')
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

        proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)

        if not os.path.exists(proj_path):
            os.makedirs(proj_path)

        if not os.path.exists(os.path.join(proj_path, 'Inputs') or overwrite is True):

            proj_name = 'TNC Priority Watersheds Second Run'
            huc_ID = dir.split('_')[1]
            watershed_name = dir.split('_')[0]

            ex_veg = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_140EVT.tif')
            hist_veg = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_140BPS.tif')
            network = os.path.join(pf_path, dir, 'NHD/NHD_24k_300mReaches.shp')
            DEM = os.path.join(pf_path, dir, 'DEM/NED_DEM_10m.tif')
            landuse = ex_veg
            valley = os.path.join(pf_path, dir, 'ValleyBottom', 'Provisional_ValleyBottom_Unedited.shp')
            road = os.path.join(pf_path, dir, 'RoadsRails/tl_2017_county_roads.shp')
            perennial_stream = os.path.join(pf_path, dir, 'NHD/NHD_24k_Perennial.shp')

            if os.path.exists(os.path.join(pf_path, dir, 'RoadsRails/tl_2017_rails.shp')):
                rr = os.path.join(pf_path, dir, 'RoadsRails/tl_2017_rails.shp')
            else:
                rr = None

            if os.path.exists(os.path.join(pf_path, dir, 'NHD/NHDCanalsDitches.shp')):
                canal = os.path.join(pf_path, dir, 'NHD/NHDCanalsDitches.shp')
            else:
                canal = None

            if os.path.exists(os.path.join(pf_path, dir, 'LandOwnership/NationalSurfaceManagementAgency.shp')):
                ownership = os.path.join(pf_path, dir, 'LandOwnership/NationalSurfaceManagementAgency.shp')
            else:
                ownership = None

            # if os.path.exists(os.path.join(pf_path, dir, 'Dams', huc_ID + 'SurveyedDams.shp')):
            #     beaver_dams = os.path.join(pf_path, dir, 'Dams', huc_ID + 'SurveyedDams.shp')
            # else:
            #     beaver_dams = None
            if os.path.exists(os.path.join(pf_path, dir, 'CensusData/Dams_WebApp.shp')):
                beaver_dams = os.path.join(pf_path, dir, 'CensusData/Dams_WebApp.shp')
            else:
                beaver_dams = None

            if all([os.path.exists(ex_veg), os.path.exists(hist_veg), os.path.exists(network), os.path.exists(DEM),
                    os.path.exists(landuse), os.path.exists(valley), os.path.exists(road), os.path.exists(perennial_stream)]):
                print "Running BRAT project script for " + dir
                try:
                    bratproj(proj_path, proj_name, huc_ID, watershed_name, ex_veg, hist_veg, network, DEM, landuse, valley, road, rr, canal, ownership, beaver_dams, perennial_stream)
                except Exception as err:
                    print "Error with " + watershed_name + " project in BRAT Project. The exception thrown was:"
                    print err
            else:
                print "WARNING: Script cannot be run.  Not all inputs exist for " + dir
                pass


if __name__ == '__main__':
    main()
