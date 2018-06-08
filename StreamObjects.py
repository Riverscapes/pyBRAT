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
    def __init__(self, reach_id,  stream_id, downstream_dist, drainage_area):
        self.reach_id = reach_id
        self.stream_id = stream_id
        self.downstream_dist = downstream_dist
        self.drainage_area = drainage_area

    def __eq__(self, other):
        return self.reach_id == other.reach_id

    def __lt__(self, other):
        """
        The heap is based on downstream distance, so we define < and > based on downstream distance

        To make the heap a max heap, we reverse what might seem to be intuitive for > and <. To make it a min heap,
        replace ">" with "<" in the return statement
        """
        if not isinstance(other, DAValueCheckStream):
            raise Exception("Comparing a DAValueCheckStream to another data type is not currently supported")
        return self.downstream_dist > other.downstream_dist

    def __gt__(self, other):
        """
        The heap is based on downstream distance, so we define < and > based on downstream distance

        To make the heap a max heap, we reverse what might seem to be intuitive for > and <. To make it a min heap,
        replace "<" with ">" in the return statement
        """
        if not isinstance(other, DAValueCheckStream):
            raise Exception("Comparing a DAValueCheckStream to another data type is not currently supported")
        return self.downstream_dist < other.downstream_dist

    def __str__(self):
        return str(self.stream_id)


class StreamHeap:
    def __init__(self, first_stream):
        self.streams = [first_stream]
        self.stream_id = first_stream.stream_id

    def push_stream(self, given_stream):
        heapq.heappush(self.streams, given_stream)

    def pop(self):
        return heapq.heappop(self.streams)

    def __eq__(self, other):
        if not isinstance(other, StreamHeap):
            raise Exception("A StreamHeap can only be compared to another StreamHeap")
        return self.stream_id == other.stream_id

    def __str__(self):
        ret_string = '['
        for i in range(len(self.streams)):
            #ret_string += '(' + str(self.streams[i].reach_id) + ', ' + str(self.streams[i].stream_id) + ')'
            ret_string += str(self.streams[i].downstream_dist)
            if i + 1 < len(self.streams):
                ret_string += ', '
        ret_string += ']'
        return ret_string