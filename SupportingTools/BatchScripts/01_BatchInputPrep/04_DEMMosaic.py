# -------------------------------------------------------------------------------
# Name:        DEM Mosaic
#
# Purpose:     Script mosaics individual DEM tiles and clips them to a user
#              defined AOI polygon.  Script will mosaic all *.img rasters in the
#              user defined folder path.  Creates hillshade of clipped DEM.
#
# Notes:       - If using a different raster type(e.g., *.tif) you'll need to change this on
#                the 'dems = glob.glob('*.img')' line.
#              - The coord_sys must be identical to corresponding ESRI coordinate system name
#              - The script outputs the initial mosaiced and unclipped raster to the output path.
#                For QA/QC purposes this is not deleted, but can be deleted by user after running the script.
#
# Author:      Sara Bangen (sara.bangen@gmail.com)
# -------------------------------------------------------------------------------

# User defined arguments:

# dem_path - path to folder that contains individual dem tiles
# out_path - path to output folder (where mosaiced and clipped dems will be written)
# out_name - output raster name without file extension(for ETAL users using 10 m DEMS should use 'NED_DEM_10m')
# aoi_path - path to shapefile used to clip final output dem (typically shapefile of study area)
# coord_sys - coordinate system name that DEM will be projected to(e.g., 'NAD 1983 California (Teale) Albers (Meters)')

#  user defined paths
dem_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\DEM\tiles'
out_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\DEM'
out_name = 'NED_DEM_10m'
aoi_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\ProjectBoundary\ProjectArea.shp'
coord_sys = 'NAD 1983 California (Teale) Albers (Meters)'

#  import required modules and extensions
import arcpy
import os
import glob
arcpy.CheckOutExtension('Spatial')


def main():

    # get list of all '*.img' rasters in dem_path folder
    os.chdir(dem_path)
    dems = glob.glob('*.img')
    dem_list = ";".join(dems)

    # environment settings
    arcpy.env.workspace = dem_path
    arcpy.env.resamplingMethod = 'CUBIC'
    outCS = arcpy.SpatialReference(coord_sys)

    # mosaic individual tiles to single raster
    tmp_dem = arcpy.MosaicToNewRaster_management(dem_list, out_path, 'tmp_' + out_name + '.tif', outCS, "32_BIT_FLOAT", "", "1")

    # clip raster to aoi shapefile
    out_dem = arcpy.Clip_management(tmp_dem, '', os.path.join(out_path, out_name + '.tif'), aoi_path, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')

    # create and save hillshade
    arcpy.ResetEnvironments()
    out_hs = arcpy.sa.Hillshade(out_dem, '', '', "NO_SHADOWS")
    out_hs.save(os.path.join(out_path, out_name + '_HS.tif'))

    # check raster cell size
    xResult = arcpy.GetRasterProperties_management(tmp_dem, 'CELLSIZEX')
    print 'Mosaic Raster Cell Size: ' + str(xResult.getOutput(0))
    xResult = arcpy.GetRasterProperties_management(out_dem, 'CELLSIZEX')
    print 'Clipped Raster Cell Size: ' + str(xResult.getOutput(0))

    # clear environment settings
    arcpy.ClearEnvironment("workspace")


if __name__ == '__main__':
    main()
