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
import FindBraidedNetwork
import BRAT_Braid_Handler


def main(
    projPath,
    projName,
    hucID,
    hucName,
    seg_network,
    inDEM,
    FlowAcc,
    coded_veg,
    coded_hist,
    valley_bottom,
    road,
    railroad,
    canal,
    landuse,
    out_name,
    findClusters):
    if findClusters == 'false' or findClusters is None:
        findClusters = False
    else:
        findClusters = True

    scratch = 'in_memory'
    #arcpy.env.workspace = scratch
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    # --check input projections--
    try:
        networkSR = arcpy.Describe(seg_network).spatialReference
    except:
        raise Exception("There was a problem finding the spatial reference of the stream network. "
                       + "This is commonly caused by trying to run the Table tool directly after running the project "
                       + "builder. Restarting ArcGIS fixes this problem most of the time.")
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

    # --check that input network is shapefile--
    if seg_network.endswith(".shp"):
        pass
    else:
        raise Exception("Input network must be a shapefile (.shp)")

    # --check input network fields--
    # add flowline reach id field ('ReachID') if it doens't already exist
    # this field allows for more for more 'stable' joining
    fields = [f.name for f in arcpy.ListFields(seg_network)]
    if 'ReachID' not in fields:
        arcpy.AddField_management(seg_network, 'ReachID', 'SHORT')
        with arcpy.da.UpdateCursor(seg_network, ['FID', 'ReachID']) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

    # --create network buffers for analyses--
    # create 'Buffers' folder if it doesn't exist
    if not os.path.exists(os.path.dirname(seg_network) + "/Buffers"):
        os.mkdir(os.path.dirname(seg_network) + "/Buffers")
    # create network segment midpoints
    midpoints = arcpy.FeatureVerticesToPoints_management(seg_network, scratch + "/midpoints", "MID")
    # remove unwanted fields from midpoints
    fields = arcpy.ListFields(midpoints)
    keep = ['ReachID']
    drop = []
    for field in fields:
        if not field.required and field.name not in keep and field.type <> 'Geometry':
            drop.append(field.name)
    if len(drop) > 0:
        arcpy.DeleteField_management(midpoints, drop)
    # create midpoint 100 m buffer
    midpoint_buffer = arcpy.Buffer_analysis(midpoints, scratch + "/midpoint_buffer", "100 Meters")
    # create network 30 m buffer
    buf_30m = os.path.dirname(seg_network) + "/Buffers/buffer_30m.shp"
    arcpy.Buffer_analysis(seg_network, buf_30m, "30 Meters", "", "ROUND")
    # create network 100 m buffer
    buf_100m = os.path.dirname(seg_network) + "/Buffers/buffer_100m.shp"
    arcpy.Buffer_analysis(seg_network, buf_100m, "100 Meters", "", "ROUND")

    # name and create output folder
    j = 1
    while os.path.exists(projPath + "/02_Analyses/Output_" + str(j)):
        j += 1
    os.mkdir(projPath + "/02_Analyses/Output_" + str(j))

    # copy input segment network to output folder
    if out_name.endswith('.shp'):
        out_network = projPath + "/02_Analyses/Output_" + str(j) + "/" + out_name
    else:
        out_network = projPath + "/02_Analyses/Output_" + str(j) + "/" + out_name + ".shp"

    arcpy.CopyFeatures_management(seg_network, out_network)

    # run geo attributes function
    arcpy.AddMessage('Adding "iGeo" attributes to network')
    igeo_attributes(out_network, inDEM, FlowAcc, midpoint_buffer, scratch)

    # run vegetation attributes function
    arcpy.AddMessage('Adding "iVeg" attributes to network')
    iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, out_network, scratch)

    # run ipc attributes function if conflict layers are defined by user
    if road is not None and valley_bottom is not None:
        arcpy.AddMessage('Adding "iPC" attributes to network')
        ipc_attributes(out_network, road, railroad, canal, valley_bottom, buf_30m, buf_100m, landuse, scratch, projPath)

    addMainstemAttribute(out_network)
    # find braided reaches
    FindBraidedNetwork.main(out_network, canal)

    if findClusters:
        clusters = BRAT_Braid_Handler.findClusters(out_network)
        BRAT_Braid_Handler.addClusterID(out_network, clusters)
        arcpy.AddMessage("Finding Clusters...")


    # run write xml function
    arcpy.AddMessage('Writing project xml')
    if FlowAcc is None:
        DrAr = os.path.dirname(inDEM) + "/Flow/DrainArea_sqkm.tif"
    else:
        DrAr = os.path.dirname(inDEM) + "/Flow/" + os.path.basename(FlowAcc)
    writexml(projPath, projName, hucID, hucName, coded_veg, coded_hist, seg_network, inDEM, valley_bottom, landuse,
             FlowAcc, DrAr, road, railroad, canal, buf_30m, buf_100m, out_network)

    arcpy.CheckInExtension("spatial")

