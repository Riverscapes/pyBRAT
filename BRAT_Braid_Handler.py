# -------------------------------------------------------------------------------
# Name:        BRAT Braid Handler
# Purpose:     Handles the braid clusters in a stream network
#
# Note: This tool is referred to in outputs as "anabranch handler", not "braid handler", for technical reasons. Out of a
# fear of breaking things, this name change generally has not been carried over to the code.
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------


import arcpy
import os
from StreamObjects import Cluster, BraidStream
from SupportingFunctions import make_layer, make_folder, find_available_num_prefix

# Provides a consistent way to refer to clusters, that give more information that a UUID
cluster_id = 0
CLUSTER_FIELD_NAME = "ClusterID"


def main(input_network):
    """
    The main function, where we go through the stream network and handle whatever we need to
    :param input_network: The stream network that we want to give mainstem values
    :return: None
    """
    check_input(input_network)
    if not has_cluster_ids(input_network):
        arcpy.AddMessage("Finding clusters...")
        clusters = find_clusters(input_network)

        handle_clusters(input_network, clusters)
    else:
        arcpy.AddMessage("Finding clusters based on the ClusterID field...")

        # Check to make sure that if 'IsMultiCh' = '0' that 'ClusterID' = '-1'
        # Ensures that stream segments identified as NOT being multi channeled won't
        # be included in DA update
        with arcpy.da.UpdateCursor(input_network, [CLUSTER_FIELD_NAME, 'IsMultiCh', 'IsMainCh']) as cursor:
            for row in cursor:
                if row[1] == 0:  # If the stream is braided. If it isn't, we don't care about its cluster id
                    row[0] = -1
                if row[0] == -1:
                    row[2] = 1
                cursor.updateRow(row)

        clusters = get_clusters_from_ids(input_network)

        for i in range(len(clusters)):
            clusters[i].id = i+1

        update_network_drainage_values(input_network, clusters)

    make_layers(input_network)


def check_input(input_network):
    """
    Checks that the input given has the fields needed for the program
    Primarily updates field names to comply with 3.0.18 name standards. This makes sure that networks produced with old
    pyBRAT can still be given as input
    :param input_network: The network given
    :return: None
    """
    fields = [f.name for f in arcpy.ListFields(input_network)]
    rename_field(input_network, fields, "IsBraided", "IsMultiCh")
    rename_field(input_network, fields, "IsMainstem", "IsMainCh")


def rename_field(input_network, fields, old_name, new_name):
    """
    Checks that the network has the field, and renames an old version if necessary
    :param input_network: The network that hold the field we want to rename
    :param fields: A list of field names
    :param old_name: The name we want to replace
    :param new_name: The name we want to replace the old name with
    :return:
    """
    if new_name not in fields:
        if old_name in fields:
            arcpy.AlterField_management(input_network, old_name, new_field_name=new_name)
        else:
            raise Exception("Field " +
                            new_name +
                            " is a required field in the input network to run the BRAT Braid Handler")


def get_clusters_from_ids(input_network):
    """
    Returns an array of clusters based on the Cluster ID elements that they already have
    :param input_network: The stream network
    :return: List of clusters
    """
    clusters = []
    fields = ['SHAPE@', CLUSTER_FIELD_NAME, "iGeo_DA", 'ReachID', "IsMultiCh"]
    with arcpy.da.SearchCursor(input_network, fields) as cursor:
        for polyline, stream_cluster_id, drainage_area, seg_id, is_braided in cursor:
            if stream_cluster_id != -1 and is_braided == 1:
                new_stream = BraidStream(polyline, seg_id, drainage_area)
                add_stream_to_clusters_with_id(new_stream, stream_cluster_id, clusters)

    return clusters


def add_stream_to_clusters_with_id(new_stream, new_cluster_id, clusters):
    """
    Adds clusters to the stream based on the
    :param new_stream: The stream we want to add
    :param new_cluster_id: The cluster we want to add it to
    :param clusters: The clusters we've already made
    :return: None
    """
    for cluster in clusters:
        if cluster.id == new_cluster_id:
            cluster.add_stream(new_stream)
            # if we found the stream, we end now
            return

    # If the for loop didn't return, add a new cluster with the new stream as the first stream
    new_cluster = Cluster(new_cluster_id)
    new_cluster.add_stream(new_stream)
    clusters.append(new_cluster)


def has_cluster_ids(input_network):
    """
    Tests whether or not a network has the Cluster_ID field, and returns true if it does, false if it doesn't
    :param input_network: The network we want to test
    :return: Bool
    """
    field_names = [field.name for field in arcpy.ListFields(input_network)]
    if CLUSTER_FIELD_NAME in field_names:
        return True
    else:
        return False


