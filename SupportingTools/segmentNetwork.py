# -------------------------------------------------------------------------------
# Name:        Segment Network
# Purpose:     Segments a NHD network into reaches before running through the
#              BRAT tools.  This tool should be run after running the Network
#              Builder Tool.
#
# Author:      Sara Bangen (sara.bangen@gmail.com)
#
# Last Updated: 02/2018
# -------------------------------------------------------------------------------

# User defined arguments:

# flowline_path - path to input flowlines that will be segmented
# outpath - name and path of output segmented flowline network
# interval - reach spacing (in meters)
# min_segLength - minimum segment (reach) length (in meters)

flowline_path = r"C:\Users\SaraBangen\Desktop\Et_Al_17050202_BRAT\01_Inputs\03_Network\Network_1\NHD_24k_17050202_Perennial.shp"
outpath = r"C:\Users\SaraBangen\Desktop\Et_Al_17050202_BRAT\tmp_segNetwork2\out_Network.shp"
interval = 300.0 # Default: 300.0
min_segLength = 50.0 # Default: 50.0


def main():
    #  import required modules and extensions
    import arcpy
    arcpy.CheckOutExtension('Spatial')

    #  environment settings
    arcpy.env.workspace = 'in_memory' # set workspace to temporary workspace
    arcpy.env.overwriteOutput = True  # set to overwrite output
    sr = arcpy.Describe(flowline_path).spatialReference

    #  dissolve input flowline network
    flowline_dissolve = arcpy.Dissolve_management(flowline_path, 'in_memory/flowline_dissolve', '', '', 'SINGLE_PART', 'UNSPLIT_LINES')

    #  create line id field and line length fields
    arcpy.AddField_management(flowline_dissolve, 'LineID', 'SHORT')
    arcpy.AddField_management(flowline_dissolve, 'LineLen', 'DOUBLE')
    with arcpy.da.UpdateCursor(flowline_dissolve, ['FID', 'LineID', 'Shape@Length', 'LineLen']) as cursor:
        for row in cursor:
            row[1] = row[0]
            row[3] = row[2]
            cursor.updateRow(row)

    #  flip lines so segment points are created from end-start of line rather than start-end
    arcpy.FlipLine_edit(flowline_dissolve)

    #  create points at regular interval along each flowline
    seg_pts = arcpy.CreateFeatureclass_management('in_memory', 'seg_pts', 'POINT', '', 'DISABLED', 'DISABLED', sr)
    with arcpy.da.SearchCursor(flowline_dissolve, ['SHAPE@'], spatial_reference = sr) as search:
        with arcpy.da.InsertCursor(seg_pts, ['SHAPE@']) as insert:
            for row in search:
                try:
                    lineGeom = row[0]
                    lineLength = row[0].length
                    lineDist = interval
                    while lineDist + min_segLength <= lineLength:
                        newPoint = lineGeom.positionAlongLine(lineDist)
                        insert.insertRow(newPoint)
                        lineDist += interval
                except Exception as e:
                    arcpy.AddMessage(str(e.message))

    # split flowlines at segment interval points
    flowline_seg = arcpy.SplitLineAtPoint_management(flowline_dissolve, seg_pts, 'in_memory/flowline_seg', 1.0)

    # add and populate segment id and length fields
    arcpy.AddField_management(flowline_seg, 'SegID', 'SHORT')
    arcpy.AddField_management(flowline_seg, 'SegLen', 'DOUBLE')
    with arcpy.da.UpdateCursor(flowline_seg, ['FID', 'SegID', 'Shape@Length', 'SegLen']) as cursor:
        for row in cursor:
            row[1] = row[0]
            row[3] = row[2]
            cursor.updateRow(row)

    #  flip lines back to correct direction
    arcpy.FlipLine_edit(flowline_seg)

    # save flowline segment output
    arcpy.CopyFeatures_management(flowline_seg, outpath)

    arcpy.Delete_management('in_memory')

if __name__ == '__main__':
    main()