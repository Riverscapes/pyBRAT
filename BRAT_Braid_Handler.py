# -------------------------------------------------------------------------------
# Name:        BRAT Braid Handler
# Purpose:     Handles the braid clusters in a stream network
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------


import arcpy
import os
from StreamObjects import Cluster, BraidStream

cluster_id = 0 # Provides a consistent way to refer to clusters, that give more information that a UUID
CLUSTERFIELDNAME = "ClusterID"


def main(inputNetwork):
    """
    The main function, where we go through the stream network and handle whatever we need to
    :param inputNetwork: The stream network that we want to give mainstem values
    :return: None
    """
    if not hasClusterIDs(inputNetwork):
        arcpy.AddMessage("Finding clusters...")
        clusters = findClusters(inputNetwork)

        handleClusters(inputNetwork, clusters)
    else:
        arcpy.AddMessage("Finding clusters based on the ClusterID field")
        clusters = getClustersFromIDs(inputNetwork)

        for i in range(len(clusters)):
            clusters[i].id = i+1

        updateNetworkDrainageValues(inputNetwork, clusters)

    makeLayers(inputNetwork)


def getClustersFromIDs(inputNetwork):
    """
    Returns an array of clusters based on the Cluster ID elements that they already have
    :param inputNetwork: The stream network
    :return: List of clusters
    """
    clusters = []
    fields = ['SHAPE@', CLUSTERFIELDNAME, "iGeo_DA", 'ReachID', "IsBraided"]
    with arcpy.da.SearchCursor(inputNetwork, fields) as cursor:
        for polyline, clusterID, drainageArea, segID, isBraided in cursor:
            if clusterID != -1 and isBraided == 1:
                newStream = BraidStream(polyline, segID, drainageArea)
                addStreamToClustersWithID(newStream, clusterID, clusters)

    return clusters


def addStreamToClustersWithID(newStream, clusterID, clusters):
    """
    Adds clusters to the stream based on the
    :param newStream: The stream we want to add
    :param clusterID: The cluster we want to add it to
    :param clusters: The clusters we've already made
    :return: None
    """
    for cluster in clusters:
        if cluster.id == clusterID:
            cluster.addStream(newStream)
            return #if we found the stream, we end now

    # If the for loop didn't return, add a new cluster with the new stream as the first stream
    newCluster = Cluster(clusterID)
    newCluster.addStream(newStream)
    clusters.append(newCluster)


def hasClusterIDs(inputNetwork):
    fields = arcpy.ListFields(inputNetwork)
    for field in fields:
        if field.name == CLUSTERFIELDNAME:
            return True
    return False


def findClusters(inputNetwork):
    """
    Where we find all the clusters in the stream network
    :param inputNetwork: The stream network whose clusters we want to find
    :return: An array of clusters
    """
    clusters = []
    fields = ['SHAPE@', 'ReachID', 'iGeo_DA', 'IsBraided']
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
    """
    Takes the clusters and applies the drainage area that we want to it
    :param inputNetwork: The network that we were given at first
    :param clusters: The list of clusters that we're working with
    :return: None
    """
    addClusterID(inputNetwork, clusters)
    updateNetworkDrainageValues(inputNetwork, clusters)


def addClusterID(inputNetwork, clusters):
    """
    Adds cluster ID attribute to the input network
    :param inputNetwork: The network to add this info to
    :param clusters: The list of clusters that we're dealing with
    :return: None
    """
    arcpy.AddMessage("Adding clusterID to the input network...")

    listFields = arcpy.ListFields(inputNetwork, CLUSTERFIELDNAME)
    if len(listFields) is not 1:
        arcpy.AddField_management(inputNetwork, CLUSTERFIELDNAME, "SHORT", "", "", "", "", "NULLABLE")
    arcpy.CalculateField_management(inputNetwork, CLUSTERFIELDNAME, -1, "PYTHON")

    for i in range(len(clusters)):
        clusters[i].id = i + 1

    with arcpy.da.UpdateCursor(inputNetwork, ['ReachID', CLUSTERFIELDNAME, 'IsBraided']) as cursor:
        for row in cursor:
            if row[2] == 1: # If the stream is braided. If it isn't, we don't care about its cluster id
                for cluster in clusters:
                    if cluster.containsStream(row[0]):
                        row[1] = cluster.id
                cursor.updateRow(row)


