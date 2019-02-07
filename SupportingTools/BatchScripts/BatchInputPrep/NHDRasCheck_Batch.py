#  import required modules and extensions
import arcpy
import os
import glob
arcpy.CheckOutExtension('Spatial')

dem_path = r'C:\etal\Shared\Projects\USA\Idaho\BRAT\FY1819\wrk_Data\00_Statewide\DEM'
scratch = r'C:\etal\Shared\Projects\USA\Idaho\BRAT\FY1819\wrk_Data\00_Statewide\scratch'
coord_sys = 'NAD 1983 Idaho TM (Meters)'

def main():
    outCS = arcpy.SpatialReference(coord_sys)
    os.chdir(dem_path)
    dems = glob.glob('*.img')
    print dems
    index = 1
    for dem in dems:
        tmp_dem = arcpy.ProjectRaster_management(os.path.join(dem_path, dem), os.path.join(scratch, 'dem_' + str(index) + '.img'), outCS, "CUBIC")
        index += 1
        xResult = arcpy.GetRasterProperties_management(tmp_dem, 'CELLSIZEX')
        yResult = arcpy.GetRasterProperties_management(tmp_dem, 'CELLSIZEY')
        print 'Cell Size X: ' + str(xResult.getOutput(0))
        print 'Cell Size Y: ' + str(yResult.getOutput(0))
        arcpy.Delete_management(tmp_dem)

if __name__ == '__main__':
    main()