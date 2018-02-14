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
import projectxml
import datetime
import uuid


def main(
    projPath,
    projName,
    hucID,
    hucName,
    seg_network,
    DEM,
    FlowAcc,
    coded_veg,
    coded_hist,
    valley_bottom,
    road,
    railroad,
    canal,
    landuse,
    out_name):


    scratch = 'in_memory'
    arcpy.env.workspace = scratch
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("spatial")

    # check that inputs are projected
    networkSR = arcpy.Describe(seg_network).spatialReference
    if networkSR.type == "Projected":
        pass
    else:
        raise Exception("Input stream network must have a projected coordinate system")

    if road is not None:
        roadSR = arcpy.Describe(road).spatialReference
        if roadSR.type == "Projected":
            pass
        else:
            raise Exception("Input roads must have a projected coordinate system")

    if railroad is not None:
        rrSR = arcpy.Describe(railroad).spatialReference
        if rrSR.type == "Projected":
            pass
        else:
            raise Exception("Input railroads must have a projected coordinate system")

    if canal is not None:
        canalSR = arcpy.Describe(canal).spatialReference
        if canalSR.type == "Projected":
            pass
        else:
            raise Exception("Input canals must have projected coordinate system")

    # check that input network is shapefile
    if seg_network.endswith(".shp"):
        pass
    else:
        raise Exception("Input network must be a shapefile (.shp)")

    # check that input network doesn't have field "objectid" already
    seg_network_fields = [f.name for f in arcpy.ListFields(seg_network)]

    # add flowline segment id field ('SegID') for more 'stable' joining
    if 'SegID' not in seg_network_fields:
        arcpy.AddField_management(seg_network, 'SegID', 'SHORT')
        with arcpy.da.UpdateCursor(seg_network, ['FID', 'SegID']) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

    # create buffers for analyses
    # if 'Buffers' folder doesn't exist, create it
    if not os.path.exists(os.path.dirname(seg_network) + "/Buffers"):
        os.mkdir(os.path.dirname(seg_network) + "/Buffers")
    # create segment midpoints
    midpoints = scratch + "/midpoints"
    arcpy.FeatureVerticesToPoints_management(seg_network, midpoints, "MID")
    # remove unwanted fields from midpoints
    fields = arcpy.ListFields(midpoints)
    arcpy.AddMessage(fields)
    keep = ['SegID']
    drop = []

    for field in fields:
        if not field.required and field.name not in keep and field.type <> 'Geometry':
            drop.append(field.name)
    if len(drop) > 0:
        arcpy.DeleteField_management(midpoints, drop)

    # create midpoint 30 m buffer
    midpoint_buffer = scratch + "/midpoint_buffer"
    arcpy.Buffer_analysis(midpoints, midpoint_buffer, "100 Meters", "", "", "NONE")
    # if network 30 meter buffer doesn't exist, create it
    if not os.path.exists(os.path.dirname(seg_network) + "/Buffers/buffer_30m.shp"):
        buf_30m = os.path.dirname(seg_network) + "/Buffers/buffer_30m.shp"
        arcpy.Buffer_analysis(seg_network, buf_30m, "30 Meters", "", "FLAT", "NONE")
    else:
        buf_30m = os.path.dirname(seg_network) + "/Buffers/buffer_30m.shp"
    # if network 100 meter buffer doesn't exist, create it
    if not os.path.exists(os.path.dirname(seg_network) + "/Buffers/buffer_100m.shp"):
        buf_100m = os.path.dirname(seg_network) + "/Buffers/buffer_100m.shp"
        arcpy.Buffer_analysis(seg_network, buf_100m, "100 Meters", "", "FLAT", "NONE")
    else:
        buf_100m = os.path.dirname(seg_network) + "/Buffers/buffer_100m.shp"


    # name and create output folder
    j = 1
    while os.path.exists(projPath + "/02_Analyses/Output_" + str(j)):
        j += 1
    os.mkdir(projPath + "/02_Analyses/Output_" + str(j))

    # copy input segment network to output
    out_network = projPath + "/02_Analyses/Output_" + str(j) + "/" + out_name + ".shp"
    arcpy.CopyFeatures_management(seg_network, out_network)

    # run geo attributes function
    arcpy.AddMessage('Adding "iGeo" attributes to network')
    igeo_attributes(out_network, DEM, FlowAcc, midpoint_buffer, scratch)

    # run vegetation attributes function
    arcpy.AddMessage('Adding "iVeg" attributes to network')
    iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, out_network, scratch)

    # run ipc attributes function
    arcpy.AddMessage('Adding "iPC" attributes to network')
    ipc_attributes(out_network, road, railroad, canal, valley_bottom, buf_30m, buf_100m, landuse, scratch)

    # fun write xml function
    arcpy.AddMessage('Writing project xml')
    if FlowAcc is None:
        DrAr = os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"
    else:
        DrAr = os.path.dirname(DEM) + "/Flow/" + os.path.basename(FlowAcc)
    writexml(projPath, projName, hucID, hucName, coded_veg, coded_hist, seg_network, DEM, valley_bottom, landuse,
             FlowAcc, DrAr, road, railroad, canal, buf_30m, buf_100m, out_network)

    arcpy.CheckInExtension("spatial")


