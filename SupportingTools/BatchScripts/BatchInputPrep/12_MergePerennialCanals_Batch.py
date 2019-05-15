#######################################################################
# Name: MergePerennialCanals_Batch
#
# Purpose: Merges perennial network and canals/ditches shapefile

#
# Author: Maggie Hallerud
#######################################################################

# import required modules
import arcpy
import os
arcpy.CheckOutExtension('Spatial')

# user defined paths
pf_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_PriorityRuns' # project folder path


def main(overwrite = False): # if overwrite = False, will not overwrite current perennial network shapefile if it already exists

    # set up arcpy environment
    arcpy.env.workspace = 'in_memory'
    arcpy.env.overwriteOutput = True
    os.chdir(pf_path)

    # list all folders in parent folder - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))

    # remove folders in the list that start with '00_' since these aren't the HUC8 watersheds
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # merges perennial and canals/ditches shapefiles and save as 'NHD_24k_Perennial_CanalsDitches.shp'
    for dir in dir_list:

        # specifying input perennial and canal shapefiles and output shapefile name
        perennial_shp = os.path.join(pf_path, dir, 'NHD/NHD_24k_Perennial.shp')
        canal_shp = os.path.join(pf_path, dir, 'NHD/NHDCanalsDitches.shp')
        out_shp = os.path.join(pf_path, dir, 'NHD/NHD_24k_Perennial_CanalsDitches.shp')

        # if canals exist then merge with perennial, otherwise just copy perennial
        if not os.path.exists(out_shp) or overwrite is True:
            if os.path.exists(perennial_shp):
                print "Merging perennial and canal shapefiles for " + dir
                try:
                    if os.path.exists(canal_shp):
                        arcpy.Merge_management([perennial_shp, canal_shp], out_shp)
                    else:
                        arcpy.CopyFeatures_management(perennial_shp, out_shp)

                # catch errors and move to the next huc8 folder
                except Exception as err:
                    print "Error with " + dir + ". Exception thrown was: "
                    print err
            else:
                print "WARNING: Merged shapefile can't be created.  Input perennial network does not exist for " + dir
                pass


if __name__ == "__main__":
    main()
