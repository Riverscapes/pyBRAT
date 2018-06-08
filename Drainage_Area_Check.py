# -------------------------------------------------------------------------------
# Name:        Drainage_Area_Check
# Purpose:     Looks through the stream network for reaches that have lower drainage networks than reaches up stream of
#              them, and modifies the network to fix that
#
# Author:      Braden Anderson
#
# Created:     06/2018
# -------------------------------------------------------------------------------

import arcpy
import os
from StreamObjects import DAValueCheckStream, StreamHeap


def main(stream_network):
    """
    The main function
    :param stream_network: The stream network that we want to fix up
    :return:
    """
    stream_heaps = find_streams(stream_network)

    check_heap(stream_network, stream_heaps)

    problem_streams = find_problem_streams(stream_heaps)

    fix_problem_streams(stream_network, problem_streams)


def find_streams(stream_network):
    """
    Creates a list of heaps, sorted by distance from the stream head
    :param stream_network: The stream network to be used
    :return:
    """
    arcpy.AddMessage("Finding Streams...")
    stream_heaps = []
    req_fields = ["ReachID", "StreamID", "ReachDist", "iGeo_DA"]
    with arcpy.da.SearchCursor(stream_network, req_fields) as cursor:
        for reach_id, stream_id, downstream_dist, drainage_area in cursor:
            new_stream = DAValueCheckStream(reach_id, stream_id, downstream_dist, drainage_area)
            new_stream_heap_index = find_new_stream_heap_index(stream_id, stream_heaps)

            if new_stream_heap_index is not None:
                stream_heaps[new_stream_heap_index].push_stream(new_stream)
            else:
                new_stream_heap = StreamHeap(new_stream)
                stream_heaps.append(new_stream_heap)
    return stream_heaps


def check_heap(stream_network, stream_heaps):
    with open(os.path.join(os.path.dirname(stream_network), "streams.txt"), 'w') as file:
        for stream_heap in stream_heaps:
            file.write(str(stream_heap) + '\n')
    for stream_heap in stream_heaps:
        streams = stream_heap.streams
        for k in range(len(streams)):
            try:
                high_dist = streams[k].downstream_dist
                low_dist_one = streams[(k*2) + 1].downstream_dist
                low_dist_two = streams[(k*2) + 2].downstream_dist
                if high_dist < low_dist_one or high_dist < low_dist_two:
                    raise Exception("Error in stream id: " + str(streams[k].stream_id))
            except IndexError:
                pass



def find_new_stream_heap_index(stream_id, stream_heaps):
    """
    Finds the index of the heap that the stream belongs to
    :param stream_id: The stream_id that we want to find in the heaps
    :param stream_heaps: A list of heaps
    :return: A number if that stream ID is in the list of heaps, otherwise, None
    """
    for i in range(len(stream_heaps)):
        if stream_id == stream_heaps[i].stream_id:
            return i
    return None



def find_problem_streams(stream_heaps):
    """
    Looks through the stream heaps, identifies streams that need to be fixed, and puts them in a list
    :param stream_heaps: A list of stream heaps
    :return:
    """
    for stream_heap in stream_heaps:
        while len(stream_heap.streams) > 0:
            upstream_reach = stream_heap.pop()

    return []


def fix_problem_streams(stream_network, problem_streams):
    """
    Fixes
    :param stream_network:
    :param problem_streams:
    :return:
    """