# -------------------------------------------------------------------------------
# Name:        Segment Network
# Purpose:     This script segments the NHD flowlines shapefile into reaches of
#              user defined length. This script should be run before running
#              the BRAT toolbox.  The only flowlines removed are segments
#              with FCODES pertaining to pipelines.  If the stream is named
#              in the original NHD flowlines shapefile (GNIS_NAME) this is
#              carried over into the output segmented network under the
#              'StreamName' field.
#
# Author:      Sara Bangen (sara.bangen@gmail.com)

# -------------------------------------------------------------------------------

# User defined arguments:

# nhd_flowline_path - path to input flowlines that will be segmented
# outpath - name and path of output segmented flowline network
# interval - reach spacing (in meters)
# min_segLength - minimum segment (reach) length (in meters)

nhd_flowline_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\WestWalker_16050302\NHD\NHDFlowline.shp"
outpath = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\WestWalker_16050302\NHD\NHD_24k_300mReaches.shp"
interval = 300.0 # Default: 300.0
min_segLength = 50.0 # Default: 50.0


def main():
    #  import required modules and extensions
    import os
    import arcpy
    arcpy.CheckOutExtension('Spatial')

    #  environment settings
    arcpy.env.workspace = 'in_memory' # set workspace to temporary workspace
    arcpy.env.overwriteOutput = True  # set to overwrite output
    sr = arcpy.Describe(nhd_flowline_path).spatialReference

    #  select lines from original nhd that are not coded as pipeline (fcdoe 428**)
    arcpy.MakeFeatureLayer_management(nhd_flowline_path, 'nhd_flowline_lyr')
    quer = """ "FCODE" >=42800 AND "FCODE" <= 42813 """
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'NEW_SELECTION', quer)
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'SWITCH_SELECTION')
    flowline_network = arcpy.CopyFeatures_management('nhd_flowline_lyr', 'in_memory/flowline_selection')


    #  dissolve flowline network by name
    #flowline_dissolve_name = arcpy.Dissolve_management(flowline_network, 'in_memory/flowline_dissolve', 'GNIS_NAME', '', 'SINGLE_PART', 'UNSPLIT_LINES')
    tmp_flowline_dissolve_name = arcpy.Dissolve_management(flowline_network, 'in_memory/flowline_dissolve_tmp', 'GNIS_NAME', '',
                                                       'SINGLE_PART', 'UNSPLIT_LINES')
    flowline_dissolve_name = arcpy.Sort_management(tmp_flowline_dissolve_name, 'in_memory/flowline_dissolve', [['Shape', 'DESCENDING']], 'PEANO')

    #  create line id field and line length fields
    #  if fields already exist, delete them
    check_fields = ['LineID', 'LineLen', 'SegID', 'SegLen', 'ReachID', 'ReachLen']
    fields = [f.name for f in arcpy.ListFields(flowline_dissolve_name)]
    for field in fields:
        if field in check_fields:
            arcpy.DeleteField_management(flowline_dissolve_name, field)
    arcpy.AddField_management(flowline_dissolve_name, 'StreamName', 'TEXT', 50)
    arcpy.AddField_management(flowline_dissolve_name, 'StreamID', 'LONG')
    arcpy.AddField_management(flowline_dissolve_name, 'StreamLen', 'DOUBLE')
    ct = 1
    with arcpy.da.UpdateCursor(flowline_dissolve_name, ['FID', 'StreamID', 'Shape@Length', 'StreamLen', 'GNIS_NAME', 'StreamName']) as cursor:
        for row in cursor:
            #row[1] = row[0]
            row[1] = ct
            row[3] = row[2]
            row[5] = row[4]
            ct += 1
            cursor.updateRow(row)



    #  dissolve flowline network
    flowline_dissolve_all = arcpy.Dissolve_management(flowline_network, 'in_memory/flowline_dissolve_all', '', '', 'SINGLE_PART', 'UNSPLIT_LINES')
    arcpy.AddField_management(flowline_dissolve_all, 'SegID', 'LONG')
    arcpy.AddField_management(flowline_dissolve_all, 'SegLen', 'DOUBLE')
    with arcpy.da.UpdateCursor(flowline_dissolve_all, ['FID', 'SegID', 'Shape@Length', 'SegLen']) as cursor:
        for row in cursor:
            row[1] = row[0]
            row[3] = row[2]
            cursor.updateRow(row)


    flowline_int = arcpy.Intersect_analysis([flowline_dissolve_name, flowline_dissolve_all], 'in_memory/flowline_int')

    keep = ['FID', 'Shape', 'StreamID', 'StreamLen', 'StreamName', 'SegID', 'SegLen']
    drop = []
    fields = [f.name for f in arcpy.ListFields(flowline_int)]
    for field in fields:
        if field not in keep:
            drop.append(field)
    arcpy.DeleteField_management(flowline_int, drop)

    #  flip lines so segment points are created from end-start of line rather than start-end
    arcpy.FlipLine_edit(flowline_int)

    #  create points at regular interval along each flowline
    seg_pts = arcpy.CreateFeatureclass_management('in_memory', 'seg_pts', 'POINT', '', 'DISABLED', 'DISABLED', sr)
    with arcpy.da.SearchCursor(flowline_int, ['SHAPE@'], spatial_reference = sr) as search:
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
    flowline_seg = arcpy.SplitLineAtPoint_management(flowline_int, seg_pts, 'in_memory/flowline_seg', 1.0)

    # add and populate reach id and length fields
    arcpy.AddField_management(flowline_seg, 'ReachID', 'SHORT')
    arcpy.AddField_management(flowline_seg, 'ReachLen', 'DOUBLE')
    with arcpy.da.UpdateCursor(flowline_seg, ['FID', 'ReachID', 'Shape@Length', 'ReachLen']) as cursor:
        for row in cursor:
            row[1] = row[0]
            row[3] = row[2]
            cursor.updateRow(row)

    # # get distance along route (LineID) for segment midpoints
    # midpoints =  arcpy.FeatureVerticesToPoints_management(flowline_seg, 'in_memory/midpoints', "MID")
    # arcpy.CopyFeatures_management(midpoints, os.path.join(os.path.dirname(outpath), 'tmp_midpoints.shp'))
    #
    # arcpy.FlipLine_edit(flowline_int)
    # arcpy.AddField_management(flowline_int, 'From_', 'DOUBLE')
    # arcpy.AddField_management(flowline_int, 'To_', 'DOUBLE')
    # with arcpy.da.UpdateCursor(flowline_int, ['SegLen', 'From_', 'To_']) as cursor:
    #     for row in cursor:
    #         row[1] = 0.0
    #         row[2] = row[0]
    #         cursor.updateRow(row)
    #
    #
    # arcpy.CreateRoutes_lr(flowline_int, 'SegID', 'in_memory/flowline_route', 'TWO_FIELDS', 'From_', 'To_')
    # routeTbl = arcpy.LocateFeaturesAlongRoutes_lr(midpoints, 'in_memory/flowline_route', 'SegID',
    #                                                1.0, os.path.join(os.path.dirname(outpath), 'tbl_Routes.dbf'),
    #                                                'RID POINT MEAS')
    #
    # distDict = {}
    # # add reach id distance values to dictionary
    # with arcpy.da.SearchCursor(routeTbl, ['ReachID', 'MEAS']) as cursor:
    #     for row in cursor:
    #         distDict[row[0]] = row[1]
    #
    # # populate dictionary value to output field by ReachID
    # arcpy.AddField_management(flowline_seg, 'ReachDist', 'DOUBLE')
    # with arcpy.da.UpdateCursor(flowline_seg, ['ReachID', 'ReachDist']) as cursor:
    #     for row in cursor:
    #         aKey = row[0]
    #         row[1] = distDict[aKey]
    #         cursor.updateRow(row)
    # #  flip lines back to correct direction
    # arcpy.FlipLine_edit(flowline_seg)

    # save flowline segment output
    arcpy.CopyFeatures_management(flowline_seg, outpath)

    arcpy.Delete_management('in_memory')

if __name__ == '__main__':
    main()