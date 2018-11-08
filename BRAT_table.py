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
from rasterstats import zonal_stats
import uuid
import FindBraidedNetwork
import BRAT_Braid_Handler
from SupportingFunctions import make_layer, make_folder

reload(FindBraidedNetwork)
reload(BRAT_Braid_Handler)


def main(
    proj_path,
    proj_name,
    huc_ID,
    huc_name,
    seg_network,
    in_DEM,
    flow_acc,
    coded_veg,
    coded_hist,
    valley_bottom,
    road,
    railroad,
    canal,
    landuse,
    out_name,
    find_clusters,
    should_segment_network,
    is_verbose):
    find_clusters = parse_input_bool(find_clusters)
    should_segment_network = parse_input_bool(should_segment_network)
    is_verbose = parse_input_bool(is_verbose)

    scratch = 'in_memory'
    #arcpy.env.workspace = scratch
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    # --check input projections--
    validate_inputs(seg_network, road, railroad, canal, is_verbose)

    # name and create output folder
    new_output_folder, intermediate_folder, seg_network_copy = build_output_folder(proj_path, out_name, seg_network, road,
                                                                                  should_segment_network, is_verbose)

    # --check input network fields--
    # add flowline reach id field ('ReachID') if it doens't already exist
    # this field allows for more for more 'stable' joining
    fields = [f.name for f in arcpy.ListFields(seg_network_copy)]
    if 'ReachID' not in fields:
        arcpy.AddField_management(seg_network_copy, 'ReachID', 'LONG')
        with arcpy.da.UpdateCursor(seg_network_copy, ['FID', 'ReachID']) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

    # --create network buffers for analyses--
    # create 'Buffers' folder if it doesn't exist
    buffers_folder = make_folder(intermediate_folder, "01_Buffers")

    # create network segment midpoints
    if is_verbose:
        arcpy.AddMessage("Finding network segment midpoints...")
    midpoints = arcpy.FeatureVerticesToPoints_management(seg_network_copy, scratch + "/midpoints", "MID")
    # remove unwanted fields from midpoints
    fields = arcpy.ListFields(midpoints)
    keep = ['ReachID']
    drop = []
    for field in fields:
        if not field.required and field.name not in keep and field.type != 'Geometry':
            drop.append(field.name)
    if len(drop) > 0:
        arcpy.DeleteField_management(midpoints, drop)

    if is_verbose:
        arcpy.AddMessage("Making buffers...")
    # create midpoint 100 m buffer
    midpoint_buffer = os.path.join(buffers_folder, "midpoint_buffer_100m.shp")
    arcpy.Buffer_analysis(midpoints, midpoint_buffer, "100 Meters")
    # create network 30 m buffer
    buf_30m = os.path.join(buffers_folder, "buffer_30m.shp")
    arcpy.Buffer_analysis(seg_network_copy, buf_30m, "30 Meters", "", "ROUND")
    # create network 100 m buffer
    buf_100m = os.path.join(buffers_folder, "buffer_100m.shp")
    arcpy.Buffer_analysis(seg_network_copy, buf_100m, "100 Meters", "", "ROUND")

    # run geo attributes function
    arcpy.AddMessage('Adding "iGeo" attributes to network...')
    igeo_attributes(seg_network_copy, in_DEM, flow_acc, midpoint_buffer, scratch, is_verbose, proj_path)

    # run vegetation attributes function
    arcpy.AddMessage('Adding "iVeg" attributes to network...')
    iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, seg_network_copy, is_verbose, proj_path)

    # run ipc attributes function if conflict layers are defined by user
    if road is not None and valley_bottom is not None:
        arcpy.AddMessage('Adding "iPC" attributes to network...')
        ipc_attributes(seg_network_copy, road, railroad, canal, valley_bottom, buf_30m, buf_100m, landuse, scratch, proj_path, is_verbose)

    handle_braids(seg_network_copy, canal, proj_path, find_clusters, is_verbose)

    # run write xml function
    arcpy.AddMessage('Writing project xml...')
    if flow_acc is None:
        DrAr = os.path.dirname(in_DEM) + "/Flow/DrainArea_sqkm.tif"
    else:
        DrAr = os.path.dirname(in_DEM) + "/Flow/" + os.path.basename(flow_acc)

    trib_code_folder = os.path.dirname(os.path.abspath(__file__))
    symbology_folder = os.path.join(trib_code_folder, 'BRATSymbology')
    flow_accumulation_sym_layer = os.path.join(symbology_folder, "Flow_Accumulation.lyr")
    make_layer(os.path.dirname(DrAr), DrAr, "Flow Accumulation", symbology_layer=flow_accumulation_sym_layer, is_raster=True)

    make_layers(seg_network_copy)
    try:
        write_xml(proj_path, proj_name, huc_ID, huc_name, coded_veg, coded_hist, seg_network, in_DEM, valley_bottom, landuse,
                  flow_acc, DrAr, road, railroad, canal, buf_30m, buf_100m, seg_network_copy, new_output_folder)
    except IndexError:
        pass

    run_tests(seg_network_copy, is_verbose)

    arcpy.CheckInExtension("spatial")


def build_output_folder(proj_path, out_name, seg_network, road, should_segment_network, is_verbose):
    if is_verbose:
        arcpy.AddMessage("Building folder structure...")
    j = 1
    new_output_folder = os.path.join(proj_path, "Output_" + str(j))
    while os.path.exists(new_output_folder):
        j += 1
        new_output_folder = os.path.join(proj_path, "Output_" + str(j))
    os.mkdir(new_output_folder)

    intermediate_folder = make_folder(new_output_folder, "01_Intermediates")

    # copy input segment network to output folder
    if out_name.endswith('.shp'):
        seg_network_copy = os.path.join(intermediate_folder, out_name)
    else:
        seg_network_copy = os.path.join(intermediate_folder, out_name + ".shp")

    if should_segment_network:
        segment_by_roads(seg_network, seg_network_copy, road, is_verbose)
    else:
        arcpy.CopyFeatures_management(seg_network, seg_network_copy)

    return new_output_folder, intermediate_folder, seg_network_copy



