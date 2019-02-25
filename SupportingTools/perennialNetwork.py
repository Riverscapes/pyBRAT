# -------------------------------------------------------------------------------
# Name:        Perennial Network
# Purpose:     Script generates perennial network using NHD data inputs
#
# Author:      Sara Bangen (sara.bangen@gmail.com)
#
# -------------------------------------------------------------------------------

# User defined arguments:

# nhd_orig_flowline_path - path to original nhd flowline shapefile
# nhd_area_path - path to nhd area shapefile
# nhd_waterbody_path - path to nhd waterbody shapefile
# outpath - name and path of output flowline network


nhd_orig_flowline_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_CodeTest\Perennial\LakeTahoe\NHDFlowline.shp"
nhd_area_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_CodeTest\Perennial\LakeTahoe\NHDArea.shp"
nhd_waterbody_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_CodeTest\Perennial\LakeTahoe\NHDWaterbody.shp"
outpath = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_CodeTest\Perennial\LakeTahoe\NHD_24k_Perennial_Test.shp"

#  import required modules and extensions
import arcpy
import os


def findGaps(lines, flowline_per, find_art = 'False'):

    #  environment settings
    arcpy.env.overwriteOutput = 'TRUE'

    # add unique id field to gap lines
    arcpy.AddField_management(lines, 'LineID', 'LONG')
    ct = 1
    with arcpy.da.UpdateCursor(lines, ['LineID']) as cursor:
        for row in cursor:
            row[0] = ct
            ct += 1
            cursor.updateRow(row)

    # create gap line start and end points
    gap_start_pts = arcpy.FeatureVerticesToPoints_management(lines, 'in_memory/gap_start_pts', "START")
    gap_end_pts = arcpy.FeatureVerticesToPoints_management(lines, 'in_memory/gap_end_pts', "END")
    arcpy.MakeFeatureLayer_management(gap_start_pts, 'gap_start_pts_lyr')
    arcpy.MakeFeatureLayer_management(gap_end_pts, 'gap_end_pts_lyr')

    # create end points along dissolved perennial network
    flowline_per_dissolve = arcpy.Dissolve_management(flowline_per, 'in_memory/flowline_per_dissolve', 'GNIS_NAME', '', 'SINGLE_PART', 'UNSPLIT_LINES')
    per_end_pts = arcpy.FeatureVerticesToPoints_management(flowline_per_dissolve, 'in_memory/per_end_pts', "END")

    # if dealing with artificial gap lines - select gap starts that intersect perennial flowlines
    # if dealing with other gap lines - select gap starts that intersect a perennial end point
    if find_art == 'True':
        arcpy.SelectLayerByLocation_management('gap_start_pts_lyr', 'INTERSECT', flowline_per_dissolve, '', 'NEW_SELECTION')
    else:
        # select gap start that intersect perennial end point
        arcpy.SelectLayerByLocation_management('gap_start_pts_lyr', 'INTERSECT', per_end_pts, '', 'NEW_SELECTION')

    # select gap end that intersect perennial start point
    arcpy.SelectLayerByLocation_management('gap_end_pts_lyr', 'INTERSECT', flowline_per_dissolve, '', 'NEW_SELECTION')

    # create list of gap start and end point unique ids
    startList = [row[0] for row in arcpy.da.SearchCursor('gap_start_pts_lyr', 'LineID')]
    endList = [row[0] for row in arcpy.da.SearchCursor('gap_end_pts_lyr', 'LineID')]

    # delete gap lines that don't start and end on perennial network
    # (i.e., they aren't true gap lines)
    with arcpy.da.UpdateCursor(lines, ['LineID']) as cursor:
        for row in cursor:
            if row[0] in startList and row[0] in endList:
                pass
            else:
                cursor.deleteRow()

    return lines


