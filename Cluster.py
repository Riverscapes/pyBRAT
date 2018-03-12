# -------------------------------------------------------------------------------
# Name:        Cluster
# Purpose:     A class that holds a cluster of braided streams. Used primarily in BRAT_Braid_Handler.py
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------

class Cluster:
    def __init__(self, firstStream=''):
        """
        The constructor. If 
        :param firstStream:
        """
        self.streams = []
        if firstStream != '':
            self.streams.append(firstStream)

    def addStream(self, newStream):
        self.streams.append(newStream)