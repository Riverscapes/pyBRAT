# -------------------------------------------------------------------------------
# Name:        NHD Clip (Batch)
#
# Purpose:     Script clips project-scale NHD data to individual HUC8 polygon shapefiles.
#              Also selects NHD flowlines with Canal FCODE and saves them to shapefile (if exist).
#              Output shapefiles are projected to user defined coordinate system and
#              written to a 'NHD' subfolder for each basin (which is created
#              if it doesn't already exist).
#
# Notes:       - The script clips/projects/saves only the NHD data that are pertinent
#                to BRAT tools (i.e., WBDHU8, NHDFlowline, NHDArea, NHDWaterbody)
#              - The coord_sys must be identical to corresponding ESRI coordinate system name
#              - The scripts assumes data are in standard ETAL BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)

# Author:      Sara Bangen (sara.bangen@gmail.com)
# -------------------------------------------------------------------------------

# User defined arguments:

# pf_path - path to parent folder that holds HUC8 folders
# nhd_path - path to folder that contains project NHD data
# huc8_aoi_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\NHD\WBDHU8_ProjectArea.shp'
# coord_sys - coordinate system name that data will be projected to(e.g., 'NAD 1983 California (Teale) Albers (Meters)')

pf_path = r"C:\Users\Maggie\Desktop\Idaho\wrk_Data"
nhd_path = r"C:\Users\Maggie\Desktop\Idaho\wrk_Data\00_Projectwide\NHD"
huc8_aoi_path = r"C:\Users\Maggie\Desktop\Idaho\wrk_Data\00_Projectwide\NHD\WBDHU8.shp"
coord_sys = 'NAD 1983 Idaho TM (Meters)'

#  import required modules and extensions
import arcpy
import os
import re
arcpy.CheckOutExtension('Spatial')


def main():

    #  environment settings
    arcpy.env.workspace = 'in_memory' # set workspace to temporary workspace
    arcpy.env.overwriteOutput = True  # set to overwrite output

    # project nhd layers and save to 'projected' sub folder
    print 'Projecting data...'

    proj_folder = os.path.join(nhd_path, 'Projected')
    if not os.path.exists(proj_folder):
        os.makedirs(proj_folder)

    outCS = arcpy.SpatialReference(coord_sys)
    flowlines = arcpy.Project_management(os.path.join(nhd_path, 'NHDFlowline.shp'), os.path.join(proj_folder, 'NHDFlowline.shp'), outCS)
    areas = arcpy.Project_management(os.path.join(nhd_path, 'NHDArea.shp'), os.path.join(proj_folder, 'NHDArea.shp'), outCS)
    wbodies = arcpy.Project_management(os.path.join(nhd_path, 'NHDWaterbody.shp'), os.path.join(proj_folder, 'NHDWaterbody.shp'), outCS)
    huc8s = arcpy.Project_management(huc8_aoi_path, os.path.join(proj_folder, os.path.basename(huc8_aoi_path)), outCS)

    # create list of all huc 8 ids
    huc8s_list = [row[0] for row in arcpy.da.SearchCursor(huc8s, 'HUC8')]

    # for each huc 8 id in the list....
    for huc8 in huc8s_list:
        # compress HUC8 name
        huc8_shp = arcpy.Select_analysis(huc8s, 'in_memory/huc8_' + str(huc8), "HUC8 = '%s'" % str(huc8))
        huc8_name = str(arcpy.da.SearchCursor(huc8_shp, ['NAME']).next()[0])
        huc8_name_new = re.sub(r'\W+', '', huc8_name)

        # print subdir name to track script progress for user
        print 'Clipping NHD data for: ' + str(huc8_name)

        # create NHD output folder if it doesn't already exist
        nhd_folder = os.path.join(pf_path, huc8_name_new + '_' + str(huc8), 'NHD')
        if not os.path.exists(nhd_folder):
            os.makedirs(nhd_folder)

        # clip and select flowlines that aren't coded as pipelines (fype 428), underground conduits (ftype 420), or coastline (ftype 566)
        tmp_huc8_flowlines = arcpy.Clip_analysis(flowlines, huc8_shp, 'in_memory/tmp_flowlines')
        arcpy.MakeFeatureLayer_management(tmp_huc8_flowlines, 'tmp_huc8_flowlines_lyr')
        quer = """ "FTYPE" = 428 OR "FTYPE" = 420 OR "FTYPE" = 566 """
        arcpy.SelectLayerByAttribute_management('tmp_huc8_flowlines_lyr', 'NEW_SELECTION', quer)
        arcpy.SelectLayerByAttribute_management('tmp_huc8_flowlines_lyr', 'SWITCH_SELECTION')
        huc8_flowlines = arcpy.CopyFeatures_management('tmp_huc8_flowlines_lyr', os.path.join(nhd_folder, 'NHDFlowline.shp'))

        # clip rest of nhd layers to the huc 8 shp
        arcpy.Clip_analysis(areas, huc8_shp, os.path.join(nhd_folder, 'NHDArea.shp'))
        arcpy.Clip_analysis(wbodies, huc8_shp, os.path.join(nhd_folder, 'NHDWaterbody.shp'))
        arcpy.CopyFeatures_management(huc8_shp, os.path.join(nhd_folder, 'WBDHU8.shp'))

        # delete identical flowlines (isn't always the case but found is an issue with some nhd polylines)
        arcpy.DeleteIdentical_management(huc8_flowlines, ['Shape'])

        #  select lines that are coded as canals (ftype 336)
        #  note: only creates 'NHDCanals.shp' if there are canal flowlines
        arcpy.MakeFeatureLayer_management(huc8_flowlines, 'huc8_flowlines_lyr')
        quer = """ "FTYPE" = 336 """
        arcpy.SelectLayerByAttribute_management('huc8_flowlines_lyr', 'NEW_SELECTION', quer)
        count = arcpy.GetCount_management('huc8_flowlines_lyr')
        ct = int(count.getOutput(0))
        if ct >= 1:
            arcpy.CopyFeatures_management('huc8_flowlines_lyr', os.path.join(nhd_folder, 'NHDCanals.shp'))
        arcpy.SelectLayerByAttribute_management('huc8_flowlines_lyr', "CLEAR_SELECTION")


if __name__ == '__main__':
    main()
