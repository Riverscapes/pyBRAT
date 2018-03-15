# -------------------------------------------------------------------------------
# Name:        BRAT Braid Handler
# Purpose:     Handles the braid clusters in a stream network
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------


import arcpy
from StreamObjects import Cluster, BraidStream

cluster_id = 0 # Provides a consistent way to refer to clusters, that give more information that a UUID


def main(inputNetwork):
    """
    The main function, where we go through the stream network and handle whatever we need to
    :param inputNetwork: The stream network that we want to give mainstem values
    :return: None
    """
    arcpy.AddMessage("Finding clusters...")
    clusters = findClusters(inputNetwork)

    arcpy.AddMessage("Adding clusterID to the input network...")

    listFields = arcpy.ListFields(inputNetwork, "ClusterID")
    if len(listFields) is not 1:
        arcpy.AddField_management(inputNetwork, "ClusterID", "SHORT", "", "", "", "", "NULLABLE")
    arcpy.CalculateField_management(inputNetwork, "ClusterID", -1, "PYTHON")

    with arcpy.da.UpdateCursor(inputNetwork, ['SegID', 'ClusterID']) as cursor:
        for row in cursor:
            for cluster in clusters:
                if cluster.containsStream(row[0]):
                    row[1] = cluster.id
            cursor.updateRow(row)

    handleClusters(inputNetwork, clusters)


def findClusters(inputNetwork):
    """
    Where we find all the clusters in the stream network
    :param inputNetwork: The stream network whose clusters we want to find
    :return: An array of clusters
    """
    clusters = []
    fields = ['SHAPE@', 'SegID', 'iGeo_DA', 'IsBraided']
    with arcpy.da.SearchCursor(inputNetwork, fields) as cursor:
        for polyline, stream_id, drainageArea, isBraided in cursor:
            if isBraided:
                addStreamToClusters(clusters, polyline, stream_id, drainageArea)

    return clusters


def addStreamToClusters(clusters, polyline, stream_id, drainageArea):
    """
    Adds the stream to the list of clusters that we have
    :param clusters: A list of clusters
    :param polyline: The geoprocessing object that contains a bunch of points we need
    :param stream_id: The stream's ID, which we'll use to compare against the original stream when it comes time to update it
    :param drainageArea: The stream's drainage area
    :return: None
    """
    newStream = BraidStream(polyline, stream_id, drainageArea)
    connectedClusters = findConnectedClusters(clusters, newStream)

    if len(connectedClusters) == 0:
        global cluster_id # Allows us to modify cluster_id, so it always keeps count properly
        new_cluster = Cluster(cluster_id)
        cluster_id += 1
        new_cluster.addStream(newStream)
        clusters.append(new_cluster)
    elif len(connectedClusters) == 1:
        i = connectedClusters[0]
        clusters[i].addStream(newStream)
    elif len(connectedClusters) == 2:
        cluster_one = clusters[connectedClusters[0]]
        cluster_two = clusters[connectedClusters[1]]
        new_cluster = mergeClusters(cluster_one, cluster_two, newStream)

        clusters.remove(cluster_one)
        clusters.remove(cluster_two)
        clusters.append(new_cluster)



def findConnectedClusters(clusters, newStream):
    """
    Finds all the clusters that the polyline connects to, and returns an array of all those available
    :param clusters: A list of clusters
    :param newStream: The stream we care about
    :return: A list of indexes for clusters that are connected to the stream
    """
    connectedClusters = []

    for i in range(len(clusters)):
        if isInCluster(newStream, clusters[i]):
            connectedClusters.append(i)

    return connectedClusters


def isInCluster(stream, cluster):
    """
    Returns true if the stream is connected to the cluster, false otherwise
    :param stream: The stream we care about
    :param cluster: The cluster we're examining
    :return: Boolean
    """
    streamEndpoints = []

    boundary = stream.polyline.boundary()
    streamEndpoints.append(boundary.firstPoint)
    streamEndpoints.append(boundary.lastPoint)

    clusterEndpoints = cluster.endpoints

    for clusterEndpoint in clusterEndpoints:
        for streamEndpoint in streamEndpoints:
            if clusterEndpoint.equals(streamEndpoint):
                return True

    return False


def mergeClusters(cluster_one, cluster_two, new_stream):
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

    new_cluster.addStream(new_stream)

    return new_cluster



def handleClusters(inputNetwork, clusters):
    pass
