#  import required modules and extensions
import arcpy
import os

arcpy.CheckOutExtension('Spatial')

evt_path = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/00_Projectwide/LANDFIRE/LANDFIRE_200EVT.tif'
bps_path = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/00_Projectwide/LANDFIRE/LANDFIRE_200BPS.tif'
pf_path = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data'

def ras_clip(x, type):
    if type == 'evt':
        ras_path = evt_path
        out_name = 'LANDFIRE_200EVT.tif'
    else:
        ras_path = bps_path
        out_name = 'LANDFIRE_200BPS.tif'
    print 'Clipping Landfire ' + type + ' for: ' + str(x)
    # create output dem folder if it doesn't already exist
    out_folder = os.path.join(pf_path, x, 'LANDFIRE')
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    # read in huc8 shp and get the huc8 code
    huc8_shp = os.path.join(pf_path, x, 'NHD', 'WBDHU8.shp')
    #huc8 = str(arcpy.da.SearchCursor(huc8_shp, ['HUC8']).next()[0])
    # clip input landfire raster by huc8_shp
    arcpy.Clip_management(ras_path, '', os.path.join(out_folder, out_name), huc8_shp, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
    return os.path.join(out_folder, out_name)



def join_attributes(x, join_table):
    print 'Joining attributes for ' + x
    arcpy.BuildRasterAttributeTable_management(x)
    arcpy.JoinField_management(x, 'Value', join_table, "VALUE")



def main():
    # change directory to the parent folder path
    os.chdir(pf_path)
    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)
    # set arcpy environment settings
    arcpy.env.overwriteOutput = 'TRUE'  # overwrite output
    arcpy.env.resamplingMethod = 'NEAREST'  # set resampling method to nearest in case arc does any behind the scenes dem re-sampling
    # run ras_clip function for each huc8 folder
    for dir in dir_list:
        try:
            evt_clip = ras_clip(dir, 'evt')
            join_attributes(evt_clip, evt_path)
        except Exception as err:
            print "Could not clip EVT for " + dir
            print err

        try:
            bps_clip = ras_clip(dir, 'bps')
            join_attributes(bps_clip, bps_path)
        except Exception as err:
            print "Could not clip BPS for " + dir
            print err

    arcpy.ResetEnvironments()
    arcpy.ClearEnvironment("workspace")

if __name__ == '__main__':
    main()
