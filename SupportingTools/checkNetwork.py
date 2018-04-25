# -------------------------------------------------------------------------------
# Name:        Check Network
# Purpose:     Identifies potential gaps in the network by creating points
#              where flowlines aren't connected to any other lines.  This
#              should be used to identify gaps but will also create 'false-positive'
#              points at the head of a network and at the DS/US end of waterbodies
#
# Author:      Sara Bangen (sara.bangen@gmail.com)
#
# -------------------------------------------------------------------------------

# User defined arguments:

# flowline_path - path to flowline to check
# outpath - name and path of output points shapefile


flowline_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\Truckee_16050102\NHD\NHD_24k_Perennial.shp"
outpath = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\Truckee_16050102\NHD\tmp_gap_points.shp"


def main():

    #  import required modules and extensions
    import arcpy

    #  environment settings
    arcpy.env.workspace = 'in_memory' # set workspace to temporary workspace
    arcpy.env.overwriteOutput = 'TRUE'

    # make a temp copy of input flowlines
    flowlines = arcpy.CopyFeatures_management(flowline_path, 'in_memory/flowlines')

    # --find gaps in flowline network--
    # need this fix to resolve issues where flowlines were omitted in nhd area and waterbody polygons

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

    # copy gap points to output path
    arcpy.CopyFeatures_management(line_pts_join, outpath)


if __name__ == '__main__':
    main()