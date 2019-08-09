# -----------------------------------------------------------------------------------------
# Name:     Tag HUC8s (Batch)
#
# Purpose:  Adds "HUC_NAME" and "HUC_ID" fields to NHD area, flowline, waterbody, perennial network,
#           and 300m reaches and populates with the HUC8 ID and shortened name
#
# Date:     March 2019
# Author:   Maggie Hallerud (maggie.hallerud@aggiemail.usu.edu)
# -----------------------------------------------------------------------------------------

# user-defined inputs
# pf_path - path to project folder for batch processing
pf_path = 'C:/Users/ETAL/Desktop/GYE_BRAT/wrk_Data' 


# load dependencies
import os
import arcpy


def main():

    # make list of all folders  in project folder that don't start with '00_'
    os.chdir(pf_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # add HUC_NAME and HUC_ID to all records in NHD data
    for dir in dir_list:
        print "Adding HUC fields for " + dir
        try:
            huc_name = dir.split('_')[0]
            name = ''.join(['"""', huc_name, '"""'])
            huc_id = dir.split('_')[1]
            area = os.path.join(dir, 'NHD/NHDArea.shp')
            flowline = os.path.join(dir, 'NHD/NHDFlowline.shp')
            waterbody = os.path.join(dir, 'NHD/NHDWaterbody.shp')
            perennial = os.path.join(dir, 'NHD/NHD_24k_Perennial.shp')
            segment = os.path.join(dir, 'NHD/NHD_24k_300mReaches.shp')
            files = [area, flowline, waterbody, perennial, segment]
            for file in files:
                if os.path.exists(file):
                    fields = arcpy.ListFields(file)
                    if 'HUC_NAME' in fields:
                        arcpy.DeleteField_management(file, 'HUC_NAME')
                    else:
                        pass
                    arcpy.AddField_management(file, 'HUC_NAME', 'TEXT')
                    if 'HUC_ID' in fields:
                        arcpy.DeleteField_management(file, 'HUC_ID')
                    else:
                        pass
                    arcpy.AddField_management(file, 'HUC_ID', 'TEXT')
                    arcpy.CalculateField_management(file, 'HUC_NAME', name, "PYTHON_9.3")
                    arcpy.CalculateField_management(file, 'HUC_ID', huc_id, "PYTHON_9.3")
        except Exception as err:
            print "Could not add fields for " + dir
            print err
    

if __name__ == "__main__":
    main()
