import arcpy
import os
arcpy.CheckOutExtension('Spatial')
import sys
sys.path.append('C:/Users/a02046349/Desktop/BatchProcessing/BatchInputPrep')
import LANDFIRE_LUCode
arcpy.env.overwriteOutput=True

evt = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/LANDFIRE/US_200EVT/us_200evt.tif'
bps = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/LANDFIRE/US_200BPS/us_200bps.tif'
landfire = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data/00_Projectwide/LANDFIRE'
coord_sys = 'NAD 1983 UTM Zone 12N'

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
