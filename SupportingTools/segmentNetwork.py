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

import os
import arcpy

# User defined arguments:

# nhd_flowline_path - path to input flowlines that will be segmented
# outpath - name and path of output segmented flowline network
# interval - reach spacing (in meters)
# min_segLength - minimum segment (reach) length (in meters)

interval = 300.0 # Default: 300.0
min_segLength = 50.0 # Default: 50.0


def main(nhd_flowline_path, outpath):
    #  import required modules and extensions
    arcpy.CheckOutExtension('Spatial')

    #  environment settings
    arcpy.env.workspace = 'in_memory' # set workspace to temporary workspace
    arcpy.env.overwriteOutput = True  # set to overwrite output
    sr = arcpy.Describe(nhd_flowline_path).spatialReference

    #  select lines from original nhd that are not coded as pipeline (fcdoe 428**)
    arcpy.MakeFeatureLayer_management(nhd_flowline_path, 'nhd_flowline_lyr')
    quer = '"FCODE" >=42800 AND "FCODE" <= 42813'
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'NEW_SELECTION', quer)
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'SWITCH_SELECTION')
    flowline_sel = arcpy.CopyFeatures_management('nhd_flowline_lyr', 'in_memory/flowline_selection')

    #  select and dissolve named reaches
    arcpy.MakeFeatureLayer_management(flowline_sel, 'flowline_sel_lyr')
    quer = """ "GNIS_NAME" = '' """
    arcpy.SelectLayerByAttribute_management('flowline_sel_lyr', 'NEW_SELECTION', quer)
    arcpy.SelectLayerByAttribute_management('flowline_sel_lyr', 'SWITCH_SELECTION')
    flowline_named = arcpy.CopyFeatures_management('flowline_sel_lyr', 'in_memory/flowline_named')
    flowline_named_dissolve = arcpy.Dissolve_management(flowline_named, 'in_memory/flowline_named_dissolve', 'GNIS_NAME', '', 'SINGLE_PART', 'UNSPLIT_LINES')

    # dissolve all reaches and then select out those that are not named
    flowline_dissolve = arcpy.Dissolve_management(flowline_sel, 'in_memory/flowline_dissolve', '', '', 'SINGLE_PART', 'UNSPLIT_LINES')
    arcpy.MakeFeatureLayer_management(flowline_dissolve, 'flowline_dissolve_lyr')
    arcpy.SelectLayerByLocation_management('flowline_dissolve_lyr', 'SHARE_A_LINE_SEGMENT_WITH', flowline_named_dissolve, '', 'NEW_SELECTION', 'INVERT')
    flowline_unnamed = arcpy.CopyFeatures_management('flowline_dissolve_lyr', 'in_memory/flowline_unnamed')

    # merge the 2 layers (named and unnamed) into single flowline network
    tmp_flowline_network = arcpy.Merge_management([flowline_named_dissolve, flowline_unnamed], 'in_memory/tmp_flowline_network')
    flowline_network = arcpy.Sort_management(tmp_flowline_network, 'in_memory/flowline_network', [['Shape', 'DESCENDING']], 'PEANO')

    #  create line id field and line length fields
    #  if fields already exist, delete them
    check_fields = ['LineID', 'LineLen', 'SegID', 'SegLen', 'ReachID', 'ReachLen']
    fields = [f.name for f in arcpy.ListFields(flowline_network)]
    for field in fields:
        if field in check_fields:
            arcpy.DeleteField_management(flowline_network, field)
    arcpy.AddField_management(flowline_network, 'StreamName', 'TEXT', 50)
    arcpy.AddField_management(flowline_network, 'StreamID', 'LONG')
    arcpy.AddField_management(flowline_network, 'StreamLen', 'DOUBLE')
    ct = 1
    with arcpy.da.UpdateCursor(flowline_network, ['StreamID', 'Shape@Length', 'StreamLen', 'GNIS_NAME', 'StreamName']) as cursor:
        for row in cursor:
            #row[1] = row[0]
            row[0] = ct
            row[2] = row[1]
            row[4] = row[3]
            ct += 1
            cursor.updateRow(row)

    #  dissolve flowline network
    flowline_network_dissolve = arcpy.Dissolve_management(flowline_network, 'in_memory/flowline_network_dissolve', '', '', 'SINGLE_PART')

    #  intersect to split by segments
    flowline_int = arcpy.Intersect_analysis([flowline_network, flowline_network_dissolve], 'in_memory/flowline_int')
    arcpy.AddField_management(flowline_int, 'SegID', 'LONG')
    arcpy.AddField_management(flowline_int, 'SegLen', 'DOUBLE')
    ct = 1
    with arcpy.da.UpdateCursor(flowline_int, ['SegID', 'Shape@Length', 'SegLen']) as cursor:
        for row in cursor:
            row[0] = ct
            row[2] = row[1]
            ct += 1
            cursor.updateRow(row)

    keep = ['FID', 'OID', 'Shape', 'StreamID', 'StreamLen', 'StreamName', 'SegID', 'SegLen']
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

    # flip line back to correct direction
    arcpy.FlipLine_edit(flowline_int)

    # split flowlines at segment interval points
    flowline_seg = arcpy.SplitLineAtPoint_management(flowline_int, seg_pts, 'in_memory/flowline_seg', 1.0)

    # add and populate reach id and length fields
    arcpy.AddField_management(flowline_seg, 'ReachID', 'SHORT')
    arcpy.AddField_management(flowline_seg, 'ReachLen', 'DOUBLE')
    ct = 1
    with arcpy.da.UpdateCursor(flowline_seg, ['ReachID', 'Shape@Length', 'ReachLen']) as cursor:
        for row in cursor:
            row[0] = ct
            row[2] = row[1]
            ct += 1
            cursor.updateRow(row)

    # get distance along route (LineID) for segment midpoints
    midpoints =  arcpy.FeatureVerticesToPoints_management(flowline_seg, 'in_memory/midpoints', "MID")
    arcpy.CopyFeatures_management(midpoints, os.path.join(os.path.dirname(outpath), 'tmp_midpoints.shp'))

    arcpy.AddField_management(flowline_network, 'From_', 'DOUBLE')
    arcpy.AddField_management(flowline_network, 'To_', 'DOUBLE')
    with arcpy.da.UpdateCursor(flowline_network, ['StreamLen', 'From_', 'To_']) as cursor:
        for row in cursor:
            row[1] = 0.0
            row[2] = row[0]
            cursor.updateRow(row)

    arcpy.CreateRoutes_lr(flowline_network, 'StreamID', 'in_memory/flowline_route', 'TWO_FIELDS', 'From_', 'To_')
    routeTbl = arcpy.LocateFeaturesAlongRoutes_lr(midpoints, 'in_memory/flowline_route', 'StreamID',
                                                   1.0, os.path.join(os.path.dirname(outpath), 'tbl_Routes.dbf'),
                                                   'RID POINT MEAS')

    distDict = {}
    # add reach id distance values to dictionary
    with arcpy.da.SearchCursor(routeTbl, ['ReachID', 'MEAS']) as cursor:
        for row in cursor:
            distDict[row[0]] = row[1]

    # populate dictionary value to output field by ReachID
    arcpy.AddField_management(flowline_seg, 'ReachDist', 'DOUBLE')
    with arcpy.da.UpdateCursor(flowline_seg, ['ReachID', 'ReachDist']) as cursor:
        for row in cursor:
            aKey = row[0]
            row[1] = distDict[aKey]
            cursor.updateRow(row)

    # save flowline segment output
    arcpy.CopyFeatures_management(flowline_seg, outpath)

    arcpy.Delete_management('in_memory')

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Segments the stream network given to it")
    parser.add_argument('input_stream', help="The shape file given as input to the program")
    parser.add_argument('-o' ,'--output_location', help="Path to where we should create the segmented stream network")
    args = parser.parse_args()
    if args.output_location:
        main(args.input_stream, args.output_location)
    else:
        output_location = os.path.join(os.path.dirname(args.input_stream), "Segmented_Stream.shp")
        main(args.input_stream, output_location)