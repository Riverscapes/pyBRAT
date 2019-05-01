# -------------------------------------------------------------------------------
# Name:        Merge LANDFIRE (Batch)
#
# Purpose:     Script merges LANDFIRE data from separate years within HUC boundaries.
#              The output is written to the LANDFIRE folder within each HUC8 folder
#
# Notes:       - The scripts assumes data are in standard ETAL BRAT project
#                folder and file structure.  Specifically:
#                i) individual basin folders (e.g., Applegate_17100309) are directly
#                   under the user defined parent folder (typically the 'wrk_Data' folder)
#               ii) a 'NHD' folder is directly under each individual basin folder and
#                   contains a 'WBDHU8.shp' polygon
#               - The script will execute on all subfolders in the parent folder EXCEPT
#                 those that start with a '00_*' (e.g., '00_Projectwide')
#               iii) project-wide LANDFIRE EVT and BPS files are found in a '00_Projectwide/LANDFIRE'
#                   folder within the project folder
#               iv) HUC8 LANDFIRE .tif files are found in LANDFIRE folders within each HUC8 folder
#                    and under the name 'LANDFIRE_xxxEVT.tif' or 'LANDFIRE_xxxBPS.tif'
#
# Author:      Maggie Hallerud (maggie.hallerud@aggiemail.usu.edu)
# -------------------------------------------------------------------------------

import arcpy
import os
import sys
sys.path.append('C:/Users/Maggie/Desktop/BatchProcessing/BatchInputPrep')
import LANDFIRE_LUCode as lu_code

pf_path = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data'
evt_out_name_with_ext = 'LANDFIRE_EVT_Merge.tif'
bps_out_name_with_ext = 'LANDFIRE_BPS_Merge.tif'
#coord_sys = 'NAD 1983 California (Teale) Albers (Meters)'
coord_sys = 'NAD 1983 Idaho TM (Meters)'


def main():
    arcpy.env.overwriteOutput = True
    
    outCS = arcpy.SpatialReference(coord_sys)
    proj_evt140 = os.path.join(pf_path, '00_Projectwide/LANDFIRE/LANDFIRE_140EVT.tif')
    proj_evt200 = os.path.join(pf_path, '00_Projectwide/LANDFIRE/LANDFIRE_200EVT.tif')
    proj_bps140 = os.path.join(pf_path, '00_Projectwide/LANDFIRE/LANDFIRE_140BPS.tif')
    proj_bps200 = os.path.join(pf_path, '00_Projectwide/LANDFIRE/LANDFIRE_200BPS.tif')

    os.chdir(pf_path)
    
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    for dir in dir_list:
        evt_old = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_140EVT.tif')
        bps_old = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_140BPS.tif')
        if os.path.exists(evt_old):            
            try:
                evt_merge(dir)
            except Exception as err:
                print "EVT MERGE FAILED FOR " + dir + ". Exception thrown was:"
                print err
                
        if os.path.exists(bps_old):
            try:
                bps_merge(dir)
            except Exception as err:
                print "BPS MERGE FAILED FOR " + dir + ". Exception thrown was:"
                print err

                    
