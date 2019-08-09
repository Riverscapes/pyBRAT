import arcpy
import os
arcpy.env.overwriteOutput=True

pf_path = 'C:/Users/Maggie/Desktop/TNC_BRAT/TNC_BRAT/wrk_Data'
max_diff_allowed = 100000

def main():

        os.chdir(pf_path)
        # list all folders in parent folder path - note this is not recursive
        dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
        # remove folders in the list that start with '00_' since these aren't our huc8 folders
        for dir in dir_list[:]:
        if dir.startswith('00_'):
                dir_list.remove(dir)

        for dir in dir_list:
                evt = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_140EVT.tif')
                bps = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_140BPS.tif')
                huc = os.path.join(pf_path, dir, 'NHD/WBDHU8.shp')
                try:
                        print 'Checking EVT area for ' + dir + '.....'
                        evt_cover = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_140EVT.shp')
                        arcpy.RasterToPolygon_conversion(evt, evt_cover, 'SIMPLIFY', 'VEG_CODE')
                        with arcpy.da.SearchCursor(huc, field_names='SHAPE@AREA') as huc_cursor:
                                for row in huc_cursor:
                                        huc_area = huc_cursor[0]
                                        #print '         HUC AREA: ' + str(huc_area)
                        evt_area = []
                        with arcpy.da.SearchCursor(evt_cover, field_names='SHAPE@AREA') as evt_cursor:
                                for row in evt_cursor:
                                        evt_area.append(row[0])
                                #print '         EVT AREA: ' + str(sum(evt_area))
                        if abs(huc_area - evt_area) > max_diff_allowed:
                                print '         HUC area: ' + huc_area
                                print '         EVT area: ' + evt_area
                        arcpy.Delete_management(evt_cover)
                except Exception as err:
                        print err

                try:
                        print 'Checking BPS area for ' + dir + '.....'
                        bps_cover = os.path.join(pf_path, dir, 'LANDFIRE/LANDFIRE_140BPS.shp')
                        arcpy.RasterToPolygon_conversion(bps, bps_cover, 'SIMPLIFY', 'VEG_CODE')
                        with arcpy.da.SearchCursor(huc, field_names='SHAPE@AREA') as huc_cursor:
                                for row in huc_cursor:
                                        huc_area = huc_cursor[0]
                                        #print '         HUC AREA: ' + str(huc_area)
                        bps_area = []
                        with arcpy.da.SearchCursor(bps_cover, field_names='SHAPE@AREA') as bps_cursor:
                                for row in bps_cursor:
                                        bps_area.append(row[0])
                                #print '         BPS AREA: ' + str(sum(bps_area))
                        if abs(huc_area - bps_area) > max_diff_allowed:
                                print '         HUC area: ' + huc_area
                                print '         BPS area: ' + bps_area
                        arcpy.Delete_management(bps_cover)
                except Exception as err:
                        print err


if __name__ == "__main__":
        main()
