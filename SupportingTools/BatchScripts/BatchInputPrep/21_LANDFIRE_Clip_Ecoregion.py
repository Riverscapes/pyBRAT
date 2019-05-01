import arcpy
import os
proj_bps = 'C:/Users/Maggie/Box/ET_AL/Projects/USA/California/TNC_BRAT/wrk_Data/00_Projectwide/LANDFIRE/LANDFIRE_140BPS.tif'
proj_evt = 'C:/Users/Maggie/Box/ET_AL/Projects/USA/California/TNC_BRAT/wrk_Data/00_Projectwide/LANDFIRE/LANDFIRE_140EVT.tif'
ecoregions_path = 'C:/Users/Maggie/Desktop/EPA_Ecoregions_Level3'


def main():
    os.chdir(ecoregions_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    arcpy.env.overwriteOutput=True
    arcpy.env.resamplingMethod = 'NEAREST'
    for dir in dir_list:
        # clip evt to ecoregion
        try:
	    evt = evt_clip(dir)
	except Exception as err:
	    print err
        # join evt attributes to clip	
	try:
	    join_attributes(evt, proj_evt)
	except Exception as err:
	    print err
	# clip bps to ecoregion
	try:
	    bps = bps_clip(dir)
	except Exception as err:
	    print err
	# join bps attributes to clip
	try:
	    join_attributes(bps, proj_bps)
	except Exception as err:
	    print err


def evt_clip(x):
    print 'Clipping Landfire EVT for: ' + x
    # create output dem folder if it doesn't already exist
    out_folder = os.path.join(ecoregions_path, x)
    out_name = x + '_140EVT.tif'
    # read in huc8 shp and get the huc8 code
    huc8_shp = os.path.join(ecoregions_path, x, x + '_HUC8s.shp')
    #huc8 = str(arcpy.da.SearchCursor(huc8_shp, ['HUC8']).next()[0])
    # clip input landfire raster by huc8_shp
    arcpy.Clip_management(proj_evt, '', os.path.join(out_folder, out_name), huc8_shp, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
    return os.path.join(out_folder, out_name)


def bps_clip(x):
	print 'Clipping Landfire BPS for: ' + x
	# create output dem folder if it doesn't already exist
	out_folder = os.path.join(ecoregions_path, x)
	out_name = x + '_140BPS.tif'
	# read in huc8 shp and get the huc8 code
	huc8_shp = os.path.join(ecoregions_path, x, x + '_HUC8s.shp')
    #huc8 = str(arcpy.da.SearchCursor(huc8_shp, ['HUC8']).next()[0])
    # clip input landfire raster by huc8_shp
	arcpy.Clip_management(proj_bps, '', os.path.join(out_folder, out_name), huc8_shp, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
	return os.path.join(out_folder, out_name)


def join_attributes(x, join_table):
    print '     Joining attributes to ' + x + '.....'
    arcpy.BuildRasterAttributeTable_management(x)
    arcpy.JoinField_management(x, 'Value', join_table, "VALUE")



if __name__ == '__main__':
    main()
    