def segment_by_roads(seg_network, seg_network_copy, roads, is_verbose):
    """
    Segments the seg_network by roads, and puts segmented network at seg_network_copy
    :param seg_network: Path to the seg_network that we want to segment further
    :param seg_network_copy: Path to where we want the new network to go
    :param roads: The shape file we use to segment
    :return:
    """
    arcpy.AddMessage("Segmenting network by roads...")

    temp_network = os.path.join(os.path.dirname(seg_network_copy), "temp.shp")
    temp_layer = "temp_lyr"
    temp_seg_network_layer = "seg_network_lyr"

    arcpy.FeatureToLine_management([seg_network, roads], temp_network)

    arcpy.MakeFeatureLayer_management(temp_network, temp_layer)
    arcpy.MakeFeatureLayer_management(seg_network, temp_seg_network_layer)

    arcpy.SelectLayerByLocation_management(temp_layer, "WITHIN", temp_seg_network_layer)
    arcpy.CopyFeatures_management(temp_layer, seg_network_copy)

    delete_with_arcpy([temp_layer, temp_seg_network_layer, temp_network])
    add_reach_dist(seg_network, seg_network_copy, is_verbose)


def add_reach_dist(seg_network, seg_network_copy, is_verbose):
    if is_verbose:
        arcpy.AddMessage("Calculating ReachDist...")

    fields = [f.name for f in arcpy.ListFields(seg_network_copy)]
    if 'ReachID' in fields:
        with arcpy.da.UpdateCursor(seg_network_copy, ['FID', 'ReachID']) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

    # get distance along route (LineID) for segment midpoints
    midpoints = arcpy.FeatureVerticesToPoints_management(seg_network_copy, 'in_memory/midpoints', "MID")

    seg_network_dissolve = arcpy.Dissolve_management(seg_network, 'in_memory/seg_network_dissolve', 'StreamID', '',
                                                     'SINGLE_PART', 'UNSPLIT_LINES')

    arcpy.AddField_management(seg_network_dissolve, 'From_', 'DOUBLE')
    arcpy.AddField_management(seg_network_dissolve, 'To_', 'DOUBLE')
    with arcpy.da.UpdateCursor(seg_network_dissolve, ['SHAPE@Length', 'From_', 'To_']) as cursor:
        for row in cursor:
            row[1] = 0.0
            row[2] = row[0]
            cursor.updateRow(row)

    arcpy.CreateRoutes_lr(seg_network_dissolve, 'StreamID', 'in_memory/flowline_route', 'TWO_FIELDS', 'From_', 'To_')
    route_tbl = arcpy.LocateFeaturesAlongRoutes_lr(midpoints, 'in_memory/flowline_route', 'StreamID',
                                                  1.0,
                                                  os.path.join(os.path.dirname(seg_network_copy), 'tbl_Routes.dbf'),
                                                  'RID POINT MEAS')

    dist_dict = {}
    # add reach id distance values to dictionary
    with arcpy.da.SearchCursor(route_tbl, ['ReachID', 'MEAS']) as cursor:
        for row in cursor:
            dist_dict[row[0]] = row[1]

    # populate dictionary value to output field by ReachID
    arcpy.AddField_management(seg_network_copy, 'ReachDist', 'DOUBLE')
    with arcpy.da.UpdateCursor(seg_network_copy, ['ReachID', 'ReachDist']) as cursor:
        for row in cursor:
            aKey = row[0]
            row[1] = dist_dict[aKey]
            cursor.updateRow(row)

    arcpy.Delete_management('in_memory')


# zonal statistics within buffer function
# dictionary join field function
def zonalStatsWithinBuffer(buffer, ras, statType, out_fc, out_FC_field):
    # get input raster stat value within each buffer
    statsShp = zonal_stats(buffer, ras, stats = statType, geojson_out = True)
    # create and populate dictionary of buffer ReachID and stat values
    statDict = {}

    for shp in statsShp:
        key = int(shp['properties']['ReachID'])
        value = shp['properties'][statType]
        statDict[key] = value

    # populate dictionary value to output field by ReachID
    with arcpy.da.UpdateCursor(out_fc, ['ReachID', out_FC_field]) as cursor:
        for row in cursor:
            try:
                aKey = int(row[0])
                row[1] = statDict[aKey]
                cursor.updateRow(row)
            except:
                pass

    statDict.clear()
    del statsShp


