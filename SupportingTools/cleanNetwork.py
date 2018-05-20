# -------------------------------------------------------------------------------
# Name:        Clean Network
# Purpose:     Script helps when 'manually' creating perennial network.
#              Cleans up network by i) removing flowlines less than
#              user defined length as long as there is no upstream
#              connected flowline, ii) filling flowline gaps
#              in input network that are within nhd area and nhd
#              waterbody polygons (copied from original nhd
#              flowlines once identified).  Should be run before
#              running the 'checkNetwork' script.
#
# Author:      Sara Bangen (sara.bangen@gmail.com)
#
# -------------------------------------------------------------------------------

# User defined arguments:

# flowline_path - path to flowline to clean-up
# nhd_orig_flowline_path - path to original nhd flowline shapefile
# nhd_area_path - path to nhd area shapefile
# nhd_waterbody_path - path to nhd waterbody shapefile
# outpath - name and path of output flowline network
# min_lineLength - minimum flowline length


flowline_path = r"C:\etal\Shared\Projects\USA\Idaho\BRAT\FY1819\wrk_Data\Lemhi_17060204\CleanTest\NHD_24k_Perennial.shp"
nhd_orig_flowline_path = r"C:\etal\Shared\Projects\USA\Idaho\BRAT\FY1819\wrk_Data\Lemhi_17060204\NHD\NHDFlowline.shp"
nhd_area_path = r"C:\etal\Shared\Projects\USA\Idaho\BRAT\FY1819\wrk_Data\Lemhi_17060204\NHD\NHDArea.shp"
nhd_waterbody_path = r"C:\etal\Shared\Projects\USA\Idaho\BRAT\FY1819\wrk_Data\Lemhi_17060204\NHD\NHDWaterbody.shp"
outpath = r"C:\etal\Shared\Projects\USA\Idaho\BRAT\FY1819\wrk_Data\Lemhi_17060204\CleanTest\Cleaned_inMem.shp"
min_lineLength = 50.0