def find_clusters(input_network):
    """
    Where we find all the clusters in the stream network
    :param input_network: The stream network whose clusters we want to find
    :return: An array of clusters
    """
    clusters = []
    fields = [f.name for f in arcpy.ListFields(input_network)]
    if "IsPeren" in fields:
        fields = ['SHAPE@', 'ReachID', 'iGeo_DA', 'IsMultiCh', 'IsPeren']
        with arcpy.da.SearchCursor(input_network, fields) as cursor:
            for polyline, stream_id, drainage_area, is_braided, is_peren in cursor:
                if is_braided and is_peren:
                    add_stream_to_clusters(clusters, polyline, stream_id, drainage_area)
    else:
        fields = ['SHAPE@', 'ReachID', 'iGeo_DA', 'IsMultiCh']
        with arcpy.da.SearchCursor(input_network, fields) as cursor:
            for polyline, stream_id, drainage_area, is_braided in cursor:
                if is_braided:
                    add_stream_to_clusters(clusters, polyline, stream_id, drainage_area)

    return clusters


def add_stream_to_clusters(clusters, polyline, stream_id, drainage_area):
    """
    Adds the stream to the list of clusters that we have
    :param clusters: A list of clusters
    :param polyline: The geoprocessing object that contains a bunch of points we need
    :param stream_id: The stream's ID, which we'll use to compare against the original stream when we update it
    :param drainage_area: The stream's drainage area
    :return: None
    """
    new_stream = BraidStream(polyline, stream_id, drainage_area)
    connected_clusters = find_connected_clusters(clusters, new_stream)

    # If there's no connecting cluster, make a new cluster
    if len(connected_clusters) == 0:
        # Allows us to modify cluster_id, so it always keeps count properly
        global cluster_id
        new_cluster = Cluster(cluster_id)
        cluster_id += 1
        new_cluster.add_stream(new_stream)
        clusters.append(new_cluster)
    # if there's only one cluster that touches our stream, add the stream to that cluster
    elif len(connected_clusters) == 1:
        i = connected_clusters[0]
        clusters[i].add_stream(new_stream)
    # If there are two clusters that we touch, we merge those two clusters, while also adding our new stream
    elif len(connected_clusters) == 2:
        cluster_one = clusters[connected_clusters[0]]
        cluster_two = clusters[connected_clusters[1]]
        new_cluster = merge_clusters(cluster_one, cluster_two, new_stream)

        clusters.remove(cluster_one)
        clusters.remove(cluster_two)
        clusters.append(new_cluster)


def find_connected_clusters(clusters, new_stream):
    """
    Finds all the clusters that the polyline connects to, and returns an array of all those available
    :param clusters: A list of clusters
    :param new_stream: The stream we care about
    :return: A list of indexes for clusters that are connected to the stream
    """
    connected_clusters = []

    for i in range(len(clusters)):
        if is_in_cluster(new_stream, clusters[i]):
            connected_clusters.append(i)

    return connected_clusters


def is_in_cluster(stream, cluster):
    """
    Returns true if the stream is connected to the cluster, false otherwise
    :param stream: The stream we care about
    :param cluster: The cluster we're examining
    :return: Boolean
    """
    stream_endpoints = []

    boundary = stream.polyline.boundary()
    stream_endpoints.append(boundary.firstPoint)
    stream_endpoints.append(boundary.lastPoint)

    cluster_endpoints = cluster.endpoints

    for cluster_endpoint in cluster_endpoints:
        for stream_endpoint in stream_endpoints:
            if cluster_endpoint.equals(stream_endpoint):
                return True

    return False


def merge_clusters(cluster_one, cluster_two, new_stream):
    """
    Merges two clusters and a new stream and returns them up
    :param cluster_one: The first cluster to merge
    :param cluster_two: The second cluster to merge
    :param new_stream: The new stream that connects them
    :return: A new merged stream
    """
    global cluster_id  # Allows us to modify cluster_id, so it always keeps count properly
    new_cluster = Cluster(cluster_id)
    cluster_id += 1

    new_cluster.merge(cluster_one, cluster_two)

    new_cluster.add_stream(new_stream)

    return new_cluster


def handle_clusters(input_network, clusters):
    """
    Takes the clusters and applies the drainage area that we want to it
    :param input_network: The network that we were given at first
    :param clusters: The list of clusters that we're working with
    :return: None
    """
    add_cluster_id(input_network, clusters)
    update_network_drainage_values(input_network, clusters)


