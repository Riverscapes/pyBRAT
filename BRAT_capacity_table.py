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
    projPath,
    seg_network,
    DEM,
    FlowAcc,
    coded_veg,
    coded_hist,
    out_name,
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
    if not os.path.exists(os.path.dirname(seg_network) + "/Buffers"):
        os.mkdir(os.path.dirname(seg_network) + "/Buffers")
    midpoints = scratch + "/midpoints"
    arcpy.FeatureVerticesToPoints_management(seg_network, midpoints, "MID")
    midpoint_fields = [f.name for f in arcpy.ListFields(midpoints)]
    midpoint_fields.remove("OBJECTID")
    midpoint_fields.remove("Shape")
    midpoint_fields.remove("ORIG_FID")
    arcpy.DeleteField_management(midpoints, midpoint_fields)
    if not os.path.exists(os.path.dirname(seg_network) + "/Buffers/buffer_30m.shp"):
        buf_30m = os.path.dirname(seg_network) + "/Buffers/buffer_30m.shp"
        arcpy.Buffer_analysis(seg_network, buf_30m, "30 Meters", "", "FLAT", "NONE")
    else:
        buf_30m = os.path.dirname(seg_network) + "/Buffers/buffer_30m.shp"
    if not os.path.exists(os.path.dirname(seg_network) + "/Buffers/buffer_100m.shp"):
        buf_100m = os.path.dirname(seg_network) + "/Buffers/buffer_100m.shp"
        arcpy.Buffer_analysis(seg_network, buf_100m, "100 Meters", "", "FLAT", "NONE")
    else:
        buf_100m = os.path.dirname(seg_network) + "/Buffers/buffer_100m.shp"
    midpoint_buffer = scratch + "/midpoint_buffer"
    arcpy.Buffer_analysis(midpoints, midpoint_buffer, "100 Meters", "", "", "NONE")

    j = 1
    while os.path.exists(projPath + "/01_Analyses/Output_" + str(j)):
        j += 1

    os.mkdir(projPath + "/02_Analyses/Output_" + str(j))
    out_network = projPath + "/02_Analyses/Ouptut_" + str(j) + "/" + out_name + ".shp"
    arcpy.CopyFeatures_management(seg_network, out_network)

    arcpy.AddMessage('Adding "iGeo" attributes to network')
    igeo_attributes(projPath, DEM, FlowAcc, midpoint_buffer, buf_30m, scratch)

    arcpy.AddMessage('Adding "iVeg" attributes to network')
    iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, out_network, scratch)

    arcpy.CheckInExtension("spatial")

    return


