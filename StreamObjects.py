# -------------------------------------------------------------------------------
# Name:        StreamObjects
# Purpose:     This file holds classes that will be used to hold data in BRAT tools
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------

import heapq

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
        :param given_stream: The stream ID that we want to check. Is an int
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


class DAValueCheckStream:
    def __init__(self, reach_id,  stream_id, downstream_dist, drainage_area, stream_name):
        self.reach_id = reach_id
        self.stream_id = stream_id
        self.downstream_dist = downstream_dist
        self.drainage_area = drainage_area
        self.stream_name = stream_name

    def __lt__(self, other):
        """
        Our heap is sorted based on how far downstream a reach is, so we want comparison to use downstream_dist to sort
        """
        if not isinstance(other, DAValueCheckStream):
            raise Exception("Comparing a DAValueCheckStream to another data type is not currently supported")
        return self.downstream_dist < other.downstream_dist

    def __gt__(self, other):
        """
        Our heap is sorted based on how far downstream a reach is, so we want comparison to use downstream_dist to sort
        """
        if not isinstance(other, DAValueCheckStream):
            raise Exception("Comparing a DAValueCheckStream to another data type is not currently supported")
        return self.downstream_dist < other.downstream_dist


class Something:
    def __init__(self, reach_id,  stream_id, downstream_dist, drainage_area, stream_name):
        self.reach_id = reach_id
        self.stream_id = stream_id
        self.downstream_dist = downstream_dist
        self.drainage_area = drainage_area
        self.stream_name = stream_name

    def __lt__(self, other):
        """
        Our heap is sorted based on how far downstream a reach is, so we want comparison to use downstream_dist to sort
        """
        if not isinstance(other, DAValueCheckStream):
            raise Exception("Comparing a DAValueCheckStream to another data type is not currently supported")
        return self.downstream_dist < other.downstream_dist

    def __gt__(self, other):
        """
        Our heap is sorted based on how far downstream a reach is, so we want comparison to use downstream_dist to sort
        """
        if not isinstance(other, DAValueCheckStream):
            raise Exception("Comparing a DAValueCheckStream to another data type is not currently supported")
        return self.downstream_dist < other.downstream_dist


class StreamHeap:
    def __init__(self, first_stream):
        self.streams = [first_stream]
        self.stream_name = first_stream.stream_name

    def first_element(self):
        return self.streams[0]

    def push_stream(self, given_stream):
        heapq.heappush(self.streams, given_stream)

    def pop(self):
        return heapq.heappop(self.streams)