def add_cluster_id(input_network, clusters):
    """
    Adds cluster ID attribute to the input network
    :param input_network: The network to add this info to
    :param clusters: The list of clusters that we're dealing with
    :return: None
    """
    arcpy.AddMessage("Adding clusterID to the input network...")

    list_fields = arcpy.ListFields(input_network, CLUSTER_FIELD_NAME)
    if len(list_fields) is not 1:
        arcpy.AddField_management(input_network, CLUSTER_FIELD_NAME, "SHORT", "", "", "", "", "NULLABLE")
    arcpy.CalculateField_management(input_network, CLUSTER_FIELD_NAME, -1, "PYTHON")

    for i in range(len(clusters)):
        clusters[i].id = i + 1

    with arcpy.da.UpdateCursor(input_network, ['ReachID', CLUSTER_FIELD_NAME, 'IsMultiCh']) as cursor:
        for row in cursor:
            # If the stream is braided. If it isn't, we don't care about its cluster id
            if row[2] == 1:
                for cluster in clusters:
                    if cluster.containsStream(row[0]):
                        row[1] = cluster.id
                cursor.updateRow(row)


def update_network_drainage_values(input_network, clusters):
    """
    Updates all the streams in our clusters based on whether or not they are mainstems
    :param input_network: The network we gave as an input
    :param clusters: The list of clusters for us to work with
    :return: None
    """
    arcpy.AddMessage("Updating Drainage Area Values...")
    with arcpy.da.UpdateCursor(input_network, ['ReachID', 'IsMainCh', 'iGeo_DA', 'IsMultiCh']) as cursor:
        for row in cursor:
            if row[3] == 1:
                update_stream_drainage_value(clusters, row, cursor)


def update_stream_drainage_value(clusters, row, cursor):
    """
    Updates the drainage area values for a single stream in the network
    :param clusters: The list of clusters we got earlier
    :param row: The row of the input network that we want to update
    :param cursor: The cursor we're using for the stream network
    :return: None
    """
    sidechannel_da_value = 25.0

    for cluster in clusters:
        if cluster.containsStream(row[0]):
            # if it's a side channel
            if row[1] == 0:
                # Set the side channels DA to the placeholder value, or the highest cluster value (whichever is lower)
                row[2] = min(cluster.maxDA, sidechannel_da_value)
            else:
                row[2] = cluster.maxDA

    cursor.updateRow(row)


def make_layers(input_network):
    """
    Makes the layers for the modified output
    :param input_network: The path to the network that we'll make a layer from
    :return:
    """
    arcpy.AddMessage("Making layers...")
    intermediates_folder = os.path.dirname(input_network)
    braid_folder_name = find_available_num_prefix(intermediates_folder) + "_AnabranchHandler"
    braid_folder = make_folder(intermediates_folder, braid_folder_name)

    trib_code_folder = os.path.dirname(os.path.abspath(__file__))
    symbology_folder = os.path.join(trib_code_folder, 'BRATSymbology')

    mainstem_symbology = os.path.join(symbology_folder, "AnabranchTypes.lyr")

    make_layer(braid_folder, input_network, "Anabranch Types", mainstem_symbology, is_raster=False)


def update_multi_ch(input_network):
    """
    Updates fields if there are no named reaches in the cluster
    :param input_network: The path to the network that we'll make a layer from
    :return:
    """
    ids = list(set(row[0] for row in arcpy.da.SearchCursor(input_network, "ClusterID")))
    ids.remove(-1)
    arcpy.MakeFeatureLayer_management(input_network, "network_lyr")

    for clusterId in ids:

        query = """ "ClusterID" = %s """ % clusterId
        arcpy.SelectLayerByAttribute_management("network_lyr", "NEW_SELECTION", query)
        count = arcpy.GetCount_management("network_lyr")
        ct = int(count.getOutput(0))

        query = """ "StreamName" = '' """
        arcpy.SelectLayerByAttribute_management("network_lyr", "SUBSET_SELECTION", query)
        count_unnamed = arcpy.GetCount_management("network_lyr")
        ct_unnamed = int(count_unnamed.getOutput(0))

        if ct == ct_unnamed:
            with arcpy.da.UpdateCursor("network_lyr", ['ClusterID', 'IsMultiCh', 'IsMainCh']) as cursor:
                for row in cursor:
                    row[0] = -1
                    row[1] = 0
                    row[2] = 1
                    cursor.updateRow(row)
