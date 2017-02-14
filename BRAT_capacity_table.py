# -------------------------------------------------------------------------------
# Name:        BRAT Table
# Purpose:     Builds the initial table to run through the BRAT tools
#
# Author:      Jordan Gilbert
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
from arcpy.sa import *
import os
import sys


def main(
    seg_network,
    DEM,
    FlowAcc,
    coded_veg,
    coded_hist,
    out_network,
    scratch):

    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("spatial")

    # check that inputs are projected here
    networkSR = arcpy.Describe(seg_network).spatialReference
    if networkSR.type == "Projected":
        pass
    else:
        raise Exception("Input stream network must have a projected coordinate system")

    # check that input network is shapefile
    if seg_network.endswith(".shp"):
        pass
    else:
        raise Exception("Input network must be a shapefile (.shp)")

    # check that input network doesn't have field "objectid" already
    seg_network_fields = [f.name for f in arcpy.ListFields(seg_network)]
    if "OBJECTID" in seg_network_fields:
        raise Exception("Input network cannot have field 'OBJECTID', delete this field")

    # set buffers for analyses
    midpoints = scratch + "/midpoints"
    arcpy.FeatureVerticesToPoints_management(seg_network, midpoints, "MID")
    midpoint_fields = [f.name for f in arcpy.ListFields(midpoints)]
    midpoint_fields.remove("OBJECTID")
    midpoint_fields.remove("Shape")
    midpoint_fields.remove("ORIG_FID")
    arcpy.DeleteField_management(midpoints, midpoint_fields)
    buf_30m = scratch + "/buf_30m"
    arcpy.Buffer_analysis(seg_network, buf_30m, "30 Meters", "", "FLAT", "NONE")
    buf_100m = scratch + "/buf_100m"
    arcpy.Buffer_analysis(seg_network, buf_100m, "100 Meters", "", "FLAT", "NONE")
    sm_midpoint_buffer = scratch + "/sm_midpoint_buffer"
    arcpy.Buffer_analysis(midpoints, sm_midpoint_buffer, "30 Meters", "", "", "NONE")
    midpoint_buffer = scratch + "/midpoint_buffer"
    arcpy.Buffer_analysis(midpoints, midpoint_buffer, "100 Meters", "", "", "NONE")

    arcpy.CopyFeatures_management(seg_network, out_network)

    arcpy.AddMessage('Adding "iGeo" attributes to network')
    igeo_attributes(out_network, DEM, FlowAcc, midpoint_buffer, midpoints, scratch)

    arcpy.AddMessage('Adding "iVeg" attributes to network')
    iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, midpoint_buffer, midpoints, out_network, scratch)

    arcpy.CheckInExtension("spatial")

    return


