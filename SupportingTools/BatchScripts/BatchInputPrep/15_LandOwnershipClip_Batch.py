#  import required modules
import arcpy
import os
import re

pf_path = r"C:\Users\a02046349\Desktop\GYE_BRAT\wrk_Data"
proj_bound = r"C:\Users\a02046349\Desktop\GYE_BRAT\wrk_Data\00_Projectwide\ProjectBoundary\GYE_ProjectBoundary_WY.shp"
ownership_path = r"C:\Users\a02046349\Desktop\GYE_BRAT\wrk_Data\00_Projectwide\LandOwnership\NationalSurfaceManagementAgency.shp"
coord_sys = 'NAD 1983 UTM Zone 12N'

def main():
    # set up arcpy environment
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = 'in_memory'
    arcpy.CheckOutExtension('Spatial')

    # clip national layer to project boundary and reproject
    
    land_folder = os.path.join(pf_path, '00_Projectwide/LandOwnership')
    if not os.path.exists(land_folder):
        os.mkdir(land_folder)
    landown_proj = os.path.join(land_folder, 'NationalSurfaceManagementAgency.shp')
    if not os.path.exists(landown_proj):
        print "Clipping national shapefile to project boundary..."
        arcpy.Clip_analysis(ownership_path, proj_bound, 'tmp_ownership')
        outCS = arcpy.SpatialReference(coord_sys)
        print "Projecting project ownership to standardized coordinate system..."
        arcpy.Project_management('tmp_ownership', landown_proj, outCS) 

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

    # for each folder in the list....
    for dir in dir_list:
        print 'Clipping land ownership for ' + dir

        # create output folder
        out_folder = os.path.join(pf_path, dir, 'LandOwnership')
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        huc8_shp = os.path.join(pf_path, dir, 'NHD', 'WBDHU8.shp')
        if not os.path.exists(huc8_shp):
            print 'No huc 8 shapefile named WBDHU8.shp'
        else:
            # clip roads and rails layers to the huc 8 shp
            arcpy.Clip_analysis(landown_proj, huc8_shp, os.path.join(out_folder, 'NationalSurfaceManagementAgency.shp'))


if __name__ == '__main__':
    main()