# geo attributes function
# calculates min and max elevation, length, slope, and drainage area for each flowline segment
def igeo_attributes(out_network, in_DEM, flow_acc, midpoint_buffer, scratch, is_verbose, projPath):

    from shutil import rmtree
    tempDir = os.path.join(projPath, 'Temp')
    if os.path.exists(tempDir):
        rmtree(tempDir)
    os.mkdir(tempDir)

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
    if is_verbose:
        arcpy.AddMessage("Preprocessing DEM...")
    #  --smooth input dem by 3x3 cell window--
    #  define raster environment settings
    desc = arcpy.Describe(in_DEM)
    arcpy.env.extent = desc.Extent
    arcpy.env.outputCoordinateSystem = desc.SpatialReference
    arcpy.env.cellSize = desc.meanCellWidth
    # calculate mean z over 3x3 cell window
    neighborhood = NbrRectangle(3, 3, "CELL")
    tmp_dem = FocalStatistics(in_DEM, neighborhood, 'MEAN')
    # clip smoothed dem to input dem
    clipDEM = ExtractByMask(tmp_dem, in_DEM)
    DEM = os.path.join(tempDir, 'smDEM.tif')
    arcpy.CopyRaster_management(clipDEM, DEM)

    # function to attribute start/end elevation (dem z) to each flowline segment
    def zSeg(vertex_type, out_field):
        if is_verbose:
            arcpy.AddMessage("Calculating values for " + out_field + "...")
        # create start/end points for each flowline reach segment
        tmp_pts = os.path.join(scratch, 'tmp_pts')
        arcpy.FeatureVerticesToPoints_management(out_network, tmp_pts, vertex_type)
        # create 30 meter buffer around each start/end point
        #tmp_buff = os.path.join(scratch, 'tmp_buff')
        tmp_buff = os.path.join(projPath, 'tmp_buff.shp')
        arcpy.Buffer_analysis(tmp_pts, tmp_buff, '30 Meters')
        # get min dem z value within each buffer
        arcpy.AddField_management(out_network, out_field, "DOUBLE")
        zonalStatsWithinBuffer(tmp_buff, DEM, "min", out_network, out_field)

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
        if is_verbose:
            arcpy.AddMessage("Calculating iGeo_Slope...")
        for row in cursor:
            row[3] = (abs(row[0] - row[1]))/row[2]
            if row[3] == 0.0:
                row[3] = 0.0001
            cursor.updateRow(row)

    # get DA values
    if flow_acc is None:
        arcpy.AddMessage("Calculating drainage area...")
        calc_drain_area(DEM, in_DEM)
    elif not os.path.exists(os.path.dirname(in_DEM) + "/Flow"): # if there's no folder for the flow accumulation, make one
        os.mkdir(os.path.dirname(in_DEM) + "/Flow")
        if is_verbose:
            arcpy.AddMessage("Copying drainage area raster...")
        arcpy.CopyRaster_management(flow_acc, os.path.dirname(in_DEM) + "/Flow/" + os.path.basename(flow_acc))

    if flow_acc is None:
        DrArea = os.path.dirname(in_DEM) + "/Flow/DrainArea_sqkm.tif"
    else:
        DrArea = os.path.dirname(in_DEM) + "/Flow/" + os.path.basename(flow_acc)
    # Todo: check this bc it seems wrong to pull from midpoint buffer

    # add drainage area 'iGeo_DA' field to flowline network
    arcpy.AddField_management(out_network, "iGeo_DA", "DOUBLE")
    # get max drainage area within 100 m midpoint buffer
    if is_verbose:
        arcpy.AddMessage("Calculating iGeo_DA...")
    zonalStatsWithinBuffer(midpoint_buffer, DrArea, "max", out_network, "iGeo_DA")

    # replace '0' drainage area values with tiny value
    with arcpy.da.UpdateCursor(out_network, ["iGeo_DA"]) as cursor:
        for row in cursor:
            if row[0] == 0:
                row[0] = 0.00000001
            cursor.updateRow(row)


# vegetation attributes function
# calculates both existing and potential mean vegetation value within 30 m and 100 m buffer of each stream segment
def iveg_attributes(coded_veg, coded_hist, buf_100m, buf_30m, out_network, is_verbose, projPath):

    from shutil import rmtree
    tempDir = os.path.join(projPath, 'Temp')
    if os.path.exists(tempDir):
        rmtree(tempDir)
    os.mkdir(tempDir)

    # if fields already exist, delete them
    fields = [f.name for f in arcpy.ListFields(out_network)]
    drop = ["iVeg_100EX", "iVeg_30EX", "iVeg_100PT", "iVeg_30PT"]
    for field in fields:
        if field in drop:
            arcpy.DeleteField_management(out_network, field)

    # --existing vegetation values--
    if is_verbose:
        arcpy.AddMessage("Creating current veg lookup raster...")
    veg_lookup = os.path.join(projPath, 'veg_lookup.tif')
    tmp_veg_lookup = Lookup(coded_veg, "VEG_CODE")
    arcpy.CopyRaster_management(tmp_veg_lookup, veg_lookup)
    # add mean veg value 'iVeg_100EX' field to flowline network
    arcpy.AddField_management(out_network, "iVeg_100EX", "DOUBLE")
    # get mean existing veg value within 100 m buffer
    if is_verbose:
        arcpy.AddMessage("Calculating iVeg_100EX...")
    zonalStatsWithinBuffer(buf_100m, veg_lookup, "mean", out_network, "iVeg_100EX")

    # add mean veg value 'iVeg_VT30EX' field to flowline network
    arcpy.AddField_management(out_network, "iVeg_30EX", "DOUBLE")
    # get mean existing veg value within 30 m buffer
    if is_verbose:
        arcpy.AddMessage("Calculating iVeg_30EX...")
    zonalStatsWithinBuffer(buf_30m, veg_lookup, "mean", out_network, "iVeg_30EX")

    # delete temp fcs, tbls, etc.
    items = [veg_lookup]
    for item in items:
        arcpy.Delete_management(item)

    # --historic (i.e., potential) vegetation values--
    if is_verbose:
        arcpy.AddMessage("Creating historic veg lookup raster...")
    hist_veg_lookup = os.path.join(projPath, 'hist_veg_lookup.tif')
    arcpy.CopyRaster_management(Lookup(coded_hist, "VEG_CODE"), hist_veg_lookup)

    # add mean veg value 'iVeg_100PT' field to flowline network
    arcpy.AddField_management(out_network, "iVeg_100PT", "DOUBLE")
    # get mean potential veg value within 100 m buffer
    if is_verbose:
        arcpy.AddMessage("Calculating iVeg_100PT...")
    zonalStatsWithinBuffer(buf_100m, hist_veg_lookup, "mean", out_network, "iVeg_100PT")

    # add mean veg value 'iVeg_30PT' field to flowline network
    arcpy.AddField_management(out_network, "iVeg_30PT", "DOUBLE")
    # get mean potential veg value within 30 m buffer
    if is_verbose:
        arcpy.AddMessage("Calculating iVeg_30PT...")
    zonalStatsWithinBuffer(buf_30m, hist_veg_lookup, "mean", out_network, "iVeg_30PT")

    # delete temp fcs, tbls, etc.
    items = [hist_veg_lookup]
    for item in items:
        arcpy.Delete_management(item)


