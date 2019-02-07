#  import required modules and extensions
import arcpy
import os

arcpy.CheckOutExtension('Spatial')

evt_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\LANDFIRE\LANDFIRE_140EVT.tif"
bps_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\LANDFIRE\LANDFIRE_140BPS.tif"
pf_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data"

def ras_clip(x, type):
    if type == 'evt':
        ras_path = evt_path
        out_name = 'LANDFIRE_140EVT.tif'
    else:
        ras_path = bps_path
        out_name = 'LANDFIRE_140BPS.tif'
    print 'Clipping Landfire for: ' + str(x)
    # create output dem folder if it doesn't already exist
    out_folder = os.path.join(pf_path, x, 'LANDFIRE')
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    # read in huc8 shp and get the huc8 code
    huc8_shp = os.path.join(pf_path, x, 'NHD', 'WBDHU8.shp')
    #huc8 = str(arcpy.da.SearchCursor(huc8_shp, ['HUC8']).next()[0])
    # clip input landfire raster by huc8_shp
    arcpy.Clip_management(ras_path, '', os.path.join(out_folder, out_name), huc8_shp, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')



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
    # run dem_clip function for each huc8 folder
    for dir in dir_list:
        ras_clip(dir, 'evt')
        #ras_clip(dir, 'bps')

    arcpy.ResetEnvironments()
    arcpy.ClearEnvironment("workspace")

if __name__ == '__main__':
    main()