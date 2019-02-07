# -------------------------------------------------------------------------------
# Name:        httpTiger (Batch)
#
# Purpose:     Script downloads all tiger roads within user defined counties
#              shapefile.  Roads are then merged and projected to user
#              defined coordinate system
#
# Notes:       - This script is currently hardcoded to download 2018 roads
#                so if another year is needed code will need to be edited by user
#              - The coord_sys must be identical to corresponding ESRI coordinate system name

# Author:      Sara Bangen (sara.bangen@gmail.com)
# -------------------------------------------------------------------------------

# User defined arguments:

# pf_path - path to parent folder for projectwide data
# counties - path to shapefile of all counties in project area
# out_name - name of output shapefile (include extension)
# coord_sys - coordinate system name that data will be projected to(e.g., 'NAD 1983 California (Teale) Albers (Meters)')

pf_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide"
counties = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\Counties\tl_2017_us_county_ProjectArea.shp"
out_name = 'tl_2018_roads.shp'
coord_sys = 'NAD 1983 California (Teale) Albers (Meters)'


def main():

    import arcpy
    import urllib2
    import os
    import zipfile
    import glob

    # create output roads folder
    roads_folder = os.path.join(pf_path, 'Roads')
    if not os.path.exists(roads_folder):
        os.makedirs(roads_folder)

    # get list of all counties
    geoidList = [row[0] for row in arcpy.da.SearchCursor(counties, "geoid")]

    # downloads roads file for each county
    for geoid in geoidList:
        url_filename = "tl_2018_" + str(geoid) + "_roads.zip"
        download = "https://www2.census.gov/geo/tiger/TIGER2018/ROADS/" + url_filename
        request = urllib2.urlopen(download)
        output = open(roads_folder + '/' + url_filename, "wb")
        output.write(request.read())
        output.close()

    #  create zipped subfolder to temporarily hold zipped folders
    zip_folder = os.path.join(pf_path, 'Roads', 'zipped')
    if not os.path.exists(zip_folder):
        os.makedirs(zip_folder)

    #  unzip all downloaded folders
    os.chdir(roads_folder)  # change directory from working dir to dir with files
    extension = ".zip"
    for item in os.listdir(roads_folder):  # loop through items in dir
        if item.endswith(extension):  # check for ".zip" extension
            file_name = os.path.abspath(item)  # get full path of files
            zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
            zip_ref.extractall(os.path.join(roads_folder, 'zipped'))  # extract file to dir
            zip_ref.close()  # close file
            os.remove(file_name)  # delete zipped file

    # get list of all '*.shp' shapefiles in folder
    os.chdir(os.path.join(roads_folder, 'zipped'))
    shps = glob.glob('*.shp')
    shps_list = ";".join(shps)

    # merge into single shp file
    roads_merged = arcpy.Merge_management(shps_list, 'in_memory/roads_merged')

    # project to coordinate system and save output
    outCS = arcpy.SpatialReference(coord_sys)
    arcpy.Project_management(roads_merged, os.path.join(roads_folder, out_name), outCS)

    # delete any identical roads
    arcpy.DeleteIdentical_management(os.path.join(roads_folder, out_name), ["Shape"])


if __name__ == '__main__':
    main()
