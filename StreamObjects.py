# -------------------------------------------------------------------------------
# Name:        Cluster
# Purpose:     A class that holds a cluster of braided streams. Used primarily in BRAT_Braid_Handler.py
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------

class Cluster:
    def __init__(self, given_id):
        """
        The constructor for our Cluster class
        :param given_id: The identifier for our cluster, used in the equal function
        """
        self.streams = []
        self.endpoints = []
        self.maxDA = 0.0
        self.id = given_id

    def addStream(self, newStream):
        self.streams.append(newStream)
        boundary = newStream.polyline.boundary()
        self.endpoints.append(boundary.firstPoint)
        self.endpoints.append(boundary.lastPoint)
        self.maxDA = max(newStream.drainageArea, self.maxDA)


    def merge(self, cluster_one, cluster_two):
        """
        Takes the data from two clusters and combines them in this cluster
        :param cluster_one: The first Cluster to merge
        :param cluster_two: The second Cluster to merge
        :return:
        """
        if len(self.streams) != 0 or len(self.endpoints) != 0 or self.maxDA !=0: # we want this cluster to be empty
            raise Exception("Trying to merge on a cluster that isn't empty!")

        self.streams = cluster_one.streams + cluster_two.streams
        self.endpoints = cluster_one.endpoints + cluster_two.endpoints
        self.maxDA = max(cluster_one.maxDA, cluster_two.maxDA)


    def containsStream(self, given_stream):
        """
        Returns True if the stream given is inside the cluster, False if otherwise
        :param given_stream: The stream ID that we want to check
        :return: Boolean
        """
        for stream in self.streams:
            if stream.id == given_stream:
                return True

        return False


    def __eq__(self, other):
        if isinstance(other, Cluster):
            return False
        else:
            return self.id == other.id


class BraidStream:
    def __init__(self, polyline, given_id, drainageArea):
        self.polyline = polyline
        self.id = given_id
        self.drainageArea = drainageArea