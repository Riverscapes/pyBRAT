# -------------------------------------------------------------------------------
# Name:        Cluster
# Purpose:     A class that holds a cluster of braided streams. Used primarily in BRAT_Braid_Handler.py
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------

class Cluster:
    def __init__(self, firstStream=None):
        """
        The constructor. Can be initialized with a stream, or also not
        :param firstStream:
        """
        self.streams = []
        self.endpoints = []
        self.maxDA = 0.0

        if firstStream is not None:
            self.streams.append(firstStream)
            boundary = firstStream.polyline.boundary()
            self.endpoints.append(boundary.firstPoint)
            self.endpoints.append(boundary.lastPoint)
            self.maxDA = firstStream.drainageArea

    def addStream(self, newStream):
        self.streams.append(newStream)


class BraidStream:
    def __init__(self, polyline, id, drainageArea):
        self.polyline = polyline
        self.id = id
        self.drainageArea = drainageArea