# -------------------------------------------------------------------------------
# Name:        Drainage_Area_Check
# Purpose:     Looks through the stream network for reaches that have lower drainage networks than reaches up stream of
#              them, and modifies the network to fix that
#
# Author:      Braden Anderson
#
# Created:     06/2018
# -------------------------------------------------------------------------------

from StreamObjects import DAValueCheckStream, StreamHeap


def main(stream_network):
    """
    The main function
    :param stream_network: The stream network that we want to fix up
    :return:
    """
    stream_heaps = find_streams(stream_network)

    problem_streams = find_problem_streams(stream_heaps)

    fix_problem_streams(stream_network, problem_streams)


def find_streams(stream_network):
    """
    Creates a list of heaps, sorted by distance from the stream head
    :param stream_network: The stream network to be used
    :return:
    """
    return []


def find_problem_streams(stream_heaps):
    """
    Looks through the stream heaps, identifies streams that need to be fixed, and puts them in a list
    :param stream_heaps: A list of stream heaps
    :return:
    """
    return []


def fix_problem_streams(stream_network, problem_streams):
    """
    Fixes
    :param stream_network:
    :param problem_streams:
    :return:
    """