# zonal statistics within buffer function
# dictionary join field function
def zonalStatsWithinBuffer(buffer, ras, statType, statField, outFC, outFCField, scratch):
    # get input raster stat value within each buffer
    # note: zonal stats as table does not support overlapping polygons so we will check which
    #       reach buffers output was produced for and which we need to run tool on again
    statTbl = arcpy.sa.ZonalStatisticsAsTable(buffer, 'ReachID', ras, os.path.join(scratch, 'statTbl'), 'DATA', statType)
    # get list of segment buffers where zonal stats tool produced output
    haveStatList = [row[0] for row in arcpy.da.SearchCursor(statTbl, 'ReachID')]
    # create dictionary to hold all reach buffer min dem z values
    statDict = {}
    # add buffer raster stat values to dictionary
    with arcpy.da.SearchCursor(statTbl, ['ReachID', statField]) as cursor:
        for row in cursor:
            statDict[row[0]] = row[1]
    # create list of overlapping buffer reaches (i.e., where zonal stats tool did not produce output)
    needStatList = []
    with arcpy.da.SearchCursor(buffer, ['ReachID']) as cursor:
        for row in cursor:
            if row[0] not in haveStatList:
                needStatList.append(row[0])
    # run zonal stats until we have output for each overlapping buffer segment
    stat = None
    tmp_buff_lyr = None
    while len(needStatList) > 0:
        # create tuple of segment ids where still need raster values
        needStat = ()
        for reach in needStatList:
            if reach not in needStat:
                needStat += (reach,)
        # use the segment id tuple to create selection query and run zonal stats tool
        if len(needStat) == 1:
            quer = '"ReachID" = ' + str(needStat[0])
        else:
            quer = '"ReachID" IN ' + str(needStat)
        tmp_buff_lyr = arcpy.MakeFeatureLayer_management(buffer, 'tmp_buff_lyr')
        arcpy.SelectLayerByAttribute_management(tmp_buff_lyr, 'NEW_SELECTION', quer)
        stat = arcpy.sa.ZonalStatisticsAsTable(tmp_buff_lyr, 'ReachID', ras, os.path.join(scratch, 'stat'), 'DATA', statType)
        # add segment stat values from zonal stats table to main dictionary
        with arcpy.da.SearchCursor(stat, ['ReachID', statField]) as cursor:
            for row in cursor:
                statDict[row[0]] = row[1]
        # create list of reaches that were run and remove from 'need to run' list
        haveStatList2 = [row[0] for row in arcpy.da.SearchCursor(stat, 'ReachID')]
        for reach in haveStatList2:
            needStatList.remove(reach)

    # populate dictionary value to output field by ReachID
    with arcpy.da.UpdateCursor(outFC, ['ReachID', outFCField]) as cursor:
        for row in cursor:
            try:
                aKey = row[0]
                row[1] = statDict[aKey]
                cursor.updateRow(row)
            except:
                pass
    statDict.clear()
    # delete temp fcs, tbls, etc.
    #items = [statTbl, haveStatList, haveStatList2, needStatList, stat, tmp_buff_lyr, needStat]
    items = [statTbl, stat, tmp_buff_lyr]
    for item in items:
        if item is not None:
            arcpy.Delete_management(item)

