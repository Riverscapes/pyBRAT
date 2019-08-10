##########################################################################
##                                                                      ##
## NAME: Check_data                                                     ##
##                                                                      ##
## PURPOSE: Checks that all files needed to run full BRAT model:        ##
##          1. exist with proper name                                   ##
##          2. are in the proper projection                             ##
##          3. have required fields                                     ##
##          4. rasters are populated                                    ##
##                                                                      ##
##########################################################################

import zipfile
import arcpy
import os


zip_folder = None
pf_path = 'C:/Users/a02046349/Desktop/Idaho_BRAT/wrk_Data'
coord_sys= 'NAD 1983 Idaho TM (Meters)'
#coord_sys = 'NAD 1983 California (Teale) Albers (Meters)'
outCS = arcpy.SpatialReference(coord_sys)
cs_string = outCS.exportToString()
BRAT_folder = 'BatchRun_01' 

def main():



    if zip_folder:
        unzip_files(zip_folder, pf_path)
        
    os.chdir(pf_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)
        if 'new' in dir:
            dir_list.remove('new')
    
    for dir in dir_list:
        huc_name = dir.split('_')[0]
        huc_id = dir.split('_')[1]
        print dir + '.................................................'
        nhd_folder = os.path.join(pf_path, dir, 'NHD')
        dem_folder = os.path.join(pf_path, dir, 'DEM')
        landfire_folder = os.path.join(dir, 'LANDFIRE')
        # check if nhd files (segmented network, perennial network, canals/ditches, huc boundary) exist
        try:
            check_nhd_files(nhd_folder, huc_name, huc_id, cs_string)
        except Exception as err:
            print err
        # check if dem files(dem, hillshade) exist
        try:
            check_dem_files(dem_folder, huc_name, huc_id, cs_string)
        except Exception as err:
            print err
        # check existing veg/landuse and historic veg
        try:
            check_vegetation(landfire_folder, huc_name, huc_id, cs_string)
        except Exception as err:
            print err
        # check management inputs (roads, rails, valley bottom, land ownership)
        try:
            check_management_inputs(dir, huc_name, huc_id, cs_string)
        except Exception as err:
            print err
        # check for dam survey data
        #check_dams(dir)
        # check for output BRAT folder
        try:
            check_project_folder(dir, BRAT_folder)
        except Exception as err:
            print err


def check_nhd_files(nhd_folder, huc_name, huc_id, cs_string):
    # check for nhd folder
    if os.path.exists(nhd_folder):
        # file names searching for
        #flowline = os.path.join(nhd_folder, 'NHDFlowline.shp')
        #area = os.path.join(nhd_folder, 'NHDArea.shp')
        #waterbody = os.path.join(nhd_folder, 'NHDWaterbody.shp')
        huc = os.path.join(nhd_folder, 'WBDHU8.shp')
        peren = os.path.join(nhd_folder, 'NHD_24k_Perennial.shp')
        segmented_network = os.path.join(nhd_folder, 'NHD_24k_300mReaches.shp')
        peren_canals = os.path.join(nhd_folder, 'NHD_24k_Perennial_CanalsDitches.shp')
        canals = os.path.join(nhd_folder, 'NHDCanalsDitches.shp')
        files = [canals, huc] #area, waterbody, peren, segmented_network]
        # check for segmented network, correct projection, and huc fields
        if os.path.exists(segmented_network):
            #print '.......... Checking ' + segmented_network
            check_projection(segmented_network, cs_string)
            check_huc_fields(segmented_network)
        else:
            print '     segmented network missing.'
        # check for perennial network, correct projection, and huc fields
        if os.path.exists(peren_canals):
            #print '.......... Checking ' + peren_canals
            check_projection(peren_canals, cs_string)
            check_huc_fields(peren_canals)
        else:
            print '     perennial canals missing.'
        if os.path.exists(peren):
            #print '.......... Checking ' + peren
            check_projection(peren, cs_string)
            check_huc_fields(peren)
        else:
            print '     perennial missing.'
        # check for other files and correct projection
        for file in files:
            if os.path.exists(file):
                #print '.......... Checking ' + file
                check_projection(file, cs_string)
            else:
                print '     ' + file + ' MISSING.'
        
    else:
        print '     NHD FOLDER MISSING'



