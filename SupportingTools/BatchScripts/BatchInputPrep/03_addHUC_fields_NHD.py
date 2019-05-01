import os
import arcpy

pf_path = 'C:\Users\Maggie\Desktop\Idaho\wrk_Data\new'

def main():
    os.chdir(pf_path)
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

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
                arcpy.CalculateField_management(file, 'HUC_ID', huc_id)
        except Exception as err:
            print "Could not add fields for " + dir
            print err
    


if __name__ == "__main__":
    main()
    
