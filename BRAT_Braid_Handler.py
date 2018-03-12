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


def main(inputNetwork):
    """
    The main function, where we go through the stream network and handle whatever we need to
    :param inputNetwork: The stream network that we want to give mainstem values
    :return: None
    """

    clusters = findClusters(inputNetwork)

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
        for polyline, id, drainageArea, isBraided in cursor:
            if isBraided:
                addStreamToClusters(clusters, polyline, id, drainageArea)

    return clusters


def addStreamToClusters(clusters, polyline, id, drainageArea):
    """
    Adds the stream to the list of clusters that we have
    :param clusters: A list of clusters
    :param polyline: The geoprocessing object that contains a bunch of points we need
    :param id: The stream's ID, which we'll use to compare against the original stream when it comes time to update it
    :param drainageArea: The stream's drainage area
    :return: None
    """
    newStream = BraidStream(polyline, id, drainageArea)
    connectedClusters = findConnectedClusters(clusters, newStream)

    if len(connectedClusters) == 0:
        newCluster = Cluster(newStream)
        clusters.append(newCluster)
    elif len(connectedClusters) == 1:
        i = connectedClusters[0]
        clusters[i].addStream(newStream)
    elif len(connectedClusters) == 2:
        mergeClusters(clusters, connectedClusters, newStream)



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
    :return:
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


def mergeClusters(clusters, connectedClusters, newStream):
    """
    Merges two clusters together if a new stream connects them
    :param clusters: A list of clusters
    :param connectedClusters: A list containing the indexes we're worried about
    :param newStream: The stream that connects the two clusters
    :return: None
    """
    clusterOne = clusters.pop(connectedClusters[0])
    clusterTwo = clusters.pop(connectedClusters[1])
    


def handleClusters(inputNetwork, clusters):
    pass