def updateNetworkDrainageValues(inputNetwork, clusters):
    """
    Updates all the streams in our clusters based on whether or not they are mainstems
    :param inputNetwork: The network we gave as an input
    :param clusters: The list of clusters for us to work with
    :return: None
    """
    arcpy.AddMessage("Updating Drainage Area Values...")
    with arcpy.da.UpdateCursor(inputNetwork, ['ReachID', 'IsMainstem', 'iGeo_DA', 'IsBraided']) as cursor:
        for row in cursor:
            if row[3] == 1:
                updateStreamDrainageValue(clusters, row, cursor)


def updateStreamDrainageValue(clusters, row, cursor):
    """
    Updates the drainage area values for a single stream in the network
    :param clusters: The list of clusters we got earlier
    :param row: The row of the input network that we want to update
    :param cursor: The cursor we're using for the stream network
    :return: None
    """
    sidechannelDAValue = 25.0

    for cluster in clusters:
        if cluster.containsStream(row[0]):
            if row[1] == 0: # if it's a side channel
                row[2] = min(cluster.maxDA, sidechannelDAValue) # set the side channels DA to the placeholder value, or the highest value in the cluster (whichever is lower)
            else:
                row[2] = cluster.maxDA

    cursor.updateRow(row)


def makeLayers(inputNetwork):
    """
    Makes the layers for the modified output
    :param inputNetwork: The path to the network that we'll make a layer from
    :return:
    """
    arcpy.AddMessage("Making layers...")
    intermediates_folder = os.path.dirname(inputNetwork)
    braid_folder_name = findAvailableNum(intermediates_folder) + "_BraidHandler"
    braid_folder = makeFolder(intermediates_folder, braid_folder_name)


    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')

    mainstemSymbology = os.path.join(symbologyFolder, "Mainstems.lyr")

    makeLayer(braid_folder, inputNetwork, "Mainstem Braids", mainstemSymbology, isRaster=False)


def makeLayer(output_folder, layer_base, new_layer_name, symbology_layer=None, isRaster=False, description="Made Up Description"):
    """
    Creates a layer and applies a symbology to it
    :param output_folder: Where we want to put the layer
    :param layer_base: What we should base the layer off of
    :param new_layer_name: What the layer should be called
    :param symbology_layer: The symbology that we will import
    :param isRaster: Tells us if it's a raster or not
    :param description: The discription to give to the layer file
    :return: The path to the new layer
    """
    new_layer = new_layer_name
    new_layer_file_name = new_layer_name.replace(" ", "")
    new_layer_save = os.path.join(output_folder, new_layer_file_name + ".lyr")

    if isRaster:
        try:
            arcpy.MakeRasterLayer_management(layer_base, new_layer)
        except arcpy.ExecuteError as err:
            if err[0][6:12] == "000873":
                arcpy.AddError(err)
                arcpy.AddMessage("The error above can often be fixed by removing layers or layer packages from the Table of Contents in ArcGIS.")
                raise Exception
            else:
                raise arcpy.ExecuteError(err)

    else:
        arcpy.MakeFeatureLayer_management(layer_base, new_layer)

    if symbology_layer:
        arcpy.ApplySymbologyFromLayer_management(new_layer, symbology_layer)

    arcpy.SaveToLayerFile_management(new_layer, new_layer_save, "RELATIVE")
    new_layer_instance = arcpy.mapping.Layer(new_layer_save)
    new_layer_instance.description = description
    new_layer_instance.save()
    return new_layer_save


def makeFolder(pathToLocation, newFolderName):
    """
    Makes a folder and returns the path to it
    :param pathToLocation: Where we want to put the folder
    :param newFolderName: What the folder will be called
    :return: String
    """
    newFolder = os.path.join(pathToLocation, newFolderName)
    if not os.path.exists(newFolder):
        os.mkdir(newFolder)
    return newFolder


def findAvailableNum(folderRoot):
    """
    Tells us the next number for a folder in the directory given
    :param folderRoot: Where we want to look for a number
    :return: A string, containing a number
    """
    takenNums = [fileName[0:2] for fileName in os.listdir(folderRoot)]
    POSSIBLENUMS = range(1, 100)
    for i in POSSIBLENUMS:
        stringVersion = str(i)
        if i < 10:
            stringVersion = '0' + stringVersion
        if stringVersion not in takenNums:
            return stringVersion
    arcpy.AddWarning("There were too many files at " + folderRoot + " to have another folder that fits our naming convention")
    return "100"