def igeo_attributes(out_network, DEM, FlowAcc, midpoint_buffer, scratch):

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

    # add flowline segment id field ('SegID') for more 'stable' joining
    if 'SegID' not in network_fields:
        arcpy.AddField_management(out_network, 'SegID', 'SHORT')
        with arcpy.da.UpdateCursor(out_network, ['FID', 'SegID']) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

    # function to attribute start/end elevation (dem z) to each flowline segment
    def zSeg(vertexType, outField):
        # create start/end points for each flowline segment
        tmp_pts = arcpy.FeatureVerticesToPoints_management(out_network, os.path.join(scratch, 'tmp_pts'), vertexType)
        # create 50 meter buffer around each start/end point
        tmp_buff = arcpy.Buffer_analysis(tmp_pts, os.path.join(scratch, 'tmp_buff'), '30 Meters')
        # get min dem z value within each buffer
        # note: zonal stats as table does not support overlapping polygons so we will check which
        #       segment buffers output was produced for and which we need to run tool on again
        zTbl = arcpy.sa.ZonalStatisticsAsTable(tmp_buff, 'SegID', DEM, os.path.join(scratch, 'zTbl'), 'DATA', 'MINIMUM')
        # get list of segment buffers where zonal stats tool produced output
        haveZList = [row[0] for row in arcpy.da.SearchCursor(zTbl, 'SegID')]
        # create dictionary to hold all segment buffer min dem z values
        zDict = {}
        # add min dem z values to dictionary
        with arcpy.da.SearchCursor(zTbl, ['SegID', 'MIN']) as cursor:
            for row in cursor:
                zDict[row[0]] = row[1]
        # create list of overlapping buffer segments (i.e., where zonal stats tool did not produce output)
        needZList = []
        with arcpy.da.SearchCursor(tmp_buff, ['SegID']) as cursor:
            for row in cursor:
                if row[0] not in haveZList:
                    needZList.append(row[0])
        # run zonal stats until we have output for each overlapping buffer segment
        while(True):
            # create tuple of segment ids where still need dem z values
            needZ = ()
            for seg in needZList:
                if seg not in needZ:
                    needZ += (seg, )
            # use the segment id tuple to create selection query and run zonal stats tool
            if len(needZ) == 1:
                quer = '"SegID" = ' + str(needZ[0])
            else:
                quer = '"SegID" IN ' + str(needZ)
            tmp_buff_lyr = arcpy.MakeFeatureLayer_management(tmp_buff, 'tmp_buff_lyr')
            arcpy.SelectLayerByAttribute_management(tmp_buff_lyr, 'NEW_SELECTION', quer)
            stat = arcpy.sa.ZonalStatisticsAsTable(tmp_buff_lyr, 'SegID', DEM, os.path.join(scratch, 'stat'), 'DATA', 'MINIMUM')
            # add segment z values from zonal stats table to main dictionary
            with arcpy.da.SearchCursor(stat, ['SegID', 'MIN']) as cursor:
                for row in cursor:
                    zDict[row[0]] = row[1]
            # create list of segments that were run and remove from 'need to run' list
            haveZList2 = [row[0] for row in arcpy.da.SearchCursor(stat, 'SegID')]
            for seg in haveZList2:
                needZList.remove(seg)
            # if need to run list is empty exit while loop
            if len(needZList) == 0:
                break

        arcpy.AddField_management(out_network, outField, "DOUBLE")
        with arcpy.da.UpdateCursor(out_network, ['SegID', outField]) as cursor:
            for row in cursor:
                try:
                    aKey = row[0]
                    row[1] = zDict[aKey]
                    cursor.updateRow(row)
                except:
                    pass

        arcpy.Delete_management(stat)
        arcpy.Delete_management(zTbl)
        arcpy.Delete_management(tmp_pts)
        arcpy.Delete_management(tmp_buff)

    # run zSeg function for start/end of each network segment
    zSeg('START', 'iGeo_ElMax')
    zSeg('END', 'iGeo_ElMin')


    # add slope
    arcpy.AddField_management(out_network, "iGeo_Len", "DOUBLE")
    arcpy.CalculateField_management(out_network, "iGeo_Len", '!shape.length@meters!', "PYTHON_9.3")
    arcpy.AddField_management(out_network, "iGeo_Slope", "DOUBLE")
    with arcpy.da.UpdateCursor(out_network, ["iGeo_ElMax", "iGeo_ElMin", "iGeo_Len", "iGeo_Slope"]) as cursor:
        for row in cursor:
            row[3] = (abs(row[0] - row[1]))/row[2]
            cursor.updateRow(row)
    with arcpy.da.UpdateCursor(out_network, "iGeo_Slope") as cursor: # fix slope values of 0
        for row in cursor:
            if row[0] == 0.0:
                row[0] = 0.0001
            else:
                pass
            cursor.updateRow(row)

    # get DA values
    if FlowAcc is None:
        arcpy.AddMessage("calculating drainage area")
        calc_drain_area(DEM)
    elif os.path.exists(os.path.dirname(DEM) + "/Flow"):
        pass
    else:
        os.mkdir(os.path.dirname(DEM) + "/Flow")
        arcpy.CopyRaster_management(FlowAcc, os.path.dirname(DEM) + "/Flow/" + os.path.basename(FlowAcc))

    if FlowAcc is None:
        DrArea = os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"
    else:
        DrArea = os.path.dirname(DEM) + "/Flow/" + os.path.basename(FlowAcc)

    drarea_zs = scratch + "/drarea_zs"
    ZonalStatisticsAsTable(midpoint_buffer, "SegID", DrArea, drarea_zs, 'DATA', "MAXIMUM")
    arcpy.JoinField_management(out_network, "SegID", drarea_zs, "SEGID", "MAX")

    arcpy.AddField_management(out_network, "iGeo_DA", "DOUBLE")
    with arcpy.da.UpdateCursor(out_network, ["MAX", "iGeo_DA"]) as cursor:
        for row in cursor:
            if row[0] == 0:
                row[1] = 0.1
            else:
                row[1] = row[0]
            cursor.updateRow(row)

    arcpy.DeleteField_management(out_network, "MAX")
    del drarea_zs

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
    ZonalStatisticsAsTable(buf_100m, "SegID", veg_lookup, ex_100_zs, 'DATA', "MEAN")
    arcpy.JoinField_management(out_network, "SegID", ex_100_zs, "SEGID", "MEAN")
    arcpy.AddField_management(out_network, "iVeg_100EX", "DOUBLE")
    with arcpy.da.UpdateCursor(out_network, ["MEAN", "iVeg_100EX"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(out_network, "MEAN")
    del ex_100_zs

    # get iVeg_30EX
    ex_30_zs = scratch + "/ex_30_zs"
    ZonalStatisticsAsTable(buf_30m, "SegID", veg_lookup, ex_30_zs, 'DATA', "MEAN")
    arcpy.JoinField_management(out_network, "SegID", ex_30_zs, "SEGID", "MEAN")
    arcpy.AddField_management(out_network, "iVeg_30EX", "DOUBLE")
    with arcpy.da.UpdateCursor(out_network, ["MEAN", "iVeg_30EX"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(out_network, "MEAN")
    del ex_30_zs, veg_lookup

    # get iVeg_100PT
    hist_veg_lookup = Lookup(coded_hist, "VEG_CODE")
    pt_100_zs = scratch + "/pt_100_zs"
    ZonalStatisticsAsTable(buf_100m, "SegID", hist_veg_lookup, pt_100_zs, 'DATA', "MEAN")
    arcpy.JoinField_management(out_network, "SegID", pt_100_zs, "SEGID", "MEAN")
    arcpy.AddField_management(out_network, "iVeg_100PT", "DOUBLE")
    with arcpy.da.UpdateCursor(out_network, ["MEAN", "iVeg_100PT"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(out_network, "MEAN")
    del pt_100_zs

    # get iVeg_30PT
    pt_30_zs = scratch + "/pt_30_zs"
    ZonalStatisticsAsTable(buf_30m, "SegID", hist_veg_lookup, pt_30_zs, 'DATA', "MEAN")
    arcpy.JoinField_management(out_network, "SegID", pt_30_zs, "SEGID", "MEAN")
    arcpy.AddField_management(out_network, "iVeg_30PT", "DOUBLE")
    with arcpy.da.UpdateCursor(out_network, ["MEAN", "iVeg_30PT"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(out_network, "MEAN")
    del pt_30_zs, hist_veg_lookup


def ipc_attributes(out_network, road, railroad, canal, valley_bottom, buf_30m, buf_100m, landuse, scratch):

    # if fields already exist, delete them
    network_fields = [f.name for f in arcpy.ListFields(out_network)]
    if "iPC_RoadX" in network_fields:
        arcpy.DeleteField_management(out_network, "iPC_RoadX")
    if "iPC_RoadAd" in network_fields:
        arcpy.DeleteField_management(out_network, "iPC_RoadAd")
    if "iPC_RR" in network_fields:
        arcpy.DeleteField_management(out_network, "iPC_RR")
    if "iPC_Canal" in network_fields:
        arcpy.DeleteField_management(out_network, "iPC_Canal")
    if "iPC_LU" in network_fields:
        arcpy.DeleteField_management(out_network, "iPC_LU")

    # get iPC_RoadX
    if road is None:
        arcpy.AddField_management(out_network, "iPC_RoadX", "DOUBLE")
        with arcpy.da.UpdateCursor(out_network, "iPC_RoadX") as cursor:
            for row in cursor:
                row[0] = 10000.0
                cursor.updateRow(row)
    else:
        roadx = scratch + "/roadx"
        arcpy.Intersect_analysis([out_network, road], roadx, "", "", "POINT")
        roadx_mts = scratch + "/roadx_mts"
        arcpy.MultipartToSinglepart_management(roadx, roadx_mts)

        roadxcount = arcpy.GetCount_management(roadx_mts)
        roadxct = int(roadxcount.getOutput(0))
        if roadxct < 1:
            arcpy.AddField_management(out_network, "iPC_RoadX", "DOUBLE")
            with arcpy.da.UpdateCursor(out_network, "iPC_RoadX") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        else:
            arcpy.env.extent = out_network
            ed_roadx = EucDistance(roadx, "", 5)
            zs_roadx = scratch + "/zs_roadx"
            ZonalStatisticsAsTable(buf_30m, "SegID", ed_roadx, zs_roadx, 'DATA', "MINIMUM")
            arcpy.JoinField_management(out_network, "SegID", zs_roadx, "SEGID", "MIN")
            arcpy.AddField_management(out_network, "iPC_RoadX", "DOUBLE")
            with arcpy.da.UpdateCursor(out_network, ["MIN", "iPC_RoadX"]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)
            arcpy.DeleteField_management(out_network, "MIN")
            del ed_roadx, zs_roadx

    # iPC_RoadAd
    if road is None:
        arcpy.AddField_management(out_network, "iPC_RoadAd", "DOUBLE")
        with arcpy.da.UpdateCursor(out_network, "iPC_RoadAd") as cursor:
            for row in cursor:
                row[0] = 10000.0
                cursor.updateRow(row)
    else:
        road_subset = scratch + '/road_subset'
        arcpy.Clip_analysis(road, valley_bottom, road_subset)
        road_mts = scratch + "/road_mts"
        arcpy.MultipartToSinglepart_management(road_subset, road_mts)

        roadcount = arcpy.GetCount_management(road_mts)
        roadct = int(roadcount.getOutput(0))
        if roadct < 1:
            arcpy.AddField_management(out_network, "iPC_RoadAd", "DOUBLE")
            with arcpy.da.UpdateCursor(out_network, "iPC_RoadAd") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        else:
            arcpy.env.extent = out_network
            ed_roadad = EucDistance(road_subset, "", 5)
            zs_roadad = scratch + "/zs_roadad"
            ZonalStatisticsAsTable(buf_30m, "SegID", ed_roadad, zs_roadad, 'DATA', "MEAN") # might try mean here to make it less restrictive
            arcpy.JoinField_management(out_network, "SegID", zs_roadad, "SEGID", "MEAN")
            arcpy.AddField_management(out_network, "iPC_RoadAd", "DOUBLE")
            with arcpy.da.UpdateCursor(out_network, ["MEAN", "iPC_RoadAd"]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)
            arcpy.DeleteField_management(out_network, "MEAN")
            del ed_roadad, zs_roadad

    # iPC_RR
    if railroad is None:
        arcpy.AddField_management(out_network, "iPC_RR", "DOUBLE")
        with arcpy.da.UpdateCursor(out_network, "iPC_RR") as cursor:
            for row in cursor:
                row[0] = 10000.0
                cursor.updateRow(row)
    else:
        rr_subset = scratch + '/rr_subset'
        arcpy.Clip_analysis(railroad, valley_bottom, rr_subset)
        rr_mts = scratch + "/rr_mts"
        arcpy.MultipartToSinglepart_management(rr_subset, rr_mts)

        rrcount = arcpy.GetCount_management(rr_mts)
        rrct = int(rrcount.getOutput(0))
        if rrct < 1:
            arcpy.AddField_management(out_network, "iPC_RR")
            with arcpy.da.UpdateCursor(out_network, "iPC_RR") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        else:
            arcpy.env.extent = out_network
            ed_rr = EucDistance(rr_subset, "", 30)
            zs_rr = scratch + "/zs_rr"
            ZonalStatisticsAsTable(buf_30m, "SegID", ed_rr, zs_rr, 'DATA', "MEAN")
            arcpy.JoinField_management(out_network, "SegID", zs_rr, "SEGID", "MEAN")
            arcpy.AddField_management(out_network, "iPC_RR", "DOUBLE")
            with arcpy.da.UpdateCursor(out_network, ["MEAN", "iPC_RR"]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)
            arcpy.DeleteField_management(out_network, "MEAN")
            del ed_rr, zs_rr

    #iPC_Canal
    if canal is None:
        arcpy.AddField_management(out_network, "iPC_Canal", "DOUBLE")
        with arcpy.da.UpdateCursor(out_network, "iPC_Canal") as cursor:
            for row in cursor:
                row[0] = 10000.0
                cursor.updateRow(row)
    else:
        canal_subset = scratch + '/canal_subset'
        arcpy.Clip_analysis(canal, valley_bottom, canal_subset)
        canal_mts = scratch + "/canal_mts"
        arcpy.MultipartToSinglepart_management(canal_subset, canal_mts)

        canalcount = arcpy.GetCount_management(canal_mts)
        canalct = int(canalcount.getOutput(0))
        if canalct < 1:
            arcpy.AddField_management(out_network, "iPC_Canal", "DOUBLE")
            with arcpy.da.UpdateCursor(out_network, "iPC_Canal") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        else:
            arcpy.env.extent = out_network
            ed_canal = EucDistance(canal_subset, "", 30)
            zs_canal = scratch + "/zs_canal"
            ZonalStatisticsAsTable(buf_30m, "SegID", ed_canal, zs_canal, 'DATA', "MEAN")
            arcpy.JoinField_management(out_network, "SegID", zs_canal, "SEGID", "MEAN")
            arcpy.AddField_management(out_network, "iPC_Canal", "DOUBLE")
            with arcpy.da.UpdateCursor(out_network, ["MEAN", "iPC_Canal"]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)
            arcpy.DeleteField_management(out_network, "MEAN")
            del ed_canal, zs_canal

    # iPC_LU
    lu_landuse = Lookup(landuse, "CODE")
    zs_landuse = scratch + "/zs_landuse"
    ZonalStatisticsAsTable(buf_100m, "SegID", lu_landuse, zs_landuse, 'DATA', "MEAN")
    arcpy.JoinField_management(out_network, "SegID", zs_landuse, "SEGID", "MEAN")
    arcpy.AddField_management(out_network, "iPC_LU", "DOUBLE")
    with arcpy.da.UpdateCursor(out_network, ["MEAN", "iPC_LU"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(out_network, "MEAN")
    del lu_landuse, zs_landuse


def calc_drain_area(DEM):
    DEMdesc = arcpy.Describe(DEM)
    height = DEMdesc.meanCellHeight
    width = DEMdesc.meanCellWidth
    res = height * width
    resolution = int(res)

    # derive a flow accumulation raster from input DEM and covert to units of square kilometers
    filled_DEM = Fill(DEM)
    flow_direction = FlowDirection(filled_DEM)
    flow_accumulation = FlowAccumulation(flow_direction)
    DrainArea = flow_accumulation * resolution / 1000000

    if os.path.exists(os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"):
        arcpy.Delete_management(os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif")
        DrArea_path = os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"
        DrainArea.save(DrArea_path)
    else:
        os.mkdir(os.path.dirname(DEM) + "/Flow")
        DrArea_path = os.path.dirname(DEM) + "/Flow/DrainArea_sqkm.tif"
        DrainArea.save(DrArea_path)

def writexml(projPath, projName, hucID, hucName, coded_veg, coded_hist, seg_network, DEM, valley_bottom, landuse,
             FlowAcc, DrAr, road, railroad, canal, buf_30m, buf_100m, out_network):
    """write the xml file for the project"""
    if not os.path.exists(projPath + "/project.rs.xml"):

        # xml file
        xmlfile = projPath + "/project.rs.xml"

        # initiate xml file creation
        newxml = projectxml.ProjectXML(xmlfile, "BRAT", projName)

        # add metadata
        if not hucID == None:
            newxml.addMeta("HUCID", hucID, newxml.project)
        if not hucID == None:
            idlist = [int(x) for x in str(hucID)]
            if idlist[0] == 1 and idlist[1] == 7:
                newxml.addMeta("Region", "CRB", newxml.project)
        if not hucName == None:
            newxml.addMeta("Watershed", hucName, newxml.project)

        # add first realization
        newxml.addBRATRealization("BRAT Realization 1", rid="RZ1", dateCreated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  productVersion="3.0.1", guid=getUUID())

        # add inputs
        newxml.addProjectInput("Raster", "Existing Vegetation", coded_veg[coded_veg.find("01_Inputs"):], iid="EXVEG1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Existing Vegetation", ref="EXVEG1")
        newxml.addProjectInput("Raster", "Historic Vegetation", coded_hist[coded_hist.find("01_Inputs"):], iid="HISTVEG1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Historic Vegetation", ref="HISTVEG1")
        newxml.addProjectInput("Vector", "Segmented Network", seg_network[seg_network.find("01_Inputs"):], iid="NETWORK1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Network", ref="NETWORK1")
        newxml.addProjectInput("DEM", "DEM", DEM[DEM.find("01_Inputs"):], iid="DEM1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "DEM", ref="DEM1")
        newxml.addProjectInput("Vector", "Valley Bottom", valley_bottom[valley_bottom.find("01_Inputs"):], iid="VALLEY1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Valley", ref="VALLEY1")
        newxml.addProjectInput("Raster", "Land Use", landuse[landuse.find("01_Inputs"):], iid="LU1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Land Use", ref="LU1")

        # add optional inputs
        if FlowAcc == None:
            newxml.addBRATInput(newxml.BRATRealizations[0], "Flow", name="Drainage Area", path=DrAr[DrAr.find("01_Inputs"):], guid=getUUID())
        else:
            newxml.addProjectInput("Raster", "Drainage Area", DrAr[DrAr.find("01_Inputs"):], iid="DA1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Flow", ref="DA1")
        if not road == None:
            newxml.addProjectInput("Vector", "Roads", road[road.find("01_Inputs"):], iid="ROAD1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Roads", ref="ROAD1")
        if not railroad == None:
            newxml.addProjectInput("Vector", "Railroads", railroad[railroad.find("01_Inputs"):], iid="RR1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Railroads", ref="RR1")
        if not canal == None:
            newxml.addProjectInput("Vector", "Canals", canal[canal.find("01_Inputs"):], iid="CANAL1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Canals", ref="CANAL1")

        # add derived inputs
        newxml.addBRATInput(newxml.BRATRealizations[0], "Buffer", name="30m Buffer", path=buf_30m[buf_30m.find("01_Inputs"):], guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Buffer", name="100m Buffer", path=buf_100m[buf_100m.find("01_Inputs"):], guid=getUUID())

        # add output
        newxml.addOutput("BRAT Analysis", "Vector", "BRAT Input Table", out_network[out_network.find("02_Analyses"):], newxml.BRATRealizations[0], guid=getUUID())

        # write xml to this point
        newxml.write()

    else:
        # xml file
        xmlfile = projPath + "/project.rs.xml"

        #open existing xml
        exxml = projectxml.ExistingXML(xmlfile)

        bratr = exxml.rz.findall("BRAT")
        bratrf = bratr[-1]
        rname = bratrf.find("Name")
        k = 2
        while rname.text == "BRAT Realization" + str(k):
            k += 1

        # add additional realizations
        exxml.addBRATRealization("BRAT Realization " + str(k), rid="RZ" + str(k),
                                 dateCreated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), productVersion="3.0.1", guid=getUUID())

        # add inputs
        inputs = exxml.root.find("Inputs")

        dems = inputs.findall("DEM")
        demid = range(len(dems))
        for i in range(len(dems)):
            demid[i] = dems[i].get("id")
        dempath = range(len(dems))
        for i in range(len(dems)):
            dempath[i] = dems[i].find("Path").text

        for i in range(len(dempath)):
            if os.path.abspath(dempath[i]) == os.path.abspath(DEM[DEM.find("01_Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "DEM", ref=str(demid[i]))

        nlist = []
        for j in dempath:
            if os.path.abspath(DEM[DEM.find("01_Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("DEM", "DEM", DEM[DEM.find("01_Inputs"):], iid="DEM" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "DEM", ref="DEM" + str(k))

        raster = inputs.findall("Raster")
        rasterid = range(len(raster))
        for i in range(len(raster)):
            rasterid[i] = raster[i].get("id")
        rasterpath = range(len(raster))
        for i in range(len(raster)):
            rasterpath[i] = raster[i].find("Path").text

        for i in range(len(rasterpath)):
            if os.path.abspath(rasterpath[i]) == os.path.abspath(coded_veg[coded_veg.find("01_Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "Existing Vegetation", ref=str(rasterid[i]))
            elif os.path.abspath(rasterpath[i]) == os.path.abspath(coded_hist[coded_hist.find("01_Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "Historic Vegetation", ref=str(rasterid[i]))
            elif os.path.abspath(rasterpath[i]) == os.path.abspath(landuse[landuse.find("01_Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "Land Use", ref=str(rasterid[i]))

        if not FlowAcc == None:
            for i in range(len(rasterpath)):
                if os.path.abspath(rasterpath[i]) == os.path.abspath(DrAr[DrAr.find("01_Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Flow", ref=str(rasterid[i]))

        nlist = []
        for j in rasterpath:
            if os.path.abspath(coded_veg[coded_veg.find("01_Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Raster", "Existing Vegetation", coded_veg[coded_veg.find("01_Inputs"):], iid="EXVEG" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Existing Vegetation", ref="EXVEG" + str(k))
        nlist = []
        for j in rasterpath:
            if os.path.abspath(coded_hist[coded_hist.find("01_Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Raster", "Historic Vegetation", coded_hist[coded_hist.find("01_Inputs"):], iid="HISTVEG" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Historic Vegetation", ref="HISTVEG" + str(k))
        nlist = []
        for j in rasterpath:
            if os.path.abspath(landuse[landuse.find("01_Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Raster", "Land Use", landuse[landuse.find("01_Inputs"):], iid="LU" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Land Use", ref="LU" + str(k))

        if FlowAcc == None:
            exxml.addBRATInput(exxml.BRATRealizations[0], "Flow", "Drainage Area", DrAr[DrAr.find("01_Inputs"):],
                               guid=getUUID())
        else:
            nlist = []
            for j in rasterpath:
                if os.path.abspath(DrAr[DrAr.find("01_Inputs")]) == os.path.abspath(j):
                    nlist.append("yes")
                else:
                    nlist.append("no")
            if "yes" in nlist:
                pass
            else:
                flows = exxml.rz.findall(".//Flow")
                flowpath = range(len(flows))
                for i in range(len(flows)):
                    if flows[i].find("Path").text:
                        flowpath[i] = flows[i].find("Path").text
                        if os.path.abspath(flowpath[i]) == os.path.abspath(DrAr[DrAr.find("01_Inputs"):]):
                            flowguid = flows[i].attrib['guid']
                            exxml.addBRATInput(exxml.BRATRealizations[0], "Flow", "Drainage Area", path=DrAr[DrAr.find("01_Inputs"):], guid=flowguid)
                    else:
                        pass

        vector = inputs.findall("Vector")
        vectorid = range(len(vector))
        for i in range(len(vector)):
            vectorid[i] = vector[i].get("id")
        vectorpath = range(len(vector))
        for i in range(len(vector)):
            vectorpath[i] = vector[i].find("Path").text

        for i in range(len(vectorpath)):
            if os.path.abspath(vectorpath[i]) == os.path.abspath(seg_network[seg_network.find("01_Inputs"):]):
                DN = exxml.root.findall(".//Network")
                for x in range(len(DN)):
                    if DN[x].attrib['ref'] == vectorid[i]:
                        r = DN[x].findall(".//Buffer")
                        buf30_guid = r[0].attrib['guid']
                        buf100_guid = r[1].attrib['guid']
                    else:
                        r = []
                exxml.addBRATInput(exxml.BRATRealizations[0], "Network", ref=str(vectorid[i]))
                if len(r) > 0:
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "30m Buffer", path=buf_30m[buf_30m.find("01_Inputs"):], guid=buf30_guid)
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "100m Buffer", path=buf_100m[buf_100m.find("01_Inputs"):], guid=buf100_guid)
                else:
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "30m Buffer", path=buf_30m[buf_30m.find("01_Inputs"):])
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "100m Buffer", path=buf_100m[buf_100m.find("01_Inputs"):])
            elif os.path.abspath(vectorpath[i]) == os.path.abspath(valley_bottom[valley_bottom.find("01_Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "Valley", ref=str(vectorid[i]))
            if not road == None:
                if os.path.abspath(vectorpath[i]) == os.path.abspath(road[road.find("01_Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Roads", ref=str(vectorid[i]))
            if not railroad == None:
                if os.path.abspath(vectorpath[i]) == os.path.abspath(railroad[railroad.find("01_Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Railroads", ref=str(vectorid[i]))
            if not canal == None:
                if os.path.abspath(vectorpath[i]) == os.path.abspath(canal[canal.find("01_Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Canals", ref=str(vectorid[i]))

        nlist = []
        for j in vectorpath:
            if os.path.abspath(seg_network[seg_network.find("01_Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Vector", "Segmented Network", seg_network[seg_network.find("01_Inputs"):], iid="NETWORK" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Network", ref="NETWORK" + str(k))
            exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "30m Buffer",
                               path=os.path.dirname(seg_network[seg_network.find("01_Inputs"):]) + "/Buffers/buffer_30m.shp", guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "100m Buffer",
                               path=os.path.dirname(seg_network[seg_network.find("01_Inputs"):]) + "/Buffers/buffer_100m.shp", guid=getUUID())
        nlist = []
        for j in vectorpath:
            if os.path.abspath(valley_bottom[valley_bottom.find("01_Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Vector", "Valley Bottom", valley_bottom[valley_bottom.find("01_Inputs"):], iid="VALLEY" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Valley", ref="VALLEY" + str(k))

        if not road == None:
            nlist = []
            for j in vectorpath:
                if os.path.abspath(road[road.find("01_Inputs"):]) == os.path.abspath(j):
                    nlist.append("yes")
                else:
                    nlist.append("no")
            if "yes" in nlist:
                pass
            else:
                exxml.addProjectInput("Vector", "Roads", road[road.find("01_Inputs"):], iid="ROAD" + str(k), guid=getUUID())
                exxml.addBRATInput(exxml.BRATRealizations[0], "Roads", ref="ROAD" + str(k))

        if not railroad == None:
            nlist = []
            for j in vectorpath:
                if os.path.abspath(railroad[railroad.find("01_Inputs"):]) == os.path.abspath(j):
                    nlist.append("yes")
                else:
                    nlist.append("no")
            if "yes" in nlist:
                pass
            else:
                exxml.addProjectInput("Vector", "Railroads", iid="RR" + str(k), guid=getUUID())
                exxml.addBRATInput(exxml.BRATRealizations[0], "Railroads", ref="RR" + str(k))

        if not canal == None:
            nlist = []
            for j in vectorpath:
                if os.path.abspath(canal[canal.find("01_Inputs"):]) == os.path.abspath(j):
                    nlist.append("yes")
                else:
                    nlist.append("no")
            if "yes" in nlist:
                pass
            else:
                exxml.addProjectInput("Vector", "Canals", canal[canal.find("01_Inputs"):], iid="CANAL" + str(k), guid=getUUID())
                exxml.addBRATInput(exxml.BRATRealizations[0], "Canals", ref="CANAL" + str(k))

        # add output
        exxml.addOutput("BRAT Analysis", "Vector", "BRAT Input Table",
                        out_network[out_network.find("02_Analyses"):], exxml.BRATRealizations[0], guid=getUUID())

        # write xml
        exxml.write()


def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
        sys.argv[8],
        sys.argv[9],
        sys.argv[10],
        sys.argv[11],
        sys.argv[12],
        sys.argv[13],
        sys.argv[14],
        sys.argv[15])