# geo attributes function
# calculates min and max elevation, length, slope, and drainage area for each flowline segment
def igeo_attributes(out_network, inDEM, FlowAcc, midpoint_buffer, scratch):

    # if fields already exist, delete them
    fields = [f.name for f in arcpy.ListFields(out_network)]
    drop = ["iGeo_ElMax", "iGeo_ElMin", "iGeo_Len", "iGeo_Slope", "iGeo_DA"]
    for field in fields:
        if field in drop:
            arcpy.DeleteField_management(out_network, field)

    # add flowline segment id field ('ReachID') for more 'stable' joining
    if 'ReachID' not in fields:
        arcpy.AddField_management(out_network, 'ReachID', 'LONG')
        with arcpy.da.UpdateCursor(out_network, ['FID', 'ReachID']) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

    #  --smooth input dem by 3x3 cell window--
    #  define raster environment settings
    desc = arcpy.Describe(inDEM)
    arcpy.env.extent = desc.Extent
    arcpy.env.outputCoordinateSystem = desc.SpatialReference
    arcpy.env.cellSize = desc.meanCellWidth
    # calculate mean z over 3x3 cell window
    neighborhood = NbrRectangle(3, 3, "CELL")
    tmpDEM = FocalStatistics(inDEM, neighborhood, 'MEAN')
    # clip smoothed dem to input dem
    DEM = ExtractByMask(tmpDEM, inDEM)

    # function to attribute start/end elevation (dem z) to each flowline segment
    def zSeg(vertexType, outField):
        # create start/end points for each flowline reach segment
        tmp_pts = os.path.join(scratch, 'tmp_pts')
        arcpy.FeatureVerticesToPoints_management(out_network, tmp_pts, vertexType)
        # create 30 meter buffer around each start/end point
        tmp_buff = os.path.join(scratch, 'tmp_buff')
        arcpy.Buffer_analysis(tmp_pts, tmp_buff, '30 Meters')
        # get min dem z value within each buffer
        arcpy.AddField_management(out_network, outField, "DOUBLE")
        zonalStatsWithinBuffer(tmp_buff, DEM, 'MINIMUM', 'MIN', out_network, outField, scratch)

        # delete temp fcs, tbls, etc.
        items = [tmp_pts, tmp_buff]
        for item in items:
            arcpy.Delete_management(item)

    # run zSeg function for start/end of each network segment
    zSeg('START', 'iGeo_ElMax')
    zSeg('END', 'iGeo_ElMin')

    # calculate network reach slope
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
            cursor.updateRow(row)

    # get DA values
    if FlowAcc is None:
        arcpy.AddMessage("calculating drainage area")
        calc_drain_area(DEM, inDEM)
    # todo: try and figure out what this elif is doing
    elif os.path.exists(os.path.dirname(inDEM) + "/Flow"):
        pass
    else:
        os.mkdir(os.path.dirname(inDEM) + "/Flow")
        arcpy.CopyRaster_management(FlowAcc, os.path.dirname(inDEM) + "/Flow/" + os.path.basename(FlowAcc))

    if FlowAcc is None:
        DrArea = os.path.dirname(inDEM) + "/Flow/DrainArea_sqkm.tif"
    else:
        DrArea = os.path.dirname(inDEM) + "/Flow/" + os.path.basename(FlowAcc)
    # Todo: check this bc it seems wrong to pull from midpoint buffer

    # add drainage area 'iGeo_DA' field to flowline network
    arcpy.AddField_management(out_network, "iGeo_DA", "DOUBLE")
    # get max drainage area within 100 m midpoint buffer
    zonalStatsWithinBuffer(midpoint_buffer, DrArea, "MAXIMUM", 'MAX', out_network, "iGeo_DA", scratch)

    # replace '0' drainage area values with tiny value
    with arcpy.da.UpdateCursor(out_network, ["iGeo_DA"]) as cursor:
        for row in cursor:
            if row[0] == 0:
                row[0] = 0.00000001
            cursor.updateRow(row)


# vegetation attributes function
# calculates both existing and potential mean vegetation value within 30 m and 100 m buffer of each stream segment
def iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, out_network, scratch):

    # if fields already exist, delete them
    fields = [f.name for f in arcpy.ListFields(out_network)]
    drop = ["iVeg_100EX", "iVeg_30EX", "iVeg_100PT", "iVeg_30PT"]
    for field in fields:
        if field in drop:
            arcpy.DeleteField_management(out_network, field)

    # --existing vegetation values--
    veg_lookup = Lookup(coded_veg, "VEG_CODE")
    # add mean veg value 'iVeg_100EX' field to flowline network
    arcpy.AddField_management(out_network, "iVeg_100EX", "DOUBLE")
    # get mean existing veg value within 100 m buffer
    zonalStatsWithinBuffer(buf_100m, veg_lookup, 'MEAN', 'MEAN', out_network, "iVeg_100EX", scratch)

    # add mean veg value 'iVeg_VT30EX' field to flowline network
    arcpy.AddField_management(out_network, "iVeg_30EX", "DOUBLE")
    # get mean existing veg value within 30 m buffer
    zonalStatsWithinBuffer(buf_30m, veg_lookup, 'MEAN', 'MEAN', out_network, "iVeg_30EX", scratch)

    # delete temp fcs, tbls, etc.
    items = [veg_lookup]
    for item in items:
        arcpy.Delete_management(item)

    # --historic (i.e., potential) vegetation values--
    hist_veg_lookup = Lookup(coded_hist, "VEG_CODE")

    # add mean veg value 'iVeg_100PT' field to flowline network
    arcpy.AddField_management(out_network, "iVeg_100PT", "DOUBLE")
    # get mean potential veg value within 100 m buffer
    zonalStatsWithinBuffer(buf_100m, hist_veg_lookup, 'MEAN', 'MEAN', out_network, "iVeg_100PT", scratch)

    # add mean veg value 'iVeg_30PT' field to flowline network
    arcpy.AddField_management(out_network, "iVeg_30PT", "DOUBLE")
    # get mean potential veg value within 30 m buffer
    zonalStatsWithinBuffer(buf_30m, hist_veg_lookup, 'MEAN', 'MEAN', out_network, "iVeg_30PT", scratch)

    # delete temp fcs, tbls, etc.
    items = [hist_veg_lookup]
    for item in items:
        arcpy.Delete_management(item)