def igeo_attributes(out_network, DEM, FlowAcc, midpoint_buffer, midpoints, scratch):

    # if fields already exist, delete them
    network_fields = [f.name for f in arcpy.ListFields(out_network)]
    if "iGeo_ElMax" in network_fields:
        arcpy.DeleteField_management(out_network, "iGeo_ElMax")
    if "iGeo_ElMin" in network_fields:
        arcpy.DeleteField_management(out_network, "iGeo_ElMin")
    if "iGeo_Len" in network_fields:
        arcpy.DeleteField_management(out_network, "iGeo_Len")
    if "iGeo_Slope" in network_fields:
        arcpy.DeleteField_management(out_network, "iGeo_Slope")
    if "iGeo_DA" in network_fields:
        arcpy.DeleteField_management(out_network, "iGeo_DA")

    # get start elevation values
    startpoints = scratch + "/startpoints"
    arcpy.FeatureVerticesToPoints_management(out_network, startpoints, "START")
    startpoint_fields = [f.name for f in arcpy.ListFields(startpoints)]
    startpoint_fields.remove("OBJECTID")
    startpoint_fields.remove("Shape")
    startpoint_fields.remove("ORIG_FID")
    arcpy.DeleteField_management(startpoints, startpoint_fields)
    startpoint_buf = scratch + "/startpoint_buf"
    arcpy.Buffer_analysis(startpoints, startpoint_buf, "50 Meters", "", "", "NONE")
    zs_startpoint = ZonalStatistics(startpoint_buf, "OBJECTID", DEM, "MINIMUM", "DATA")
    startpointx100 = zs_startpoint * 100
    startpoint_int = Int(startpointx100)
    startpoint_poly = scratch + "/startpoint_poly"
    arcpy.RasterToPolygon_conversion(startpoint_int, startpoint_poly, "NO_SIMPLIFY")
    startpoint_join = scratch + "/startpoint_join"
    arcpy.SpatialJoin_analysis(startpoint_poly, startpoints, startpoint_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "INTERSECT", "5 Meters")
    arcpy.DeleteField_management(startpoint_join, ["Id", "JOIN_FID", "Join_Count", "TARGET_FID"])
    arcpy.JoinField_management(out_network, "FID", startpoint_join, "ORIG_FID", "gridcode")
    arcpy.AddField_management(out_network, "iGeo_ElMax", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["gridcode", "iGeo_ElMax"])
    for row in cursor:
        index = row[0]/100.0
        row[1] = index
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "gridcode")
    del zs_startpoint, startpointx100, startpoint_int

    # get end elevation values
    endpoints = scratch + "/endpoints"
    arcpy.FeatureVerticesToPoints_management(out_network, endpoints, "END")
    endpoint_fields = [f.name for f in arcpy.ListFields(endpoints)]
    endpoint_fields.remove("OBJECTID")
    endpoint_fields.remove("Shape")
    endpoint_fields.remove("ORIG_FID")
    arcpy.DeleteField_management(endpoints, endpoint_fields)
    endpoint_buf = scratch + "/endpoint_buf"
    arcpy.Buffer_analysis(endpoints, endpoint_buf, "50 Meters", "", "", "NONE")
    zs_endpoint = ZonalStatistics(endpoint_buf, "OBJECTID", DEM, "MINIMUM", "DATA")
    endpointx100 = zs_endpoint * 100
    endpoint_int = Int(endpointx100)
    endpoint_poly = scratch + "/endpoint_poly"
    arcpy.RasterToPolygon_conversion(endpoint_int, endpoint_poly, "NO_SIMPLIFY")
    endpoint_join = scratch + "/endpoint_join"
    arcpy.SpatialJoin_analysis(endpoint_poly, endpoints, endpoint_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "INTERSECT", "5 Meters")
    arcpy.DeleteField_management(endpoint_join, ["Id", "JOIN_FID", "Join_Count", "TARGET_FID"])
    arcpy.JoinField_management(out_network, "FID", endpoint_join, "ORIG_FID", "gridcode")
    arcpy.AddField_management(out_network, "iGeo_ElMin", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["gridcode", "iGeo_ElMin"])
    for row in cursor:
        index = row[0]/100.0
        row[1] =  index
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "gridcode")
    del zs_endpoint, endpointx100, endpoint_int

    # add slope
    arcpy.AddField_management(out_network, "iGeo_Len", "DOUBLE")
    arcpy.CalculateField_management(out_network, "iGeo_Len", "!shape.length@meters!", "PYTHON_9.3")
    arcpy.AddField_management(out_network, "iGeo_Slope", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["iGeo_ElMax", "iGeo_ElMin", "iGeo_Len", "iGeo_Slope"])
    for row in cursor:
        index = (abs(row[0] - row[1]))/row[2]
        row[3] = index
        cursor.updateRow(row)
    del row
    del cursor
    cursor = arcpy.da.UpdateCursor(out_network, "iGeo_Slope")
    for row in cursor:
        if row[0] == 0.0:
            row[0] = 0.0001
        elif row[0] > 1.0:
            row[0] = 0.5
        else:
            pass
        cursor.updateRow(row)
    del row
    del cursor

    # get DA values
    if FlowAcc == None:
        arcpy.AddMessage("calculating drainage area")
        calc_drain_area(DEM)
    else:
        pass

    if FlowAcc == None:
        DEM_dirname = os.path.dirname(DEM)
        DrAr = DEM_dirname + "/DrainArea_sqkm.tif"
        DrArea = Raster(DrAr)
    else:
        DrArea = Raster(FlowAcc)

    drarea_zs = ZonalStatistics(midpoint_buffer, "OBJECTID", DrArea, "MAXIMUM", "DATA")
    drarea_int = Int(drarea_zs)
    drarea_poly = scratch + "/drarea_poly"
    arcpy.RasterToPolygon_conversion(drarea_int, drarea_poly)
    poly_point_join = scratch + "/poly_point_join"
    arcpy.SpatialJoin_analysis(drarea_poly, midpoints, poly_point_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "INTERSECT")
    arcpy.DeleteField_management(poly_point_join, ["Id", "JOIN_FID", "Join_Count", "TARGET_FID"])
    arcpy.JoinField_management(out_network, "FID", poly_point_join, "ORIG_FID", "gridcode")

    arcpy.AddField_management(out_network, "iGeo_DA", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["gridcode", "iGeo_DA"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    cursor = arcpy.da.UpdateCursor(out_network, "iGeo_DA")
    for row in cursor:
        if row[0] == 0:
            row[0] = 0.1
            cursor.updateRow(row)

        else:
            pass
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "gridcode")
    del drarea_zs, drarea_int

    return


def iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, midpoint_buffer, midpoints, out_network, scratch):

    # if fields already exist, delete them
    network_fields = [f.name for f in arcpy.ListFields(out_network)]
    if "iVeg_100EX" in network_fields:
        arcpy.DeleteField_management(out_network, "iVeg_100EX")
    if "iVeg_30EX" in network_fields:
        arcpy.DeleteField_management(out_network, "iVeg_30EX")
    if "iVeg_100PT" in network_fields:
        arcpy.DeleteField_management(out_network, "iVeg_100PT")
    if "iVeg_30PT" in network_fields:
        arcpy.DeleteField_management(out_network, "iVeg_30PT")

    # get iVeg_VT100EX
    veg_lookup = Lookup(coded_veg, "VEG_CODE")
    ex_100_zs = ZonalStatistics(buf_100m, "OBJECTID", veg_lookup, "MEAN", "DATA")
    ex100_max = ZonalStatistics(midpoint_buffer, "OBJECTID", ex_100_zs, "MAXIMUM", "DATA")
    ex100x100 = ex100_max * 100
    ex100_int = Int(ex100x100)
    ex100_poly = scratch + '/ex100_poly'
    arcpy.RasterToPolygon_conversion(ex100_int, ex100_poly, "NO_SIMPLIFY")
    ex100_join = scratch + '/ex100_join'
    arcpy.SpatialJoin_analysis(ex100_poly, midpoints, ex100_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "INTERSECT")
    arcpy.DeleteField_management(ex100_join, ["Id", "JOIN_FID", "Join_Count", "TARGET_FID"])
    arcpy.JoinField_management(out_network, "FID", ex100_join, "ORIG_FID", "gridcode")
    arcpy.AddField_management(out_network, "iVeg_100EX", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["gridcode", "iVeg_100EX"])
    for row in cursor:
        index = row[0] / 100.0
        row[1] = index
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "gridcode")
    del ex_100_zs, ex100_max, ex100x100, ex100_int

    # get iVeg_30EX
    ex_30_zs = ZonalStatistics(buf_30m, "OBJECTID", veg_lookup, "MEAN", "DATA")
    ex30_max = ZonalStatistics(midpoint_buffer, "OBJECTID", ex_30_zs, "MAXIMUM", "DATA")
    ex30x100 = ex30_max * 100
    ex30_int = Int(ex30x100)
    ex30_poly = scratch + '/ex30_poly'
    arcpy.RasterToPolygon_conversion(ex30_int, ex30_poly, "NO_SIMPLIFY")
    ex30_join = scratch + '/ex30_join'
    arcpy.SpatialJoin_analysis(ex30_poly, midpoints, ex30_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "INTERSECT")
    arcpy.DeleteField_management(ex30_join, ["Id", "JOIN_FID", "Join_Count", "TARGET_FID"])
    arcpy.JoinField_management(out_network, "FID", ex30_join, "ORIG_FID", "gridcode")
    arcpy.AddField_management(out_network, "iVeg_30EX", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["gridcode", "iVeg_30EX"])
    for row in cursor:
        index = row[0] / 100.0
        row[1] =  index
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "gridcode")
    del ex_30_zs, ex30_max, ex30x100, ex30_int, veg_lookup

    # get iVeg_100PT
    hist_veg_lookup = Lookup(coded_hist, "VEG_CODE")
    pt_100_zs = ZonalStatistics(buf_100m, "OBJECTID", hist_veg_lookup, "MEAN", "DATA")
    pt100_max = ZonalStatistics(midpoint_buffer, "OBJECTID", pt_100_zs, "MAXIMUM", "DATA")
    pt100x100 = pt100_max * 100
    pt100_int = Int(pt100x100)
    pt100_poly = scratch + '/pt100_poly'
    arcpy.RasterToPolygon_conversion(pt100_int, pt100_poly, "NO_SIMPLIFY")
    pt100_join = scratch + '/pt100_join'
    arcpy.SpatialJoin_analysis(pt100_poly, midpoints, pt100_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "INTERSECT")
    arcpy.DeleteField_management(pt100_join, ["Id", "JOIN_FID", "Join_Count", "TARGET_FID"])
    arcpy.JoinField_management(out_network, "FID", pt100_join, "ORIG_FID", "gridcode")
    arcpy.AddField_management(out_network, "iVeg_100PT", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["gridcode", "iVeg_100PT"])
    for row in cursor:
        index = row[0] / 100.0
        row[1] = index
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "gridcode")
    del pt_100_zs, pt100_max, pt100x100, pt100_int

    # get iVeg_30PT
    pt_30_zs = ZonalStatistics(buf_30m, "OBJECTID", hist_veg_lookup, "MEAN", "DATA")
    pt30_max = ZonalStatistics(midpoint_buffer, "OBJECTID", pt_30_zs, "MAXIMUM", "DATA")
    pt30x100 = pt30_max * 100
    pt30_int = Int(pt30x100)
    pt30_poly = scratch + '/pt30_poly'
    arcpy.RasterToPolygon_conversion(pt30_int, pt30_poly, "NO_SIMPLIFY")
    pt30_join = scratch + '/pt30_join'
    arcpy.SpatialJoin_analysis(pt30_poly, midpoints, pt30_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "INTERSECT")
    arcpy.DeleteField_management(pt30_join, ["Id", "JOIN_FID", "Join_Count", "TARGET_FID"])
    arcpy.JoinField_management(out_network, "FID", pt30_join, "ORIG_FID", "gridcode")
    arcpy.AddField_management(out_network, "iVeg_30PT", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["gridcode", "iVeg_30PT"])
    for row in cursor:
        index = row[0] / 100.0
        row[1] = index
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "gridcode")
    del pt_30_zs, pt30_max, pt30x100, pt30_int, hist_veg_lookup

    return


def calc_drain_area(DEM):
    DEMdesc = arcpy.Describe(DEM)
    height = DEMdesc.meanCellHeight
    width = DEMdesc.meanCellWidth
    res = height * width
    resolution = int(res)

    # derive a flow accumulation raster from input DEM and covert to units of square kilometers
    filled_DEM = Fill(DEM, "")
    flow_direction = FlowDirection(filled_DEM, "NORMAL", "")
    flow_accumulation = FlowAccumulation(flow_direction, "", "FLOAT")
    DrainArea = flow_accumulation * resolution / 1000000

    DEM_dirname = os.path.dirname(DEM)
    if os.path.exists(DEM_dirname + "/DrainArea_sqkm.tif"):
        arcpy.Delete_management(DEM_dirname + "/DrainArea_sqkm.tif")
        DrArea_path = DEM_dirname + "/DrainArea_sqkm.tif"
        DrainArea.save(DrArea_path)
    else:
        DrArea_path = DEM_dirname + "/DrainArea_sqkm.tif"
        DrainArea.save(DrArea_path)

    return


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7])
