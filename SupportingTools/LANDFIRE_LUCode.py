#  import required modules and extensions
import arcpy
import os
arcpy.CheckOutExtension('Spatial')

# path to landuse raster
landuse = r"C:\xxx\01_Inputs\05_Conflict\05_Land_Use\Land_Use_1\us_140evt.tif"

def main():

    #  environment settings
    arcpy.env.workspace = 'in_memory' # set workspace to temporary workspace
    arcpy.env.overwriteOutput = True  # set to overwrite output

    luDict = {
        "Agricultural-Aquaculture": 0.66,
        "Agricultural-Bush fruit and berries": 0.66,
        "Agricultural-Close Grown Crop": 0.66,
        "Agricultural-Fallow/Idle Cropland": 0.33,
        "Agricultural-Orchard": 0.66,
        "Agricultural-Pasture and Hayland": 0.33,
        "Agricultural-Row Crop": 0.66,
        "Agricultural-Row Crop-Close Grown Crop": 0.66,
        "Agricultural-Vineyard": 0.66,
        "Agricultural-Wheat": 0.66,
        "Developed-High Intensity": 1.0,
        "Developed-Medium Intensity": 1.0,
        "Developed-Low Intensity": 1.0,
        "Developed-Roads": 1.0,
        "Developed-Upland Deciduous Forest": 1.0,
        "Developed-Upland Evergreen Forest": 1.0,
        "Developed-Upland Herbaceous": 1.0,
        "Developed-Upland Mixed Forest": 1.0,
        "Developed-Upland Shrubland": 1.0,
        "Managed Tree Plantation - Northern and Central Hardwood and Conifer Plantation Group": 0.66,
        "Managed Tree Plantation - Southeast Conifer and Hardwood Plantation Group": 0.66,
        "Quarries-Strip Mines-Gravel Pits": 1.0
    }

    fields = arcpy.ListFields(landuse)
    if "LU_CODE" not in fields:
        arcpy.AddField_management(landuse, "LU_CODE", "DOUBLE")
    if "LUI_Class" not in fields:
        arcpy.AddField_management(landuse, "LUI_Class", "TEXT", 10)
    with arcpy.da.UpdateCursor(landuse, ["EVT_GP_N", "LU_CODE", "LUI_Class"]) as cursor:
        for row in cursor:
            keyName = row[0]
            if keyName in luDict:
                row[1] = luDict[keyName]
            else:
                row[1] = 0.0
            if row[1] >= 1.0:
                row[2] = 'High'
            elif row[1] <= 0.0:
                row[2] = 'VeryLow'
            elif row[1] <= 0.33:
                row[2] = 'Low'
            else:
                row[2] = 'Moderate'
            cursor.updateRow(row)

    #arcpy.Delete_management('in_memory')

if __name__ == '__main__':
    main()