def igeo_attributes(projPath, out_network, DEM, FlowAcc, midpoint_buffer, buf_30m, scratch):

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
    arcpy.Buffer_analysis(startpoints, startpoint_buf, "50 Meters", "", "", "LIST", "ORIG_FID")
    zs_startpoint = scratch + "/zs_startpoint"
    ZonalStatisticsAsTable(startpoint_buf, "ORIG_FID", DEM, zs_startpoint, statistics_type="MINIMUM")
    arcpy.JoinField_management(out_network, "FID", zs_startpoint, "ORIG_FID", "MIN")
    arcpy.AddField_management(out_network, "iGeo_ElMax", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["MIN", "iGeo_ElMax"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "MIN")
    del zs_startpoint

    # get end elevation values
    zs_buf_30m = scratch + "/zs_buf_30m"
    ZonalStatisticsAsTable(buf_30m, "ORIG_FID", DEM, zs_buf_30m, statistics_type="MINIMUM")
    arcpy.JoinField_management(out_network, "FID", zs_buf_30m, "ORIG_FID", "MIN")
    arcpy.AddField_management(out_network, "iGeo_ElMin", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["MIN", "iGeo_ElMin"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "MIN")
    del zs_buf_30m

    # add slope
    arcpy.AddField_management(out_network, "iGeo_Len", "DOUBLE")
    arcpy.CalculateField_management(out_network, "iGeo_Len", '!shape.length@meters!', "PYTHON_9.3")
    arcpy.AddField_management(out_network, "iGeo_Slope", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["iGeo_ElMax", "iGeo_ElMin", "iGeo_Len", "iGeo_Slope"])
    for row in cursor:
        index = (abs(row[0] - row[1])) / row[2]
        row[3] = index
        cursor.updateRow(row)
    del row
    del cursor
    cursor = arcpy.da.UpdateCursor(out_network, "iGeo_Slope")  # fix slope values of 0
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
    elif os.path.exists(os.path.dirname(DEM) + "/Flow"):
        pass
    else:
        os.mkdir(projPath + os.path.dirname(DEM) + "/Flow")
        arcpy.CopyRaster_management(FlowAcc, os.path.dirname(DEM) + "/Flow" + os.path.basename(FlowAcc))

    if FlowAcc == None:
        DrAr = os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"
        DrArea = Raster(DrAr)
    else:
        DrAr = os.path.dirname(DEM) + "/Flow/" + os.path.basename(FlowAcc)
        DrArea = Raster(DrAr)

    drarea_zs = scratch + "/drarea_zs"
    ZonalStatisticsAsTable(midpoint_buffer, "ORIG_FID", DrArea, drarea_zs, statistics_type="MAXIMUM")
    arcpy.JoinField_management(out_network, "FID", drarea_zs, "ORIG_FID", "MAX")

    arcpy.AddField_management(out_network, "iGeo_DA", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["MAX", "iGeo_DA"])
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
    arcpy.DeleteField_management(out_network, "MAX")
    del drarea_zs

    return


def iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, out_network, scratch):

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
    ex_100_zs = scratch + "/ex_100_zs"
    ZonalStatisticsAsTable(buf_100m, "ORIG_FID", veg_lookup, ex_100_zs, statistics_type="MEAN")
    arcpy.JoinField_management(out_network, "FID", ex_100_zs, "ORIG_FID", "MEAN")
    arcpy.AddField_management(out_network, "iVeg_100EX", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["MEAN", "iVeg_100EX"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "MEAN")
    del ex_100_zs

    # get iVeg_30EX
    ex_30_zs = scratch + "/ex_30_zs"
    ZonalStatisticsAsTable(buf_30m, "ORIG_FID", veg_lookup, ex_30_zs, statistics_type="MEAN")
    arcpy.JoinField_management(out_network, "FID", ex_30_zs, "ORIG_FID", "MEAN")
    arcpy.AddField_management(out_network, "iVeg_30EX", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["MEAN", "iVeg_30EX"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "MEAN")
    del ex_30_zs, veg_lookup

    # get iVeg_100PT
    hist_veg_lookup = Lookup(coded_hist, "VEG_CODE")
    pt_100_zs = scratch + "/pt_100_zs"
    ZonalStatisticsAsTable(buf_100m, "ORIG_FID", hist_veg_lookup, pt_100_zs, statistics_type="MEAN")
    arcpy.JoinField_management(out_network, "FID", pt_100_zs, "ORIG_FID", "MEAN")
    arcpy.AddField_management(out_network, "iVeg_100PT", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["MEAN", "iVeg_100PT"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "MEAN")
    del pt_100_zs

    # get iVeg_30PT
    pt_30_zs = scratch + "/pt_30_zs"
    ZonalStatisticsAsTable(buf_30m, "ORIG_FID", hist_veg_lookup, pt_30_zs, statistics_type="MEAN")
    arcpy.JoinField_management(out_network, "FID", pt_30_zs, "ORIG_FID", "MEAN")
    arcpy.AddField_management(out_network, "iVeg_30PT", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(out_network, ["MEAN", "iVeg_30PT"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(out_network, "MEAN")
    del pt_30_zs, hist_veg_lookup

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

    if os.path.exists(os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"):
        arcpy.Delete_management(os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif")
        DrArea_path = os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"
        DrainArea.save(DrArea_path)
    else:
        os.mkdir(os.path.dirname(DEM) + "/Flow")
        DrArea_path = os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"
        DrainArea.save(DrArea_path)


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
        sys.argv[8])