# conflict potential function
# calculates distances from road intersections, adjacent roads, railroads and canals for each flowline segment
def ipc_attributes(out_network, road, railroad, canal, valley_bottom, buf_30m, buf_100m, landuse, scratch, projPath, is_verbose):
    # create temp directory
    if is_verbose:
        arcpy.AddMessage("Deleting and remaking temp dir...")
    from shutil import rmtree
    temp_dir = os.path.join(projPath, 'Temp')
    if os.path.exists(temp_dir):
        rmtree(temp_dir)
    os.mkdir(temp_dir)

    # if fields already exist, delete them
    fields = [f.name for f in arcpy.ListFields(out_network)]
    drop = ["iPC_RoadX", "iPC_Road", "iPC_RoadVB", "iPC_Rail", "iPC_RailVB", "iPC_Canal", "iPC_LU"]
    for field in fields:
        if field in drop:
            arcpy.DeleteField_management(out_network, field)

    # calculate mean distance from road-stream crossings ('iPC_RoadX'), roads ('iPC_Road') and roads clipped to the valley bottom ('iPC_RoadVB')
    if road is not None:
        roadx = temp_dir + "\\roadx.shp"
        # create points at road-stream intersections
        arcpy.Intersect_analysis([out_network, road], roadx, "", "", "POINT")
        find_distance_from_feature(out_network, roadx, valley_bottom, temp_dir, buf_30m, "roadx", "iPC_RoadX", scratch, is_verbose, clip_feature = False)

    # calculate mean distance from road-stream crossings ('iPC_RoadX'), roads ('iPC_Road') and roads clipped to the valley bottom ('iPC_RoadVB')
    if road is not None:
        find_distance_from_feature(out_network, road, valley_bottom, temp_dir, buf_30m, "roadvb", "iPC_RoadVB", scratch, is_verbose, clip_feature = True)
        find_distance_from_feature(out_network, road, valley_bottom, temp_dir, buf_30m, "road", "iPC_Road", scratch, is_verbose, clip_feature = False)

    # calculate mean distance from railroads ('iPC_Rail') and railroads clipped to valley bottom ('iPC_RailVB')
    if railroad is not None:
        find_distance_from_feature(out_network, railroad, valley_bottom, temp_dir, buf_30m, "railroadvb", "iPC_RailVB", scratch, is_verbose, clip_feature = True)
        find_distance_from_feature(out_network, railroad, valley_bottom, temp_dir, buf_30m, "railroad", "iPC_Rail", scratch, is_verbose, clip_feature = False)

    # calculate minimum distance from canals ('iPC_Canal')
    if canal is not None:
        find_distance_from_feature(out_network, canal, valley_bottom, temp_dir, buf_30m, "canal", "iPC_Canal", scratch, is_verbose, clip_feature=False)

    # calculate mean landuse value ('iPC_LU')
    if landuse is not None:
        if is_verbose:
            arcpy.AddMessage("Calculating iPC_LU values...")
        arcpy.AddField_management(out_network, "iPC_LU", "DOUBLE")
        # create raster with just landuse code values
        lu_ras = os.path.join(temp_dir, 'lu_lookup.tif')
        tmp_lu_ras = Lookup(landuse, "LU_CODE")
        arcpy.CopyRaster_management(tmp_lu_ras, lu_ras)
        # calculate mean landuse value within 100 m buffer of each network segment
        zonalStatsWithinBuffer(buf_100m, lu_ras, "mean", out_network, "iPC_LU")
        # get percentage of each land use class in 100 m buffer of stream segment
        fields = [f.name.upper() for f in arcpy.ListFields(landuse)]

        if "LUI_CLASS" in fields:
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
            area_tbl = arcpy.Statistics_analysis(landuse_int, os.path.join(scratch, 'areaTbl'), [['propArea', 'SUM']], ['ReachID', 'LUI_CLASS'])
            area_piv_tbl = arcpy.PivotTable_management(area_tbl, ['ReachID'], 'LUI_CLASS', 'SUM_propArea', os.path.join(scratch, 'areaPivTbl'))

            sanitize_area_piv_tbl(area_piv_tbl)
            # create empty dictionary to hold input table field values
            tbl_dict = {}
            # add values to dictionary
            with arcpy.da.SearchCursor(area_piv_tbl, ['ReachID', 'VeryLow', 'Low', 'Moderate', 'High']) as cursor:
                for row in cursor:
                    tbl_dict[row[0]] = [row[1], row[2], row[3], row[4]]

            # populate flowline network out fields
            arcpy.AddField_management(out_network, "iPC_VLowLU", 'DOUBLE')
            arcpy.AddField_management(out_network, "iPC_LowLU", 'DOUBLE')
            arcpy.AddField_management(out_network, "iPC_ModLU", 'DOUBLE')
            arcpy.AddField_management(out_network, "iPC_HighLU", 'DOUBLE')

            with arcpy.da.UpdateCursor(out_network, ['ReachID', 'iPC_VLowLU', 'iPC_LowLU', 'iPC_ModLU', 'iPC_HighLU']) as cursor:
                for row in cursor:
                    try:
                        aKey = row[0]
                        row[1] = round(100*tbl_dict[aKey][0], 2)
                        row[2] = round(100*tbl_dict[aKey][1], 2)
                        row[3] = round(100*tbl_dict[aKey][2], 2)
                        row[4] = round(100*tbl_dict[aKey][3], 2)
                        cursor.updateRow(row)
                    except:
                        pass
            tbl_dict.clear()
        else:
            arcpy.AddWarning("No field named \"LU_CLASS\" in the land use raster. Make sure that this field exists" +
                             " with no typos if you wish to use the data from the land use raster")

        # delete temp fcs, tbls, etc.
        items = [lu_ras]
        for item in items:
            arcpy.Delete_management(item)

    # calculate min distance of all 'iPC' distance fields
    arcpy.AddField_management(out_network, "oPC_Dist", 'DOUBLE')
    fields = [f.name for f in arcpy.ListFields(out_network)]
    all_dist_fields = ["oPC_Dist", "iPC_RoadX", "iPC_Road", "iPC_RoadVB", "iPC_Rail", "iPC_RailVB", "iPC_Canal"]
    dist_fields = []
    for field in all_dist_fields:
        if field in fields:
            dist_fields.append(field)
    with arcpy.da.UpdateCursor(out_network, dist_fields) as cursor:
        for row in cursor:
            row[0] = min(row[1:])
            cursor.updateRow(row)

    # clear the environment extent setting
    arcpy.ClearEnvironment("extent")


