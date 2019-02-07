#  import required modules and extensions
import arcpy
import os
import re
arcpy.CheckOutExtension('Spatial')

pf_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data"
roads_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\Roads\tl_2017_roads.shp"
rails_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\Rails\tl_2017_rails.shp"

def main():

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
        print dir

        # create output folder
        out_folder = os.path.join(pf_path, dir, 'RoadsRails')
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        huc8_shp = os.path.join(pf_path, dir, 'NHD', 'WBDHU8.shp')
        if not os.path.exists(huc8_shp):
            print 'No huc 8 shapefile named WBDHU8.shp'
        else:
            # clip roads to the huc 8 shp
            arcpy.Clip_analysis(roads_path, huc8_shp, os.path.join(out_folder, os.path.basename(roads_path)))
            # clip rails to the huc 8 shp and save only if rails exist
            rails_clip = arcpy.Clip_analysis(rails_path, huc8_shp, 'in_memory/rails_clip')
            count = arcpy.GetCount_management(rails_clip)
            ct = int(count.getOutput(0))
            if ct >= 1:
                arcpy.CopyFeatures_management(tmp_rails, os.path.join(out_folder, os.path.basename(rails_path)))


if __name__ == '__main__':
    main()