def main():

    #  environment settings
    arcpy.env.overwriteOutput = 'TRUE'

    # --perennial coded lines--

    # select lines from original nhd that are coded as perennial
    arcpy.MakeFeatureLayer_management(nhd_orig_flowline_path, 'nhd_flowline_lyr')
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'NEW_SELECTION', """ "FCODE" = 46006 """)
    flowline_per = arcpy.CopyFeatures_management('nhd_flowline_lyr', 'in_memory/flowline_per')

    # --add missing major rivers--
    # --subsetted artificial coded lines that are in perennial nhd area polygons--

    # select perennial coded nhd area polygons
    arcpy.MakeFeatureLayer_management(nhd_area_path, 'nhd_area_lyr')
    arcpy.SelectLayerByAttribute_management('nhd_area_lyr', 'NEW_SELECTION', """ "FCODE" = 46006 """)

    # select and dissolve artificial coded nhd lines that are within perennial nhd area polygons
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'NEW_SELECTION', """ "FCODE" = 55800 """)
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'WITHIN', 'nhd_area_lyr', '', 'SUBSET_SELECTION')
    flowline_art_code = arcpy.Dissolve_management('nhd_flowline_lyr', 'in_memory/flowline_art_code', 'GNIS_NAME', '', 'SINGLE_PART', 'UNSPLIT_LINES')

    # remove short lines (< 50 m) that act as artificial connectors to flowlines outside perennial nhd area polygons
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'INTERSECT', 'nhd_area_lyr', '1 Meters', 'NEW_SELECTION')
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'SUBSET_SELECTION', """ "FCODE" <> 55800 """)
    arcpy.MakeFeatureLayer_management(flowline_art_code, 'flowline_art_code_lyr')
    arcpy.SelectLayerByLocation_management('flowline_art_code_lyr', 'INTERSECT', 'nhd_flowline_lyr', '', 'NEW_SELECTION')
    with arcpy.da.UpdateCursor('flowline_art_code_lyr', ['SHAPE@Length']) as cursor:
        for row in cursor:
            if row[0] < 50:
                cursor.deleteRow()

    # remove lines that end where canal starts
    mr_end_pt = arcpy.FeatureVerticesToPoints_management(flowline_art_code, 'in_memory/mr_end_pt', "END")
    arcpy.MakeFeatureLayer_management(mr_end_pt, 'mr_end_pt_lyr')
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'NEW_SELECTION', """ "FCODE" = 33600 """)
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'INTERSECT', flowline_art_code, '1 Meters', 'SUBSET_SELECTION')

    canal_start_pt = arcpy.FeatureVerticesToPoints_management('nhd_flowline_lyr', 'in_memory/canal_start_pt', "START")
    arcpy.SelectLayerByLocation_management('mr_end_pt_lyr', 'INTERSECT', canal_start_pt, '', 'NEW_SELECTION')
    arcpy.SelectLayerByLocation_management('flowline_art_code_lyr', 'INTERSECT', 'mr_end_pt_lyr', '', 'NEW_SELECTION')

    arcpy.DeleteFeatures_management('flowline_art_code_lyr')
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'SHARE_A_LINE_SEGMENT_WITH', flowline_art_code, '', 'NEW_SELECTION')

    # add selected flowlines to the perennial stream shp
    with arcpy.da.InsertCursor(flowline_per, ["SHAPE@"]) as iCursor:
        with arcpy.da.SearchCursor('nhd_flowline_lyr', ["SHAPE@"]) as sCursor:
            for row in sCursor:
                iCursor.insertRow([row[0]])

    # --add missing flowlines in marshes--
    # --artificial coded lines that are perennial gaps in marsh waterbody polygons--

    #  select nhd waterbodys that:
    #   - are coded as marshes (ftype 466)
    #   - intersect perennial stream start and end (i.e., are perennial stream inlet AND outlet)
    arcpy.MakeFeatureLayer_management(nhd_waterbody_path, 'nhd_waterbody_lyr')
    arcpy.SelectLayerByAttribute_management('nhd_waterbody_lyr', 'NEW_SELECTION', """ "FTYPE" = 466 """)
    marshes = arcpy.CopyFeatures_management('nhd_waterbody_lyr', 'in_memory/marshes')
    arcpy.MakeFeatureLayer_management(marshes, 'marshes_lyr')
    per_start_pt = arcpy.FeatureVerticesToPoints_management(flowline_per, 'in_memory/per_start_pt', "START")
    per_end_pt = arcpy.FeatureVerticesToPoints_management(flowline_per, 'in_memory/per_end_pt', "END")
    arcpy.SelectLayerByLocation_management('marshes_lyr', 'INTERSECT', per_start_pt, '', 'NEW_SELECTION')
    arcpy.SelectLayerByLocation_management('marshes_lyr', 'INTERSECT', per_end_pt, '', 'SUBSET_SELECTION')

    #  select and dissolve nhd flowlines that:
    #   - are coded as artificial
    #   - fall within selected marsh waterbodies
    #   - are not already part of perennial stream network
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'NEW_SELECTION', """ "FCODE" = 55800 """)
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'WITHIN', 'marshes_lyr', '', 'SUBSET_SELECTION')
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'SHARE_A_LINE_SEGMENT_WITH', flowline_per, '', 'REMOVE_FROM_SELECTION')
    marsh_lines = arcpy.Dissolve_management('nhd_flowline_lyr', 'in_memory/marsh_lines', 'GNIS_NAME', '', 'SINGLE_PART', 'UNSPLIT_LINES')

    marsh_gap_lines = findGaps(marsh_lines, flowline_per)

    # add selected flowlines to the perennial stream shp
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'SHARE_A_LINE_SEGMENT_WITH', marsh_gap_lines, '', 'NEW_SELECTION')
    with arcpy.da.InsertCursor(flowline_per, ["SHAPE@"]) as iCursor:
        with arcpy.da.SearchCursor('nhd_flowline_lyr', ["SHAPE@"]) as sCursor:
            for row in sCursor:
                iCursor.insertRow([row[0]])

    # --add missing flowlines in smaller lakes and ponds--

    #  select nhd waterbodys that:
    #   - are coded as lakes/ponds (ftype 390)
    #   - area <= .03 sq km
    #   - are not named
    #   - intersect perennial stream start and end (i.e., are perennial stream inlet AND outlet)
    arcpy.SelectLayerByLocation_management('nhd_waterbody_lyr', 'INTERSECT', flowline_per, '', 'NEW_SELECTION')
    arcpy.SelectLayerByAttribute_management('nhd_waterbody_lyr', 'SUBSET_SELECTION', """ "FTYPE" = 390 AND "AREASQKM" <= 0.03 AND "GNIS_NAME" = '' """)
    sm_lakes_ponds = arcpy.CopyFeatures_management('nhd_waterbody_lyr', 'in_memory/sm_lakes_ponds')
    arcpy.MakeFeatureLayer_management(sm_lakes_ponds, 'sm_lakes_ponds_lyr')
    per_start_pt = arcpy.FeatureVerticesToPoints_management(flowline_per, 'in_memory/per_start_pt', "START")
    per_end_pt = arcpy.FeatureVerticesToPoints_management(flowline_per, 'in_memory/per_end_pt', "END")
    arcpy.SelectLayerByLocation_management('sm_lakes_ponds_lyr', 'INTERSECT', per_start_pt, '', 'NEW_SELECTION')
    arcpy.SelectLayerByLocation_management('sm_lakes_ponds_lyr', 'INTERSECT', per_end_pt, '', 'SUBSET_SELECTION')

    #  select nhd flowlines that:
    #   - fall within selected waterbodies
    #   - intersect a perennial streams (i.e., are gaps on perennial network)
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'WITHIN', 'sm_lakes_ponds_lyr', '', 'NEW_SELECTION')
    flowline_wbody_dissolve = arcpy.Dissolve_management('nhd_flowline_lyr', 'in_memory/flowline_wbody_dissolve', 'GNIS_NAME', '', 'SINGLE_PART', 'UNSPLIT_LINES')
    arcpy.MakeFeatureLayer_management(flowline_wbody_dissolve, 'flowline_wbody_dissolve_lyr')
    arcpy.SelectLayerByLocation_management('flowline_wbody_dissolve_lyr', 'INTERSECT', flowline_per, '', 'NEW_SELECTION')

    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'SHARE_A_LINE_SEGMENT_WITH', 'flowline_wbody_dissolve_lyr', '', 'NEW_SELECTION')

    # add selected flowlines to the perennial stream shp
    with arcpy.da.InsertCursor(flowline_per, ["SHAPE@"]) as iCursor:
        with arcpy.da.SearchCursor('nhd_flowline_lyr', ["SHAPE@"]) as sCursor:
            for row in sCursor:
                iCursor.insertRow([row[0]])

    # --remove flowlines where 2 lines end but none start (indicate 'false perennial tribs')--

    per_start_pt = arcpy.FeatureVerticesToPoints_management(flowline_per, 'in_memory/per_start_pt', "START")
    per_end_pt = arcpy.FeatureVerticesToPoints_management(flowline_per, 'in_memory/per_end_pt', "END")
    per_end_pt_join = arcpy.SpatialJoin_analysis(per_end_pt, per_end_pt, 'in_memory/per_end_pt_join', 'JOIN_ONE_TO_ONE', 'KEEP_ALL', '', 'INTERSECT')
    arcpy.MakeFeatureLayer_management(per_end_pt_join, 'per_end_pt_join_lyr')
    arcpy.SelectLayerByLocation_management('per_end_pt_join_lyr', 'INTERSECT', per_start_pt, '', 'NEW_SELECTION')
    arcpy.SelectLayerByAttribute_management('per_end_pt_join_lyr', 'SWITCH_SELECTION')
    arcpy.SelectLayerByAttribute_management('per_end_pt_join_lyr', 'SUBSET_SELECTION', """ "Join_Count" >= 2 """)
    arcpy.MakeFeatureLayer_management(flowline_per, 'flowline_per_lyr')
    arcpy.SelectLayerByLocation_management('flowline_per_lyr', 'INTERSECT', 'per_end_pt_join_lyr', '', 'NEW_SELECTION')
    arcpy.DeleteFeatures_management('flowline_per_lyr')

    # --add artifical flowlines that fall on gaps in the perennial network--
    # --these are potential network gap lines--

    # select artificial coded flowlines that aren't part of perennial network up to this point
    arcpy.SelectLayerByAttribute_management('nhd_flowline_lyr', 'NEW_SELECTION', """ "FCODE" = 55800 """)
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'SHARE_A_LINE_SEGMENT_WITH', flowline_per, '', 'REMOVE_FROM_SELECTION')

    # create search aoi from perennial area polygons and marsh waterbody polygons
    arcpy.SelectLayerByAttribute_management('nhd_waterbody_lyr', 'NEW_SELECTION', """ "FTYPE" = 466 """)
    marshes = arcpy.CopyFeatures_management('nhd_waterbody_lyr', 'in_memory/marshes')
    arcpy.SelectLayerByAttribute_management('nhd_area_lyr', 'NEW_SELECTION', """ "FCODE" = 46006 """)
    per_area = arcpy.CopyFeatures_management('nhd_area_lyr', 'in_memory/per_area')
    art_gap_aoi = arcpy.Merge_management([marshes, per_area], 'in_memory/art_gap_aoi')

    # subset selection to flowlines that flow throw search aoi
    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'WITHIN', art_gap_aoi, '', 'SUBSET_SELECTION')
    art_lines = arcpy.CopyFeatures_management('nhd_flowline_lyr', 'in_memory/art_lines')

    art_gap_lines = findGaps(art_lines, flowline_per, 'True')

    # add artificial gap to the perennial stream shp
    with arcpy.da.InsertCursor(flowline_per, ["SHAPE@"]) as iCursor:
        with arcpy.da.SearchCursor(art_gap_lines, ["SHAPE@"]) as sCursor:
            for row in sCursor:
                iCursor.insertRow([row[0]])


    # --remove isolated (i.e., only intersect themselves), short (< 300 m) line segments--

    flowline_per_dissolve2 = arcpy.Dissolve_management(flowline_per, 'in_memory/flowline_per_dissolve2', '', '', 'SINGLE_PART', 'UNSPLIT_LINES')
    flowline_per_join = arcpy.SpatialJoin_analysis(flowline_per_dissolve2, flowline_per_dissolve2, 'in_memory/flowline_per_join', 'JOIN_ONE_TO_ONE', 'KEEP_ALL', '', 'INTERSECT')
    with arcpy.da.UpdateCursor(flowline_per_join, ['SHAPE@Length', 'Join_Count']) as cursor:
        for row in cursor:
            if row[0] < 300 and row[1] <= 1:
                cursor.deleteRow()

    # --select and save final perennial shp--

    arcpy.SelectLayerByLocation_management('nhd_flowline_lyr', 'SHARE_A_LINE_SEGMENT_WITH', flowline_per_join, '', 'NEW_SELECTION')
    arcpy.CopyFeatures_management('nhd_flowline_lyr', outpath)
    arcpy.DeleteIdentical_management(outpath, ['Shape'])


if __name__ == '__main__':
    main()