# conflict potential function
# calculates distances from road intersections, adjacent roads, railroads and canals for each flowline segment
def ipc_attributes(out_network, road, railroad, canal, valley_bottom, buf_30m, buf_100m, landuse, scratch, projPath):

    # create temp directory
    from shutil import rmtree
    tempDir = projPath + '\Temp'
    if os.path.exists(tempDir):
        rmtree(tempDir)
    os.mkdir(tempDir)

    # if fields already exist, delete them
    fields = [f.name for f in arcpy.ListFields(out_network)]
    drop = ["iPC_RoadX", "iPC_RoadAd", "iPC_RR", "iPC_Canal", "iPC_LU"]
    for field in fields:
        if field in drop:
            arcpy.DeleteField_management(out_network, field)

    # calculate minimum distance from road-stream crossings ('iPC_RoadX')
    if road is not None:
        arcpy.AddField_management(out_network, "iPC_RoadX", "DOUBLE")
        roadx = tempDir + "\\roadx.shp"
        # create points at road-stream intersections
        arcpy.Intersect_analysis([out_network, road], roadx, "", "", "POINT")
        # get count of road-stream intersections
        roadx_mts = tempDir + "\\roadx_mts.shp"
        arcpy.MultipartToSinglepart_management(roadx, roadx_mts)
        roadxcount = arcpy.GetCount_management(roadx_mts)
        roadxct = int(roadxcount.getOutput(0))
        # if there are no road-stream crossings, set 'iPC_RoadsX' to high value (10000 m)
        if roadxct < 1:
            with arcpy.da.UpdateCursor(out_network, "iPC_RoadX") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        # if there are road-stream crossings, calculate distance
        else:
            # set extent to the stream network
            arcpy.env.extent = out_network
            # calculate euclidean distance from road-stream crossings
            ed_roadx = EucDistance(roadx, cell_size = 5)  # cell size of 5 m
            # get minimum distance from road-stream crossings within 30 m buffer of each network segment
            zonalStatsWithinBuffer(buf_30m, ed_roadx, "MINIMUM", 'MIN', out_network, "iPC_RoadX", scratch)

            # delete temp fcs, tbls, etc.
            items = [ed_roadx]
            for item in items:
                arcpy.Delete_management(item)

    # calculate mean distance from adjacent roads ('iPC_RoadAd')
    # here we only care about roads in the valley bottom
    if road is not None:
        arcpy.AddField_management(out_network, "iPC_RoadAd", "DOUBLE")
        # clip roads to the valley bottom
        road_subset = arcpy.Clip_analysis(road, valley_bottom, tempDir + '\\road_subset.shp')
        # get count of roads in the valley bottom
        road_mts = arcpy.MultipartToSinglepart_management(road_subset, tempDir + "\\road_mts.shp")
        roadcount = arcpy.GetCount_management(road_mts)
        roadct = int(roadcount.getOutput(0))
        # if there are no roads in the valley bottom, set 'iPC_RoadsAd' to high value (10000 m)
        if roadct < 1:
            with arcpy.da.UpdateCursor(out_network, "iPC_RoadAd") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        # if there are roads in the valley bottom, calculate distance
        else:
            # set extent to the stream network
            arcpy.env.extent = out_network
            # calculate euclidean distance from roads in the valley bottom
            ed_roadad = EucDistance(road_subset, cell_size = 5) # cell size of 5 m
            # get mean distance from roads in the valley bottom within 30 m buffer of each network segment
            zonalStatsWithinBuffer(buf_30m, ed_roadad, 'MEAN', 'MEAN', out_network, "iPC_RoadAd", scratch)

            # delete temp fcs, tbls, etc.
            items = [ed_roadad]
            for item in items:
                arcpy.Delete_management(item)

    # calculate mean distance from railroads ('iPC_RR')
    # here we only care about railroads in the valley bottom
    if railroad is not None:
        arcpy.AddField_management(out_network, "iPC_RR", "DOUBLE")
        # clip railroads to the valley bottom
        rr_subset = arcpy.Clip_analysis(railroad, valley_bottom, tempDir + '\\rr_subset.shp')
        # get count of railroads in the valley bottom
        rr_mts = arcpy.MultipartToSinglepart_management(rr_subset, tempDir + "\\rr_mts.shp")
        rrcount = arcpy.GetCount_management(rr_mts)
        rrct = int(rrcount.getOutput(0))
        # if there are not railroads in the valley bottom, set 'iPC_RR' to high value (10000 m)
        if rrct < 1:
            with arcpy.da.UpdateCursor(out_network, "iPC_RR") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        # if there are railroads in the valley bottom calculate distance
        else:
            # set extent to the flowline network
            arcpy.env.extent = out_network
            # calculate distance from railroads in the valley bottom
            ed_rr = EucDistance(rr_subset, cell_size = 5)  # cell size of 5 m
            # get mean distance from railroads in the valley bottom within 30 m buffer of each network segment
            zonalStatsWithinBuffer(buf_30m, ed_rr, 'MEAN', 'MEAN', out_network, "iPC_RR", scratch)

            # delete temp fcs, tbls, etc.
            items = [ed_rr]
            for item in items:
                arcpy.Delete_management(item)

    # calculate mean distance from canals ('iPC_Canal')
    # here we only care about canals in the valley bottom
    if canal is not None:
        arcpy.AddField_management(out_network, "iPC_Canal", "DOUBLE")
        # clip canals to the valley bottom
        canal_subset = arcpy.Clip_analysis(canal, valley_bottom, tempDir + '\\canal_subset.shp')
        # get count of canals in the valley bottom
        canal_mts = arcpy.MultipartToSinglepart_management(canal_subset, tempDir + "\\canal_mts.shp")
        canalcount = arcpy.GetCount_management(canal_mts)
        canalct = int(canalcount.getOutput(0))
        # if there are not canals in the valley bottom, set 'iPC_Canal' to high value (10000 m)
        if canalct < 1:
            with arcpy.da.UpdateCursor(out_network, "iPC_Canal") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        # if there are canals in the valley bottom, calculate distance
        else:
            # set extent to the stream network
            arcpy.env.extent = out_network
            # calculate euclidean distance from canals in the valley bottom
            ed_canal = EucDistance(canal_subset, cell_size = 5)  # cell size of 5 m
            # get mean distance from canals in the valley bottom within 30 m buffer of each network segment
            zonalStatsWithinBuffer(buf_30m, ed_canal, 'MEAN', 'MEAN', out_network, "iPC_Canal", scratch)

            # delete temp fcs, tbls, etc.
            items = [ed_canal]
            for item in items:
                arcpy.Delete_management(item)

    rmtree(tempDir)
    """
    This is the section of code that stores intermediary data in memory. In ArcMap 10.6, that crashes the program,
    so we're getting rid of it for now, and using a temp dir instead
    # get iPC_RoadX
    arcpy.AddField_management(out_network, "iPC_RoadX", "DOUBLE")
    if road is None:
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
            with arcpy.da.UpdateCursor(out_network, "iPC_RoadX") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        else:
            arcpy.env.extent = out_network
            # calculate euclidean distance from road-stream crossings
            ed_roadx = EucDistance(roadx, cell_size=5)  # cell size of 5 m
            # get minimum distance from road-stream crossings within 30 m buffer of each network segment
            roadxTbl = ZonalStatisticsAsTable(buf_30m, "SegID", ed_roadx, scratch + "/roadxTbl", 'DATA', "MINIMUM")
            # populate flowline network min distance 'iPC_RoadX' field
            dictJoinField(roadxTbl, 'MIN', out_network, "iPC_RoadX")
            # delete temp fcs, tbls, etc.
            items = [ed_roadx, roadxTbl]
            for item in items:
                arcpy.Delete_management(item)

    # iPC_RoadAd
    arcpy.AddField_management(out_network, "iPC_RoadAd", "DOUBLE")
    if road is None:
        with arcpy.da.UpdateCursor(out_network, "iPC_RoadAd") as cursor:
            for row in cursor:
                row[0] = 10000.0
                cursor.updateRow(row)
    else:
        road_subset = arcpy.Clip_analysis(road, valley_bottom, scratch + '/road_subset')
        road_mts = arcpy.MultipartToSinglepart_management(road_subset, scratch + "/road_mts")
        roadcount = arcpy.GetCount_management(road_mts)
        roadct = int(roadcount.getOutput(0))
        if roadct < 1:
            with arcpy.da.UpdateCursor(out_network, "iPC_RoadAd") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        else:
            arcpy.env.extent = out_network
            ed_roadad = EucDistance(road_subset, "", 5)
            roadadjTbl = ZonalStatisticsAsTable(buf_30m, "SegID", ed_roadad, scratch + "/roadadjTbl", 'DATA', "MEAN") # might try mean here to make it less restrictive
            # populate flowline network adjacent road distance "iPC_RoadAd" field
            dictJoinField(roadadjTbl, 'MEAN', out_network, "iPC_RoadAd")
            items = [ed_roadad, roadadjTbl]
            for item in items:
                arcpy.Delete_management(item)

    # iPC_RR
    arcpy.AddField_management(out_network, "iPC_RR")
    if railroad is None:
        with arcpy.da.UpdateCursor(out_network, "iPC_RR") as cursor:
            for row in cursor:
                row[0] = 10000.0
                cursor.updateRow(row)
    else:
        rr_subset = arcpy.Clip_analysis(railroad, valley_bottom, scratch + '/rr_subset')
        rr_mts = arcpy.MultipartToSinglepart_management(rr_subset, scratch + "/rr_mts")
        rrcount = arcpy.GetCount_management(rr_mts)
        rrct = int(rrcount.getOutput(0))
        if rrct < 1:

            with arcpy.da.UpdateCursor(out_network, "iPC_RR") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        else:
            arcpy.env.extent = out_network
            ed_rr = EucDistance(rr_subset, "", 30)
            rrTbl = ZonalStatisticsAsTable(buf_30m, "SegID", ed_rr, scratch + "/rrTable", 'DATA', "MEAN")
            dictJoinField(rrTbl, 'MEAN', out_network, "iPC_RR")
            items = [ed_rr, rrTbl]
            for item in items:
                arcpy.Delete_management(item)

    #iPC_Canal
    arcpy.AddField_management(out_network, "iPC_Canal", "DOUBLE")
    if canal is None:
        with arcpy.da.UpdateCursor(out_network, "iPC_Canal") as cursor:
            for row in cursor:
                row[0] = 10000.0
                cursor.updateRow(row)
    else:
        canal_subset = arcpy.Clip_analysis(canal, valley_bottom, scratch + '/canal_subset')
        canal_mts = arcpy.MultipartToSinglepart_management(canal_subset, scratch + "/canal_mts")

        canalcount = arcpy.GetCount_management(canal_mts)
        canalct = int(canalcount.getOutput(0))
        if canalct < 1:
            with arcpy.da.UpdateCursor(out_network, "iPC_Canal") as cursor:
                for row in cursor:
                    row[0] = 10000.0
                    cursor.updateRow(row)
        else:
            arcpy.env.extent = out_network
            ed_canal = EucDistance(canal_subset, "", 30)
            canalTbl = ZonalStatisticsAsTable(buf_30m, "SegID", ed_canal, scratch + "/canalTbl", 'DATA', "MEAN")
            dictJoinField(canalTbl, 'MEAN', out_network, "iPC_Canal")
            items = [ed_canal, canalTbl]
            for item in items:
                arcpy.Delete_management(item)   
    """ ##The code that supports in memory scratch spaces

    # calculate mean landuse value ('iPC_LU')
    if landuse is not None:
        arcpy.AddField_management(out_network, "iPC_LU", "DOUBLE")
        # create raster with just landuse code values
        lu_ras = Lookup(landuse, "LU_CODE")
        # calculate mean landuse value within 100 m buffer of each network segment
        zonalStatsWithinBuffer(buf_100m, lu_ras, 'MEAN', 'MEAN', out_network, "iPC_LU", scratch)

        # get percentage of each land use class in 100 m buffer of stream segment
        fields = [f.name for f in arcpy.ListFields(landuse)]

        if "LUI_Class" in fields:
            buf_fields = [f.name for f in arcpy.ListFields(buf_100m)]
            if 'oArea' not in buf_fields:
                arcpy.AddField_management(buf_100m, 'oArea', 'DOUBLE')
                with arcpy.da.UpdateCursor(buf_100m, ['SHAPE@AREA', 'oArea']) as cursor:
                    for row in cursor:
                        row[1] = row[0]
                        cursor.updateRow(row)
            landuse_poly = arcpy.RasterToPolygon_conversion(landuse, os.path.join(scratch, 'landuse_poly'), 'NO_SIMPLIFY', "LUI_Class")
            landuse_int = arcpy.Intersect_analysis([landuse_poly, buf_100m], os.path.join(scratch, 'landuse_int'))
            arcpy.AddField_management(landuse_int, 'propArea', 'DOUBLE')
            with arcpy.da.UpdateCursor(landuse_int, ['SHAPE@AREA', 'oArea', 'propArea']) as cursor:
                for row in cursor:
                    row[2] = row[0]/row[1]
                    cursor.updateRow(row)
            areaTbl = arcpy.Statistics_analysis(landuse_int, os.path.join(scratch, 'areaTbl'), [['propArea', 'SUM']], ['ReachID', 'LUI_CLASS'])
            areaPivTbl = arcpy.PivotTable_management(areaTbl, ['ReachID'], 'LUI_CLASS', 'SUM_propArea', os.path.join(scratch, 'areaPivTbl'))

            # create empty dictionary to hold input table field values
            tblDict = {}
            # add values to dictionary
            with arcpy.da.SearchCursor(areaPivTbl, ['ReachID', 'VeryLow', 'Low', 'Moderate', 'High']) as cursor:
                for row in cursor:
                    tblDict[row[0]] = [row[1], row[2], row[3], row[4]]
            # populate flowline network out fields
            arcpy.AddField_management(out_network, "iPC_VLowLU", 'DOUBLE')
            arcpy.AddField_management(out_network, "iPC_LowLU", 'DOUBLE')
            arcpy.AddField_management(out_network, "iPC_ModLU", 'DOUBLE')
            arcpy.AddField_management(out_network, "iPC_HighLU", 'DOUBLE')

            with arcpy.da.UpdateCursor(out_network, ['ReachID', 'iPC_VLowLU', 'iPC_LowLU', 'iPC_ModLU', 'iPC_HighLU']) as cursor:
                for row in cursor:
                    try:
                        aKey = row[0]
                        row[1] = round(100*tblDict[aKey][0], 2)
                        row[2] = round(100*tblDict[aKey][1], 2)
                        row[3] = round(100*tblDict[aKey][2], 2)
                        row[4] = round(100*tblDict[aKey][3], 2)
                        cursor.updateRow(row)
                    except:
                        pass
            tblDict.clear()

        # delete temp fcs, tbls, etc.
        items = [lu_ras]
        for item in items:
            arcpy.Delete_management(item)

    # clear the environment extent setting
    arcpy.ClearEnvironment("extent")