def sanitize_area_piv_tbl(area_piv_tbl):
    """
    Makes sure that the areaPivTbl has all the fields we need. If it doesn't, we'll add it.
    :param area_piv_tbl:
    :return:
    """
    fields = [f.name for f in arcpy.ListFields(area_piv_tbl)]
    check_and_add_zero_fields(area_piv_tbl, fields, 'VeryLow')
    check_and_add_zero_fields(area_piv_tbl, fields, 'Low')
    check_and_add_zero_fields(area_piv_tbl, fields, 'Moderate')
    check_and_add_zero_fields(area_piv_tbl, fields, 'High')


def check_and_add_zero_fields(table, fields, field_name):
    """
    Checks that a field is in the table. If it isn't, we add it and populate it with zeros
    :param table: The table that we want to check
    :param fields: All the fields in the table (more efficient if doing multiple checks)
    :param field_name: The name of the field we want to check for
    :return:
    """
    if field_name not in fields:
        arcpy.AddField_management(table, field_name, "DOUBLE")
        arcpy.CalculateField_management(table, field_name, 0, "PYTHON")


def find_distance_from_feature(out_network, feature, valley_bottom, temp_dir, buf, temp_name, new_field_name, scratch, is_verbose, clip_feature = False):
    if is_verbose:
        arcpy.AddMessage("Calculating " + new_field_name + " values...")
    arcpy.AddField_management(out_network, new_field_name, "DOUBLE")

    if clip_feature == True:
        # clip input feature to the valley bottom
        feature_subset = arcpy.Clip_analysis(feature, valley_bottom, os.path.join(temp_dir, temp_name + '_subset.shp'))
        # convert feature for count purposes
        feature_mts = arcpy.MultipartToSinglepart_management(feature_subset, os.path.join(temp_dir, temp_name + "_mts.shp"))
    else:
        feature_mts = arcpy.MultipartToSinglepart_management(feature, os.path.join(temp_dir, temp_name + "_mts.shp"))
        feature_subset = feature

    count = arcpy.GetCount_management(feature_mts)
    ct = int(count.getOutput(0))
    # if there are features, then set the distance from to high value (10000 m)
    if ct < 1:
        with arcpy.da.UpdateCursor(out_network, new_field_name) as cursor:
            for row in cursor:
                row[0] = 10000.0
                cursor.updateRow(row)
    # if there are features, calculate distance
    else:
        # set extent to the stream network
        arcpy.env.extent = out_network
        # calculate euclidean distance from input features
        ed_feature = os.path.join(temp_dir, temp_name + "_dist.tif")
        tmp_ed_feature = EucDistance(feature_subset, cell_size = 5) # cell size of 5 m
        arcpy.CopyRaster_management(tmp_ed_feature, ed_feature)
        # get min distance from feature in the within 30 m buffer of each network segment
        if new_field_name == 'iPC_RoadX':
            zonalStatsWithinBuffer(buf, ed_feature, "min", out_network, new_field_name)
        else:
            zonalStatsWithinBuffer(buf, ed_feature, "mean", out_network, new_field_name)

        # delete temp fcs, tbls, etc.
        items = []
        for item in items:
            arcpy.Delete_management(item)

# calculate drainage area function
def calc_drain_area(DEM, input_DEM):

    #  define raster environment settings
    desc = arcpy.Describe(DEM)
    arcpy.env.extent = desc.Extent
    arcpy.env.outputCoordinateSystem = desc.SpatialReference
    arcpy.env.cellSize = desc.meanCellWidth

    #  calculate cell area for use in drainage area calcultion
    height = desc.meanCellHeight
    width = desc.meanCellWidth
    cell_area = height * width

    # derive drainage area raster (in square km) from input DEM
    # note: draiange area calculation assumes input dem is in meters
    filled_DEM = Fill(DEM) # fill sinks in dem
    flow_direction = FlowDirection(filled_DEM) # calculate flow direction
    flow_accumulation = FlowAccumulation(flow_direction) # calculate flow accumulattion
    drain_area = flow_accumulation * cell_area / 1000000 # calculate drainage area in square kilometers

    # save drainage area raster
    if os.path.exists(os.path.dirname(input_DEM) + "/Flow/DrainArea_sqkm.tif"):
        arcpy.Delete_management(os.path.dirname(input_DEM) + "/Flow/DrainArea_sqkm.tif")
        arcpy.CopyRaster_management(drain_area, os.path.dirname(input_DEM) + "/Flow/DrainArea_sqkm.tif")
    else:
        os.mkdir(os.path.dirname(input_DEM) + "/Flow")
        arcpy.CopyRaster_management(drain_area, os.path.dirname(input_DEM) + "/Flow/DrainArea_sqkm.tif")



