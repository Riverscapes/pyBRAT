import arcpy
import os
arcpy.env.overwriteOutput=True
arcpy.CheckOutExtension('Spatial')
from arcpy.sa import *
pf_path = 'C:/Users/Maggie/Desktop/TNC_BRAT/TNC_BRAT/wrk_Data'


def main():
    os.chdir(pf_path)
    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    for dir in dir_list:
	dem = os.path.join(pf_path, dir, 'DEM/NED_DEM_10m.tif')
	huc = os.path.join(pf_path, dir, 'NHD/WBDHU8.shp')
	try:
	    print 'Checking DEM for ' + dir + '.....'

	    # convert DEM to polygon
	    dem_cover = os.path.join(pf_path, dir, 'DEM/DEM_area.shp')
	    dem_class = os.path.join(pf_path, dir, 'DEM/DEM_class.shp')
	    arcpy.sa.Reclassify(dem, 'Value', RemapRange([[0, 100, 1], )
	    arcpy.RasterToPolygon_conversion(dem, dem_cover, 'SIMPLIFY', 'VALUE')

            # get HUC8 area
	    with arcpy.da.SearchCursor(huc, field_names='SHAPE@AREA') as huc_cursor:
                for row in huc_cursor:
                    huc_area = huc_cursor[0]
                    # print '         HUC AREA: ' + str(huc_area)
            dem_area = []
            
            # get DEM area
	    with arcpy.da.SearchCursor(dem_cover, field_names='SHAPE@AREA') as dem_cursor:
		for row in dem_cursor:
                    dem_area.append(row[0])
                    #print '         DEM AREA: ' + str(sum(dem_area))

            # Check for large difference between DEM area and watershed area
            if abs(dem_area - huc_area) > 100000:
                    print '         HUC area: ' + str(huc_area)
                    print '         DEM area: ' + str(dem_area)
            # delete DEM shapefile
            arcpy.Delete_management(dem_cover)
	except Exception as err:
		print err


if __name__ == "__main__":
    main()