def main():

    #  import required modules and extensions
    import arcpy
    import os

    #  environment settings
    arcpy.env.workspace = 'in_memory' # set workspace to temporary workspace
    arcpy.env.overwriteOutput = 'TRUE'

    # make a temp copy of input flowlines
    flowlines = arcpy.CopyFeatures_management(flowline_path, 'in_memory/flowlines')

    # check if Length field exists, if not create it
    field_names = [f.name for f in arcpy.ListFields(flowlines)]
    if 'Length' not in field_names:
        arcpy.AddField_management(flowlines, 'Length', 'DOUBLE')
    # re-calculate Length field in case it hasn't been updated
    with arcpy.da.UpdateCursor(flowlines, ['SHAPE@Length', 'Length']) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)

    # check if SegID field exists, if not create it
    if 'SegID' not in field_names:
        arcpy.AddField_management(flowlines, 'SegID', 'SHORT')
        with arcpy.da.UpdateCursor(flowlines, ['FID', 'SegID']) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

    # make layer from flowlines for selection
    arcpy.MakeFeatureLayer_management(flowlines, "flowlines_lyr")

    # -- delete short flowlines segments--
    # select flowlines that are less than designated length
    arcpy.SelectLayerByAttribute_management("flowlines_lyr", "NEW_SELECTION", '"Length" < ' + str(min_lineLength))

    # create feature class from selected short flowlines
    short_flowlines = arcpy.CopyFeatures_management("flowlines_lyr", 'in_memory/short_flowlines')

    # join selected short flowlines with input flowlines to get count of intersecting features
    short_flowlines_join = arcpy.SpatialJoin_analysis(short_flowlines, flowlines, 'in_memory/short_flowlines_join', 'JOIN_ONE_TO_ONE', 'KEEP_ALL', '', 'INTERSECT')

    # delete short flowlines that intersect > 3 flowlines
    # note: here we only keep flowlines that are either
    #       1. isolated (intersect only 1 flowlines i.e., itself)
    #       2. short 'tribs' that flow into a flowline but without another feature upstream
    with arcpy.da.UpdateCursor(short_flowlines_join, ['Join_Count']) as cursor:
        for row in cursor:
            if row[0] > 3:
                cursor.deleteRow()
    # create list of short flowline 'SegID' fields to remove from input flowlines and delete them
    drop_list = [row[0] for row in arcpy.da.SearchCursor(short_flowlines_join, ['SegID'])]
    with arcpy.da.UpdateCursor(flowlines, ['SegID']) as cursor:
        for row in cursor:
            if row[0] in drop_list:
                cursor.deleteRow()

    # --find and fix gaps in flowline network--
    # need this fix to resolve issues where flowlines were omitted in nhd area and waterbody polygons

    # -get missing segments in nhd area polygons-

    # create points at start and end of each flowlines
    line_pts = arcpy.FeatureVerticesToPoints_management(flowlines, 'in_memory/line_pts', 'BOTH_ENDS')

    # join start/end points with flowlines to get intersecting flowline count
    # here we want to isolate points that aren't connected to another line that indicate gaps in network
    line_pts_join = arcpy.SpatialJoin_analysis(line_pts, flowlines, 'in_memory/line_pts_join', 'JOIN_ONE_TO_ONE', 'KEEP_ALL', '', 'INTERSECT')

    # remove points that intersect > 1 line feature (these are not on gaps)
    with arcpy.da.UpdateCursor(line_pts_join, ['Join_Count']) as cursor:
        for row in cursor:
            if row[0] > 1:
                cursor.deleteRow()

    # select points that intersect nhd area polygon
    arcpy.MakeFeatureLayer_management(line_pts_join, "line_pts_join_lyr")
    arcpy.SelectLayerByLocation_management("line_pts_join_lyr", 'INTERSECT', nhd_area_path, '1 Meters', 'NEW_SELECTION')

    # create feature class from selected end points
    line_pts_area = arcpy.CopyFeatures_management("line_pts_join_lyr", 'in_memory/line_pts_area')

    # find flowlines from orignal nhd that intersect selected end points and aren't in input flowline network
    arcpy.MakeFeatureLayer_management(nhd_orig_flowline_path, "nhd_orig_lyr")
    arcpy.SelectLayerByLocation_management("nhd_orig_lyr", 'INTERSECT', line_pts_area, '1 Meters', 'NEW_SELECTION')
    arcpy.SelectLayerByLocation_management("nhd_orig_lyr", 'SHARE_A_LINE_SEGMENT_WITH', flowlines, '', 'REMOVE_FROM_SELECTION')

    # create feature class from selected gap lines
    line_gaps = arcpy.CopyFeatures_management("nhd_orig_lyr", 'in_memory/line_gaps')

    # create insert gap lines into flowlines copy
    with arcpy.da.InsertCursor(flowlines, ["SHAPE@"]) as iCursor:
        with arcpy.da.SearchCursor(line_gaps, ["SHAPE@"]) as sCursor:
            for row in sCursor:
                iCursor.insertRow([row[0]])

    # # -get missing segments in nhd waterbody polygons-
    #
    # # find line end points that intersect waterbody polygons
    # arcpy.SelectLayerByLocation_management("line_pts_join_lyr", 'INTERSECT', nhd_waterbody_path, '1 Meters', 'NEW_SELECTION')
    #
    # # create feature class from selected end points
    # line_pts_wbody = arcpy.CopyFeatures_management("line_pts_join_lyr", 'in_memory/line_pts_wbody')
    #
    # # delete previous join count field
    # fields = [f.name for f in arcpy.ListFields(line_pts_wbody)]
    # for field in fields:
    #     if 'Join' in field:
    #         arcpy.DeleteField_management(line_pts_wbody, field)
    #
    # # find flowlines from orignal nhd that and aren't in subsetted flowline network
    # arcpy.SelectLayerByLocation_management("nhd_orig_lyr", 'SHARE_A_LINE_SEGMENT_WITH', flowlines, '', 'NEW_SELECTION', 'INVERT')
    #
    # # create feature class from selected nhd lines
    # nhd_line_sel = arcpy.CopyFeatures_management("nhd_orig_lyr", 'in_memory/nhd_line_sel')
    #
    # # join flowlines selection to end points on waterbodies to get point counts
    # # here we want to find lines that are between 2 points (i.e., connecting across a waterbody)
    # nhd_line_join = arcpy.SpatialJoin_analysis(nhd_line_sel, line_pts_wbody, 'in_memory/nhd_line_join', 'JOIN_ONE_TO_ONE', 'KEEP_ALL', '', 'INTERSECT')
    #
    # # remove points that intersect > 1 line feature
    # with arcpy.da.UpdateCursor(nhd_line_join, ['Join_Count']) as cursor:
    #     for row in cursor:
    #         if row[0] < 2:
    #             cursor.deleteRow()
    #
    # # insert nhd gap lines into flowlines
    # with arcpy.da.InsertCursor(flowlines, ["SHAPE@"]) as iCursor:
    #     with arcpy.da.SearchCursor(nhd_line_join, ["SHAPE@"]) as sCursor:
    #         for row in sCursor:
    #             iCursor.insertRow([row[0]])

    # copy cleaned-up flowlines to output path
    arcpy.CopyFeatures_management(flowlines, outpath)

if __name__ == '__main__':
    main()