# write xml function
def write_xml(projPath, projName, hucID, hucName, coded_veg, coded_hist, seg_network, inDEM, valley_bottom, landuse,
              FlowAcc, DrAr, road, railroad, canal, buf_30m, buf_100m, out_network, output_folder):
    """write the xml file for the project"""
    output_folder_name = os.path.basename(output_folder)
    intermediates_folder_name = os.path.join(output_folder_name, "01_Intermediates")
    inputs_folder = "Inputs"
    xmlfile = projPath + "/project.rs.xml"
    if not os.path.exists(xmlfile):
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
                                  productVersion="3.0.17", guid=getUUID())

        # add inputs
        newxml.addProjectInput("Raster", "Existing Vegetation", coded_veg[coded_veg.find(inputs_folder):], iid="EXVEG1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Existing Vegetation", ref="EXVEG1")
        newxml.addProjectInput("Raster", "Historic Vegetation", coded_hist[coded_hist.find(inputs_folder):], iid="HISTVEG1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Historic Vegetation", ref="HISTVEG1")
        newxml.addProjectInput("Vector", "Segmented Network", seg_network[seg_network.find(inputs_folder):], iid="NETWORK1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Network", ref="NETWORK1")
        newxml.addProjectInput("DEM", "DEM", inDEM[inDEM.find(inputs_folder):], iid="DEM1", guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "DEM", ref="DEM1")

        # add optional inputs
        if FlowAcc is None:
            newxml.addBRATInput(newxml.BRATRealizations[0], "Flow", name="Drainage Area", path=DrAr[DrAr.find(inputs_folder):], guid=getUUID())
        else:
            newxml.addProjectInput("Raster", "Drainage Area", DrAr[DrAr.find(inputs_folder):], iid="DA1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Flow", ref="DA1")
        if landuse is not None:
            newxml.addProjectInput("Raster", "Land Use", landuse[landuse.find(inputs_folder):], iid="LU1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Land Use", ref="LU1")
        if valley_bottom is not None:
            newxml.addProjectInput("Vector", "Valley Bottom", valley_bottom[valley_bottom.find(inputs_folder):], iid="VALLEY1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Valley", ref="VALLEY1")
        if road is not None:
            newxml.addProjectInput("Vector", "Roads", road[road.find(inputs_folder):], iid="ROAD1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Roads", ref="ROAD1")
        if railroad is not None:
            newxml.addProjectInput("Vector", "Railroads", railroad[railroad.find(inputs_folder):], iid="RR1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Railroads", ref="RR1")
        if canal is not None:
            newxml.addProjectInput("Vector", "Canals", canal[canal.find(inputs_folder):], iid="CANAL1", guid=getUUID())
            newxml.addBRATInput(newxml.BRATRealizations[0], "Canals", ref="CANAL1")

        # add derived inputs
        newxml.addBRATInput(newxml.BRATRealizations[0], "Buffer", name="30m Buffer", path=buf_30m[buf_30m.find(intermediates_folder_name):], guid=getUUID())
        newxml.addBRATInput(newxml.BRATRealizations[0], "Buffer", name="100m Buffer", path=buf_100m[buf_100m.find(intermediates_folder_name):], guid=getUUID())

        # add output
        newxml.addOutput("BRAT Analysis", "Vector", "BRAT Input Table", out_network[out_network.find(intermediates_folder_name):], newxml.BRATRealizations[0], guid=getUUID())

        # write xml to this point
        newxml.write()

    else:
        # xml file

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
            if os.path.abspath(dempath[i]) == os.path.abspath(inDEM[inDEM.find("Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "DEM", ref=str(demid[i]))

        nlist = []
        for j in dempath:
            if os.path.abspath(inDEM[inDEM.find("Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("DEM", "DEM", inDEM[inDEM.find("Inputs"):], iid="DEM" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "DEM", ref="DEM" + str(k))

        raster = inputs.findall("Raster")
        rasterid = range(len(raster))
        for i in range(len(raster)):
            rasterid[i] = raster[i].get("id")
        rasterpath = range(len(raster))
        for i in range(len(raster)):
            rasterpath[i] = raster[i].find("Path").text

        for i in range(len(rasterpath)):
            if os.path.abspath(rasterpath[i]) == os.path.abspath(coded_veg[coded_veg.find("Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "Existing Vegetation", ref=str(rasterid[i]))
            elif os.path.abspath(rasterpath[i]) == os.path.abspath(coded_hist[coded_hist.find("Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "Historic Vegetation", ref=str(rasterid[i]))
            elif os.path.abspath(rasterpath[i]) == os.path.abspath(landuse[landuse.find("Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "Land Use", ref=str(rasterid[i]))

        if FlowAcc is not None:
            for i in range(len(rasterpath)):
                if os.path.abspath(rasterpath[i]) == os.path.abspath(DrAr[DrAr.find("Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Flow", ref=str(rasterid[i]))

        nlist = []
        for j in rasterpath:
            if os.path.abspath(coded_veg[coded_veg.find("Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Raster", "Existing Vegetation", coded_veg[coded_veg.find("Inputs"):], iid="EXVEG" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Existing Vegetation", ref="EXVEG" + str(k))
        nlist = []
        for j in rasterpath:
            if os.path.abspath(coded_hist[coded_hist.find("Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Raster", "Historic Vegetation", coded_hist[coded_hist.find("Inputs"):], iid="HISTVEG" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Historic Vegetation", ref="HISTVEG" + str(k))
        nlist = []
        for j in rasterpath:
            if os.path.abspath(landuse[landuse.find("Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Raster", "Land Use", landuse[landuse.find("Inputs"):], iid="LU" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Land Use", ref="LU" + str(k))

        if FlowAcc is None:
            exxml.addBRATInput(exxml.BRATRealizations[0], "Flow", "Drainage Area", DrAr[DrAr.find("Inputs"):],
                               guid=getUUID())
        else:
            nlist = []
            for j in rasterpath:
                if os.path.abspath(DrAr[DrAr.find("Inputs")]) == os.path.abspath(j):
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
                        if os.path.abspath(flowpath[i]) == os.path.abspath(DrAr[DrAr.find("Inputs"):]):
                            flowguid = flows[i].attrib['guid']
                            exxml.addBRATInput(exxml.BRATRealizations[0], "Flow", "Drainage Area", path=DrAr[DrAr.find("Inputs"):], guid=flowguid)


        vector = inputs.findall("Vector")
        vectorid = range(len(vector))
        for i in range(len(vector)):
            vectorid[i] = vector[i].get("id")
        vectorpath = range(len(vector))
        for i in range(len(vector)):
            vectorpath[i] = vector[i].find("Path").text

        for i in range(len(vectorpath)):
            if os.path.abspath(vectorpath[i]) == os.path.abspath(seg_network[seg_network.find("Inputs"):]):
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
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "30m Buffer", path=buf_30m[buf_30m.find(output_folder_name):], guid=buf30_guid)
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "100m Buffer", path=buf_100m[buf_100m.find(output_folder_name):], guid=buf100_guid)
                else:
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "30m Buffer", path=buf_30m[buf_30m.find(output_folder_name):])
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "100m Buffer", path=buf_100m[buf_100m.find(output_folder_name):])
            elif os.path.abspath(vectorpath[i]) == os.path.abspath(valley_bottom[valley_bottom.find("Inputs"):]):
                exxml.addBRATInput(exxml.BRATRealizations[0], "Valley", ref=str(vectorid[i]))
            if road is not None:
                if os.path.abspath(vectorpath[i]) == os.path.abspath(road[road.find("Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Roads", ref=str(vectorid[i]))
            if railroad is not None:
                if os.path.abspath(vectorpath[i]) == os.path.abspath(railroad[railroad.find("Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Railroads", ref=str(vectorid[i]))
            if canal is not None:
                if os.path.abspath(vectorpath[i]) == os.path.abspath(canal[canal.find("Inputs"):]):
                    exxml.addBRATInput(exxml.BRATRealizations[0], "Canals", ref=str(vectorid[i]))

        nlist = []
        for j in vectorpath:
            if os.path.abspath(seg_network[seg_network.find("Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Vector", "Segmented Network", seg_network[seg_network.find("01_Inputs"):], iid="NETWORK" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Network", ref="NETWORK" + str(k))
            exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "30m Buffer",
                               path=os.path.dirname(seg_network[seg_network.find(output_folder_name):]) + "/Buffers/buffer_30m.shp", guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Buffer", "100m Buffer",
                               path=os.path.dirname(seg_network[seg_network.find(output_folder_name):]) + "/Buffers/buffer_100m.shp", guid=getUUID())
        nlist = []
        for j in vectorpath:
            if os.path.abspath(valley_bottom[valley_bottom.find("Inputs"):]) == os.path.abspath(j):
                nlist.append("yes")
            else:
                nlist.append("no")
        if "yes" in nlist:
            pass
        else:
            exxml.addProjectInput("Vector", "Valley Bottom", valley_bottom[valley_bottom.find("Inputs"):], iid="VALLEY" + str(k), guid=getUUID())
            exxml.addBRATInput(exxml.BRATRealizations[0], "Valley", ref="VALLEY" + str(k))

        if road is not None:
            nlist = []
            for j in vectorpath:
                if os.path.abspath(road[road.find("Inputs"):]) == os.path.abspath(j):
                    nlist.append("yes")
                else:
                    nlist.append("no")
            if "yes" in nlist:
                pass
            else:
                exxml.addProjectInput("Vector", "Roads", road[road.find("Inputs"):], iid="ROAD" + str(k), guid=getUUID())
                exxml.addBRATInput(exxml.BRATRealizations[0], "Roads", ref="ROAD" + str(k))

        if railroad is not None:
            nlist = []
            for j in vectorpath:
                if os.path.abspath(railroad[railroad.find("Inputs"):]) == os.path.abspath(j):
                    nlist.append("yes")
                else:
                    nlist.append("no")
            if "yes" in nlist:
                pass
            else:
                pass
                # exxml.addProjectInput("Vector", "Railroads", iid="RR" + str(k), guid=getUUID())
                # exxml.addBRATInput(exxml.BRATRealizations[0], "Railroads", ref="RR" + str(k))

        if canal is not None:
            nlist = []
            for j in vectorpath:
                if os.path.abspath(canal[canal.find("Inputs"):]) == os.path.abspath(j):
                    nlist.append("yes")
                else:
                    nlist.append("no")
            if "yes" in nlist:
                pass
            else:
                exxml.addProjectInput("Vector", "Canals", canal[canal.find("Inputs"):], iid="CANAL" + str(k), guid=getUUID())
                exxml.addBRATInput(exxml.BRATRealizations[0], "Canals", ref="CANAL" + str(k))

        # add output
        exxml.addOutput("BRAT Analysis", "Vector", "BRAT Input Table",
                        out_network[out_network.find(intermediates_folder_name):], exxml.BRATRealizations[0], guid=getUUID())

        # write xml
        exxml.write()


def validate_inputs(seg_network, road, railroad, canal, is_verbose):
    """
    Checks if the spatial references are correct and that the inputs are what we want
    :param seg_network: The stream network shape file
    :param road: The roads shapefile
    :param railroad: The railroads shape file
    :param canal: The canals shapefile
    :param is_verbose: Tells us if we should print out extra debug messages
    :return:
    """
    if is_verbose:
        arcpy.AddMessage("Validating inputs...")
    try:
        network_sr = arcpy.Describe(seg_network).spatialReference
    except:
        raise Exception("There was a problem finding the spatial reference of the stream network. "
                       + "This is commonly caused by trying to run the Table tool directly after running the project "
                       + "builder. Restarting ArcGIS fixes this problem most of the time.")
    if not network_sr.type == "Projected":
        raise Exception("Input stream network must have a projected coordinate system")

    if road is not None:
        if not arcpy.Describe(road).spatialReference.type == "Projected":
            raise Exception("Input roads must have a projected coordinate system")

    if railroad is not None:
        if not arcpy.Describe(railroad).spatialReference.type == "Projected":
            raise Exception("Input railroads must have a projected coordinate system")

    if canal is not None:
        if not arcpy.Describe(canal).spatialReference.type == "Projected":
            raise Exception("Input canals must have projected coordinate system")

    # --check that input network is shapefile--
    if not seg_network.endswith(".shp"):
        raise Exception("Input network must be a shapefile (.shp)")


def add_mainstem_attribute(out_network):
    """
    Adds the mainstem attribute to our output network
    :param out_network: The network that we want to work with
    :return: None
    """
    list_fields = arcpy.ListFields(out_network,"IsMainCh")
    if len(list_fields) is not 1:
        arcpy.AddField_management(out_network, "IsMainCh", "SHORT", "", "", "", "", "NULLABLE")
    arcpy.CalculateField_management(out_network,"IsMainCh",1,"PYTHON")


def make_layers(out_network):
    """
    Writes the layers
    :param out_network: The output network, which we want to make into a layer
    :return:
    """
    arcpy.AddMessage("Making layers...")
    intermediates_folder = os.path.dirname(out_network)
    buffers_folder = os.path.join(intermediates_folder, "01_Buffers")
    topo_folder = make_folder(intermediates_folder, "02_TopographicMetrics")
    anthropogenic_metrics_folder = make_folder(intermediates_folder, "03_AnthropogenicMetrics")


    trib_code_folder = os.path.dirname(os.path.abspath(__file__))
    symbology_folder = os.path.join(trib_code_folder, 'BRATSymbology')

    dist_symbology = os.path.join(symbology_folder, "Distance_To_Infrastructure.lyr")
    land_use_symbology = os.path.join(symbology_folder, "Land_Use_Intensity.lyr")
    slope_symbology = os.path.join(symbology_folder, "Slope_Feature_Class.lyr")
    drain_area_symbology = os.path.join(symbology_folder, "Drainage_Area_Feature_Class.lyr")
    buffer_30m_symbology = os.path.join(symbology_folder, "buffer_30m.lyr")
    buffer_100m_symbology = os.path.join(symbology_folder, "buffer_100m.lyr")

    make_buffer_layers(buffers_folder, buffer_30m_symbology, buffer_100m_symbology)
    make_layer(topo_folder, out_network, "Reach Slope", slope_symbology, is_raster=False)
    make_layer(topo_folder, out_network, "Drainage Area", drain_area_symbology, is_raster=False)

    fields = [f.name for f in arcpy.ListFields(out_network)]
    if 'iPC_LU' in fields:
        make_layer(anthropogenic_metrics_folder, out_network, "Land Use Intensity", land_use_symbology, is_raster=False)
    if 'iPC_RoadX' in fields:
        make_layer(anthropogenic_metrics_folder, out_network, "Distance to Road Crossing", dist_symbology, is_raster=False, symbology_field ='iPC_RoadX')
    if 'iPC_Road' in fields:
        make_layer(anthropogenic_metrics_folder, out_network, "Distance to Road", dist_symbology, is_raster=False, symbology_field ='iPC_Road')
    if 'iPC_RoadVB' in fields:
        make_layer(anthropogenic_metrics_folder, out_network, "Distance to Road in Valley Bottom", dist_symbology, is_raster=False, symbology_field ='iPC_RoadVB')
    if 'iPC_Rail' in fields:
        make_layer(anthropogenic_metrics_folder, out_network, "Distance to Railroad", dist_symbology, is_raster=False, symbology_field ='iPC_Rail')
    if 'iPC_RailVB' in fields:
        make_layer(anthropogenic_metrics_folder, out_network, "Distance to Railroad in Valley Bottom", dist_symbology, is_raster=False, symbology_field ='iPC_RailVB')
    if 'iPC_Canal' in fields:
        make_layer(anthropogenic_metrics_folder, out_network, "Distance to Canal", dist_symbology, is_raster=False, symbology_field ='iPC_Canal')
    if 'oPC_Dist' in fields:
        make_layer(anthropogenic_metrics_folder, out_network, "Distance to Closest Infrastructure", dist_symbology, is_raster=False, symbology_field ='oPC_Dist')


def handle_braids(seg_network_copy, canal, proj_path, find_clusters, is_verbose):
    if is_verbose:
        arcpy.AddMessage("Finding multi-threaded attributes...")
    add_mainstem_attribute(seg_network_copy)
    # find braided reaches

    temp_dir = os.path.join(proj_path, 'Temp')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    FindBraidedNetwork.main(seg_network_copy, canal, temp_dir, is_verbose)

    if find_clusters:
        arcpy.AddMessage("Finding Clusters...")
        clusters = BRAT_Braid_Handler.find_clusters(seg_network_copy)
        BRAT_Braid_Handler.add_cluster_id(seg_network_copy, clusters)


def make_buffer_layers(buffers_folder, buffer_30m_symbology, buffer_100m_symbology):
    """
    Makes a layer for each buffer
    :param buffers_folder: The path to the buffers folder
    :return: Nothing
    """
    for file_name in os.listdir(buffers_folder):
        if file_name.endswith(".shp"):
            file_path = os.path.join(buffers_folder, file_name)
            given_symbology = None
            if "30m" in file_name:
                new_layer_name = "30 m Buffer"
                given_symbology = buffer_30m_symbology
            elif "100m" in file_name:
                new_layer_name = "100 m Buffer"
                given_symbology = buffer_100m_symbology
            make_layer(buffers_folder, file_path, new_layer_name, given_symbology)


def parse_input_bool(given_input):
    if given_input == 'false' or given_input is None:
        return False
    else:
        return True


def delete_with_arcpy(stuffToDelete):
    """
    Deletes everything in a list with arcpy.Delete_management()
    :param stuffToDelete: A list of stuff to delete
    :return:
    """
    for thing in stuffToDelete:
        arcpy.Delete_management(thing)


def run_tests(seg_network_copy, is_verbose):
    """
    Runs tests on the tool's output
    :param seg_network_copy: The network that we want to test
    :return:
    """
    if is_verbose:
        arcpy.AddMessage("Running tests...")
    run_tests = True
    if not run_tests: # don't run tests in execution
        return
    from Tests import test_reach_id_is_unique, report_exceptions, TestException
    test_exceptions = []

    try:
        test_reach_id_is_unique(seg_network_copy)
    except TestException as e:
        test_exceptions.append(str(e))

    report_exceptions(test_exceptions)


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