def check_dem_files(dem_folder, huc_name, huc_id, cs_string):
    if os.path.exists(dem_folder):
        dem = os.path.join(dem_folder, 'NED_DEM_10m_'+huc_id+'.tif')
        hs = os.path.join(dem_folder, 'NED_HS_10m.tif')
        # check DEM 
        if os.path.exists(dem):
            check_projection(dem, cs_string)
            min_elev = arcpy.GetRasterProperties_management(dem, "MINIMUM")
            max_elev = arcpy.GetRasterProperties_management(dem, "MAXIMUM")
            if min_elev == max_elev:
                print '     Check DEM values: min = max  '
        else:
            print '     DEM missing.'
        # check hillshade
        if os.path.exists(hs):
            check_projection(hs, cs_string)
            min_elev = arcpy.GetRasterProperties_management(hs, "MINIMUM")
            max_elev = arcpy.GetRasterProperties_management(hs, "MAXIMUM")
            if min_elev == max_elev:
                print '     Check hillshade values: min = max'
        #else:
        #    print '     ' + hs + ' MISSING.'
    else:
        print '     DEM FOLDER MISSING'



def check_vegetation(veg_folder, huc_name, huc_id, cs_string):
    if os.path.exists(veg_folder):
        evt = os.path.join(veg_folder, 'LANDFIRE_200EVT.tif')
        bps = os.path.join(veg_folder, 'LANDFIRE_200BPS.tif')
        evt_merge = os.path.join(veg_folder, 'LANDFIRE_EVT_merge.tif')
        bps_merge = os.path.join(veg_folder, 'LANDFIRE_BPS_merge.tif')
        # check existing vegetation & landuse
        if os.path.exists(evt):
            check_evt(evt)
        elif os.path.exists(evt_merge):
            check_evt(evt_merge)
        else:
            print '     EVT missing.' 

        # check historic vegetation
        if os.path.exists(bps):
            check_bps(bps)
        elif os.path.exists(bps_merge):
            check_bps(bps_merge)
        else:
            print '     BPS missing.'
    else:
        print '     LANDFIRE FOLDER MISSING'



def check_evt(evt):
            #print '.......... Checking ' + evt
            check_projection(evt, cs_string)
            fields = [f.name for f in arcpy.ListFields(evt)]
            if 'EVT_NAME' not in fields:
                print '                 EVT_NAME not in fields - EVT layer will not draw'
            if 'EVT_CLASS' not in fields:
                print '                 EVT_CLASS not in fields - EVT layer will not draw'
            if 'EVT_PHYS' not in fields:
                print '                 EVT_PHYS not in fields - EVT layer will not draw'                
            if 'VEG_CODE' not in fields:
                print '                 VEG_CODE MUST BE ADDED TO EVT'
            else:
                with arcpy.da.SearchCursor(evt, "VEG_CODE") as cursor:
                    for row in cursor:
                        if row[0] == ' ':
                            print '                 BLANKS IN VEG_CODE'
                        elif row[0] is None:
                            print '                 BLANKS IN VEG_CODE'
                        else:
                            pass
            if 'LU_CODE' not in fields:
                print '                 LU_CODE MUST BE ADDED'
            else:
                with arcpy.da.SearchCursor(evt, "LU_CODE") as cursor:
                    for row in cursor:
                        if row[0] == ' ':
                            print '                 BLANKS IN EVT VEG_CODE'
                        elif row[0] is None:
                            print '                 BLANKS IN EVT VEG_CODE'
                        else:
                            pass
            if 'LUI_Class' not in fields:
                print '                 LUI_CLASS MUST BE ADDED'
            try:
                count = arcpy.GetRasterProperties_management(evt, "UNIQUEVALUECOUNT")
                if count <= 5:
                    print '                 5 OR LESS EVT VALUES - CHECK VALUES'
            except Exception as err:
                print 'Could not check unique value for ' + evt
                print err


    