def evt_merge(x):
    print 'Starting EVT merge for ' + x
    hu8 = os.path.join(pf_path, x, 'NHD/WBDHU8.shp')
    evt_new = os.path.join(pf_path, x, 'LANDFIRE/LANDFIRE_200EVT.tif')
    evt_old = os.path.join(pf_path, x, 'LANDFIRE/LANDFIRE_140EVT.tif')
    evt_erase = os.path.join(pf_path, x, 'LANDFIRE/EVT_2016_Erase.shp')
    evt_clip_name = os.path.join(pf_path, x, 'LANDFIRE/EVT_2014_clip.tif')
    evt_new_shp = os.path.join(pf_path, x, 'LANDFIRE/LANDFIRE_200EVT.shp')
    print '         Converting LANDFIRE 200EVT to shapefile...'
    arcpy.RasterToPolygon_conversion(evt_new, evt_new_shp)
    print '         Erasing LANDFIRE 200EVT coverage from watershed boundary & buffering...'
    arcpy.Erase_analysis(hu8, evt_new_shp, evt_erase)
    evt_erase_buffer = os.path.join(pf_path, x, 'LANDFIRE/EVT_2016_Erase_30m.shp')
    arcpy.Buffer_analysis(evt_erase, evt_erase_buffer, "30 Meters")
    print '         Clipping LANDFIRE 140EVT to watershed area not covered by 200 EVT...'
    clip = arcpy.Clip_management(in_raster=evt_old, rectangle=None, out_raster=evt_clip_name, in_template_dataset=evt_erase_buffer, nodata_value='', clipping_geometry='ClippingGeometry')
    print '         Creating dataset to store output...'
    evt_output = arcpy.CreateRasterDataset_management(os.path.join(pf_path, x, 'LANDFIRE'), evt_out_name_with_ext, None, '16_BIT_SIGNED', outCS, 1)
    print '         Merging LANDFIRE EVT rasters...'
    arcpy.Mosaic_management(inputs=[clip, evt_new], target=evt_output, mosaic_type="LAST")
    print '         Creating attribute table for merged output...'
    arcpy.BuildRasterAttributeTable_management(evt_output)
    arcpy.JoinField_management(evt_output, 'Value', proj_evt140, 'VALUE')
    arcpy.JoinField_management(evt_output, 'Value', proj_evt200, 'VALUE')
    with arcpy.da.UpdateCursor(evt_output, field_names = ['EVT_NAME', 'CLASSNAME', 'EVT_CLASS', 'EVT_CLAS_1', 'EVT_PHYS', 'EVT_PHYS_1']) as cursor:
        for row in cursor:                
            if row[0] == ' ':
                row[0] = row[1]
            else:
                pass

            if row[1] == ' ':
                row[1] = row[0]
            else:
                pass

            if row[2] == ' ':
                row[2] = row[3]
            else:
                pass

            if row[4] == ' ':
                row[4] = row[5]
            else:
                pass
            cursor.updateRow(row)
    lu_code.main(evt_output)



def bps_merge(x):
    print 'Starting BPS merge for ' + x
    hu8 = os.path.join(pf_path, x, 'NHD/WBDHU8.shp')
    bps_new = os.path.join(pf_path, x, 'LANDFIRE/LANDFIRE_200BPS.tif')
    bps_old = os.path.join(pf_path, x, 'LANDFIRE/LANDFIRE_140BPS.tif')
    bps_erase = os.path.join(pf_path, x, 'LANDFIRE/BPS_2016_Erase.shp')
    bps_clip_name = os.path.join(pf_path, x, 'LANDFIRE/BPS_2014_clip.tif')
    bps_new_shp = os.path.join(pf_path, x, 'LANDFIRE/LANDFIRE_200BPS.shp')
    print '         Converting LANDFIRE 200BPS to shapefile...'
    arcpy.RasterToPolygon_conversion(bps_new, bps_new_shp)
    print '         Erasing LANDFIRE 200BPS coverage from watershed boundary & buffering...'
    arcpy.Erase_analysis(hu8, bps_new_shp, bps_erase)
    bps_erase_buffer = os.path.join(pf_path, x, 'LANDFIRE/BPS_2016_Erase_30m.shp')
    arcpy.Buffer_analysis(bps_erase, bps_erase_buffer, "30 Meters")
    print '         Clipping LANDFIRE 140BPS to watershed area not covered by 200BPS...'
    clip = arcpy.Clip_management(in_raster=bps_old, rectangle=None, out_raster=bps_clip_name, in_template_dataset=bps_erase_buffer, nodata_value='', clipping_geometry='ClippingGeometry')
    print '         Creating dataset to store output...'
    bps_output = arcpy.CreateRasterDataset_management(os.path.join(pf_path, x, 'LANDFIRE'), bps_out_name_with_ext, None, '16_BIT_SIGNED', outCS, 1)
    print '         Merging LANDFIRE BPS rasters...'
    arcpy.Mosaic_management(inputs=[clip, bps_new], target=bps_output, mosaic_type="LAST")
    print '         Creating attribute table for merged output...'
    arcpy.BuildRasterAttributeTable_management(bps_output)
    arcpy.JoinField_management(bps_output, 'Value', proj_bps140, 'VALUE')
    arcpy.JoinField_management(bps_output, 'Value', proj_bps200, 'VALUE')
    with arcpy.da.UpdateCursor(bps_output, field_names = ['BPS_NAME', 'BPS_NAME_1', 'GROUPVEG', 'GROUPVEG_1']) as cursor:
        for row in cursor:                
            if row[0] == ' ':
                row[0] = row[1]
            else:
                pass

            if row[1] == ' ':
                row[1] = row[0]
            else:
                pass
                    
            if row[2] == ' ':
                row[2] = row[3]
            else:
                pass
            cursor.updateRow(row)


            
if __name__ == '__main__':
    main()
