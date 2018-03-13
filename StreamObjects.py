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

        #TODO Make sure this is up to snuff
        """
        :param given_id:
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


    def __eq__(self, other):
        #Todo write equal for clusters
        if isinstance(other, Cluster):
            return False
        else:
            return self.id == other.id


class BraidStream:
    def __init__(self, polyline, given_id, drainageArea):
        self.polyline = polyline
        self.id = given_id
        self.drainageArea = drainageArea