# calculate drainage area function
def calc_drain_area(DEM, inputDEM):

    #  define raster environment settings
    desc = arcpy.Describe(DEM)
    arcpy.env.extent = desc.Extent
    arcpy.env.outputCoordinateSystem = desc.SpatialReference
    arcpy.env.cellSize = desc.meanCellWidth

    #  calculate cell area for use in drainage area calcultion
    height = desc.meanCellHeight
    width = desc.meanCellWidth
    cellArea = height * width

    # derive drainage area raster (in square km) from input DEM
    # note: draiange area calculation assumes input dem is in meters
    filled_DEM = Fill(DEM) # fill sinks in dem
    flow_direction = FlowDirection(filled_DEM) # calculate flow direction
    flow_accumulation = FlowAccumulation(flow_direction) # calculate flow accumulattion
    DrainArea = flow_accumulation * cellArea / 1000000 # calculate drainage area in square kilometers

    # save drainage area raster
    if os.path.exists(os.path.dirname(inputDEM) + "/Flow/DrainArea_sqkm.tif"):
        arcpy.Delete_management(os.path.dirname(inputDEM) + "/Flow/DrainArea_sqkm.tif")
        arcpy.CopyRaster_management(DrainArea, os.path.dirname(inputDEM) + "/Flow/DrainArea_sqkm.tif")
    else:
        os.mkdir(os.path.dirname(inputDEM) + "/Flow")
        arcpy.CopyRaster_management(DrainArea, os.path.dirname(inputDEM) + "/Flow/DrainArea_sqkm.tif")


