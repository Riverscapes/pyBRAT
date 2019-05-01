#  import required modules and extensions
import arcpy
import os
arcpy.CheckOutExtension('Spatial')

ras_path = r'C:\Users\Maggie\Desktop\Idaho\wrk_Data\00_Projectwide\LANDFIRE\tiles'
out_path = os.path.dirname(ras_path)
#scratch = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\scratch'
aoi_path = r'C:\Users\Maggie\Desktop\Idaho\wrk_Data\00_Projectwide\ProjectBoundary\WBDHU8_ProjectArea.shp'
coord_sys = 'NAD 1983 Idaho TM (Meters)'


def main():

    evt_list = []
    bps_list = []

    def search_files(directory, extension):
        extension = extension.lower()
        for dirpath, dirnames, files in os.walk(directory):
            for name in files:
                if extension and name.lower().endswith(extension):
                    #print(os.path.join(ras_path, dirpath, name))
                    if 'BPS' in name:
                        bps_list.append(os.path.join(ras_path, dirpath, name))
                    elif 'EVT' in name:
                        evt_list.append(os.path.join(ras_path, dirpath, name))
                    else:
                        pass

    search_files(directory = ras_path, extension = '.tif')

    arcpy.env.overwriteOutput = 'TRUE'
    arcpy.env.resamplingMethod = 'NEAREST'
    outCS = arcpy.SpatialReference(coord_sys)

    tmp_bps_ras = arcpy.MosaicToNewRaster_management(bps_list, out_path, 'tmp_LANDFIRE_140BPS.tif', outCS, "16_BIT_SIGNED", "", "1")

    bps_tbl_list = []
    index = 1
    for ras in bps_list:
        tbl_path = os.path.join(out_path, 'tmp_bps_tbl_' + str(index) + '.dbf')
        arcpy.CopyRows_management(ras, tbl_path)
        bps_tbl_list.append(tbl_path)
        index += 1
    print bps_tbl_list

    bps_tbl = arcpy.Merge_management(bps_tbl_list, os.path.join(out_path, 'tmp_bps_tbl.dbf'))
    arcpy.DeleteIdentical_management(bps_tbl, ['Value'])

    arcpy.BuildRasterAttributeTable_management(tmp_bps_ras, "Overwrite")

    tbl_fields = [f.name for f in arcpy.ListFields(bps_tbl)]
    join_fields = []
    drop = ['Count', 'Value', 'OID']
    for field in tbl_fields:
        if field not in drop:
            join_fields.append(field)
    print join_fields

    arcpy.JoinField_management(tmp_bps_ras, 'Value', bps_tbl, 'VALUE', join_fields)

    arcpy.Clip_management(tmp_bps_ras, '', os.path.join(out_path, 'LANDFIRE_140BPS.tif'), aoi_path, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')

    tmp_evt_ras = arcpy.MosaicToNewRaster_management(evt_list, out_path, 'tmp_LANDFIRE_140EVT.tif', outCS, "16_BIT_SIGNED", "", "1")

    evt_tbl_list = []
    index = 1
    for ras in evt_list:
        tbl_path = os.path.join(out_path, 'tmp_evt_tbl_' + str(index) + '.dbf')
        arcpy.CopyRows_management(ras, tbl_path)
        evt_tbl_list.append(tbl_path)
        index += 1
    print evt_tbl_list

    evt_tbl = arcpy.Merge_management(evt_tbl_list, os.path.join(out_path, 'tmp_evt_tbl.dbf'))
    arcpy.DeleteIdentical_management(evt_tbl, ['Value'])

    arcpy.BuildRasterAttributeTable_management(tmp_evt_ras, "Overwrite")

    tbl_fields = [f.name for f in arcpy.ListFields(evt_tbl)]
    join_fields = []
    drop = ['Count', 'Value', 'OID']
    for field in tbl_fields:
        if field not in drop:
            join_fields.append(field)
    print join_fields

    arcpy.JoinField_management(tmp_evt_ras, 'Value', evt_tbl, 'VALUE', join_fields)

    arcpy.Clip_management(tmp_evt_ras, '', os.path.join(out_path, 'LANDFIRE_140EVT.tif'), aoi_path, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')


    # xResult = arcpy.GetRasterProperties_management(evt_ras, 'CELLSIZEX')
    # yResult = arcpy.GetRasterProperties_management(evt_ras, 'CELLSIZEY')
    # print 'Cell Size X: ' + str(xResult.getOutput(0))
    # print 'Cell Size Y: ' + str(yResult.getOutput(0))

    arcpy.ResetEnvironments()
    arcpy.ClearEnvironment("workspace")

if __name__ == '__main__':
    main()
