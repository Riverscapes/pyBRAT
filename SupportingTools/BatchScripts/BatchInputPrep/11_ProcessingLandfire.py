import arcpy
import os
arcpy.CheckOutExtension('Spatial')
import sys
sys.path.append('C:/Users/Maggie/Desktop/BatchProcessing/BatchInputPrep')
import LANDFIRE_LUCode

evt = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/00_Projectwide/LANDFIRE/US_200EVT/us_200evt'
bps = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/00_Projectwide/LANDFIRE/US_200BPS/us_200bps'
landfire = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/00_Projectwide/LANDFIRE'
coord_sys = 'NAD 1983 Idaho TM (Meters)'

def main():
    outCS = arcpy.SpatialReference(coord_sys)
    out_evt = os.path.join(landfire, 'LANDFIRE_200EVT.tif')
    out_bps = os.path.join(landfire, 'LANDFIRE_200BPS.tif')

    arcpy.ProjectRaster_management(evt, out_evt, outCS)
    arcpy.ProjectRaster_management(bps, out_bps, outCS)

    landuse = out_evt
    LANDFIRE_LUCode.main(landuse)



if __name__ == '__main__':
    main()