# write xml function
def writexml(projPath, projName, hucID, hucName, coded_veg, coded_hist, seg_network, inDEM, valley_bottom, landuse,
             FlowAcc, DrAr, road, railroad, canal, buf_30m, buf_100m, out_network):
    """write the xml file for the project"""
    if not os.path.exists(projPath + "/project.rs.xml"):

        # xml file
        xmlfile = projPath + "/project.rs.xml"

        # initiate xml file creation
        newxml = projectxml.ProjectXML(xmlfile, "BRAT", projName)

        # add metadata
        if hucID is not None:
            newxml.addMeta("HUCID", hucID, newxml.project)
        if hucID is not None:
            idlist = [int(x) for x in str(hucID)]
            if idlist[0] == 1 and idlist[1] == 7:
                newxml.addMeta("Region", "CRB", newxml.project)
        if hucName is not None:
            newxml.addMeta("Watershed", hucName, newxml.project)

        # add first realization
        newxml.addBRATRealization("BRAT Realization 1", rid="RZ1", dateCreated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  productVersion="3.0.3", guid=getUUID())

        # add inputs
        newxml.addProjectInput("Raster", "Existing Vegetation", coded_veg[coded_veg.find("01_Inputs"):], iid="EXVEG1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Existing Vegetation", ref="EXVEG1")
        newxml.addProjectInput("Raster", "Historic Vegetation", coded_hist[coded_hist.find("01_Inputs"):], iid="HISTVEG1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Historic Vegetation", ref="HISTVEG1")
        newxml.addProjectInput("Vector", "Segmented Network", seg_network[seg_network.find("01_Inputs"):], iid="NETWORK1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Network", ref="NETWORK1")
        newxml.addProjectInput("DEM", "DEM", inDEM[inDEM.find("01_Inputs"):], iid="DEM1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "DEM", ref="DEM1")

        # add optional inputs
        if FlowAcc is None:
            newxml.addBRATInput(newxml.BRATRealizations[0], "Flow", name="Drainage Area", path=DrAr[DrAr.find("01_Inputs"):], guid=getUUID())
        else:
            newxml.addProjectInput("Raster", "Drainage Area", DrAr[DrAr.find("01_Inputs"):], iid="DA1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Flow", ref="DA1")
        if landuse is not None:
            newxml.addProjectInput("Raster", "Land Use", landuse[landuse.find("01_Inputs"):], iid="LU1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Land Use", ref="LU1")
        if valley_bottom is not None:
            newxml.addProjectInput("Vector", "Valley Bottom", valley_bottom[valley_bottom.find("01_Inputs"):], iid="VALLEY1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Valley", ref="VALLEY1")
        if road is not None:
            newxml.addProjectInput("Vector", "Roads", road[road.find("01_Inputs"):], iid="ROAD1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Roads", ref="ROAD1")
        if railroad is not None:
            newxml.addProjectInput("Vector", "Railroads", railroad[railroad.find("01_Inputs"):], iid="RR1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Railroads", ref="RR1")
        if canal is not None:
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
            if os.path.abspath(dempath[i]) == os.path.abspath(inDEM[inDEM.find("01_Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "DEM", ref=str(demid[i]))

        nlist = []
        for j in dempath:
            if os.path.abspath(inDEM[inDEM.find("01_Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("DEM", "DEM", inDEM[inDEM.find("01_Inputs"):], iid="DEM" + str(k), guid=getUUID())
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

        if FlowAcc is not None:
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

        if FlowAcc is None:
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
                    if flows[i].find("Path") and flows[i].find("Path").text:
                        flowpath[i] = flows[i].find("Path").text
                        if os.path.abspath(flowpath[i]) == os.path.abspath(DrAr[DrAr.find("01_Inputs"):]):
                            flowguid = flows[i].attrib['guid']
                            exxml.addBRATInput(exxml.BRATRealizations[0], "Flow", "Drainage Area", path=DrAr[DrAr.find("01_Inputs"):], guid=flowguid)


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
            if road is not None:
                if os.path.abspath(vectorpath[i]) == os.path.abspath(road[road.find("01_Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Roads", ref=str(vectorid[i]))
            if railroad is not None:
                if os.path.abspath(vectorpath[i]) == os.path.abspath(railroad[railroad.find("01_Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Railroads", ref=str(vectorid[i]))
            if canal is not None:
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

        if road is not None:
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

        if railroad is not None:
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

        if canal is not None:
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


def addMainstemAttribute(out_network):
    """
    Adds the mainstem attribute to our output network
    :param out_network: The network that we want to work with
    :return: None
    """
    listFields = arcpy.ListFields(out_network,"IsMainstem")
    if len(listFields) is not 1:
        arcpy.AddField_management(out_network, "IsMainstem", "SHORT", "", "", "", "", "NULLABLE")
    arcpy.CalculateField_management(out_network,"IsMainstem",1,"PYTHON")


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