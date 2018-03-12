# -------------------------------------------------------------------------------
# Name:        Braid Stream
# Purpose:     Holds the polyline and other data that we want for our braided streams
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------

class BraidStream:
    def __init__(self, polyline, id, drainageArea):
        self.polyline = polyline
        self.id = id
        self.drainageArea = drainageArea