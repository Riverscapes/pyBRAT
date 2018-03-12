# -------------------------------------------------------------------------------
# Name:        BRAT Braid Handler
# Purpose:     Handles the braid clusters in a stream network
#
# Author:      Braden Anderson
#
# Created:     03/2018
# -------------------------------------------------------------------------------


import arcpy
from Cluster import Cluster
from BraidStream import BraidStream


def main(inputNetwork):
    """
    The main function, where we go through the stream network and handle whatever we need to
    :param inputNetwork: The stream network that we want to give mainstem values
    :return: None
    """
    clusters = []

    findClusters(inputNetwork, clusters)

    handleClusters(inputNetwork, clusters)


def findClusters(inputNetwork, clusters):
    """
    Where we build
    :param inputNetwork:
    :param clusters:
    :return:
    """
    pass


def handleClusters(inputNetwork, clusters):
    pass