def check_bps(bps):
    #print '.......... Checking ' + bps
            check_projection(bps, cs_string)
            fields = [f.name for f in arcpy.ListFields(bps)]
            if 'BPS_NAME' not in fields:
                print '                 BPS_NAME not in fields - BPS layer will not draw'
            if 'GROUPVEG' not in fields:
                print '                 GROUPVEG not in fields - BPS layers will not draw'
            if 'VEG_CODE' not in fields:
                print '                 VEG_CODE MUST BE ADDED TO BPS'
            else:
                with arcpy.da.SearchCursor(bps, "VEG_CODE") as cursor:
                    for row in cursor:
                        if row[0] == ' ':
                            print '                 BLANKS IN BPS VEG_CODE'
                        elif row[0] is None:
                            print '                 BLANKS IN BPS VEG_CODE'
                        else:
                            pass
            try:
                count = arcpy.GetRasterProperties_management(bps, "UNIQUEVALUECOUNT")
                if count <= 5:
                    print '                 5 OR LESS BPS VALUES - CHECK VALUES'
            except Exception as err:
                print '     Could not check unique value for ' + bps
                print err

            


def check_management_inputs(dir, huc_name, huc_id, cs_string):
    vbet = os.path.join(dir, 'VBET/BatchRun_01/02_Analyses/Output_1/Provisional_ValleyBottom_Unedited.shp')
    roads = os.path.join(dir, 'RoadsRails', 'tl_2018_roads.shp')
    rail = os.path.join(dir, 'RoadsRails', 'tl_2018_us_rails.shp')
    ownership = os.path.join(dir, 'LandOwnership', 'NationalSurfaceManagementAgency.shp')
    files = [vbet, roads, rail, ownership]
    for file in files:
        if os.path.exists(file):
            #print '.......... Checking ' + file
            check_projection(file, cs_string)
        else:
            print '     ' + file + ' MISSING.'
    



def check_project_folder(dir, BRAT_folder):
    brat_folder = os.path.join(dir, BRAT_folder)
    if not os.path.exists(brat_folder):
        'Build ' + BRAT_folder + ' for ' + dir



def check_dams(dir):
    dams = os.path.join(dir) 

    
def check_projection(file, cs_string):
    sp = arcpy.Describe(file).spatialReference
    str = sp.exporttostring()
    if str[8:25] == cs_string[8:25]:
        pass
    else:
        print '     ' + file + 'Needs to be reprojected'
                


def check_huc_fields(file):
            fields = [f.name for f in arcpy.ListFields(file)]
            if 'HUC_NAME' not in fields:
                print '     ' + file + 'Needs HUC_NAME field added'
            else:
                pass
            if 'HUC_ID' not in fields:
                print '     ' + file + 'Needs HUC_ID field added'
            else:
                pass


"""        #check for canals
	canals = os.path.join(dir, 'NHD/NHDCanals.shp')
	canals1 = os.path.join(dir, 'BRAT/BatchRun_01/Inputs/04_Conflict/04_Canals/Canals_1/NHDCanals.shp')
	canals2 = os.path.join(dir, 'BRAT/BatchRun_01/Inputs/04_Anthropogenic/04_Canals/Canals_1/NHDCanals.shp'
	if os.path.exists(canals) or os.path.exists(canals1) or os.path.exists(canals2):
	    print huc_name + huc_id
            sp = arcpy.Describe(canals).spatialReference
            str = sp.exporttostring()
            if str[8:25] == cs_string[8:25]:
                pass
            else:
                print '     Needs to be reprojected'
        else:
	    print 'Canals missing for ' + huc_name + huc_id
"""

def unzip_files(zip_folder, output_folder):
    os.chdir(zip_folder)  # change directory from working dir to dir with files
    extension = ".zip"
    for item in os.listdir(zip_folder):  # loop through items in dir
        if item.endswith(extension):  # check for ".zip" extension
            file_name = os.path.abspath(item)  # get full path of files
            zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
            zip_ref.extractall(pf_path)  # extract file to dir
            zip_ref.close()  # close file
            os.remove(file_name)  # delete zipped file



if __name__ == "__main__":
        main()
                 
