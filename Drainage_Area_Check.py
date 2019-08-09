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
from StreamObjects import DAValueCheckStream, ProblemStream, StreamHeap


def main(stream_network):
    """
    The main function
    :param stream_network: The stream network that we want to fix up
    :return:
    """
    stream_heaps = find_streams(stream_network)
    # check_heap(stream_network, stream_heaps)

    problem_streams = find_problem_streams(stream_heaps)
    # check_problem_streams(stream_network, problem_streams)

    fix_problem_streams(stream_network, problem_streams)


def find_streams(stream_network):
    """
    Creates a list of heaps, sorted by distance from the stream head
    :param stream_network: The stream network to be used
    :return: Sorted heap list
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
    """
    A simple function that's meant to write the data to a text file and raise errors if something seems wrong
    :param stream_network: The stream network to be used
    :param stream_heaps: List of stream heaps
    :return:
    """
    with open(os.path.join(os.path.dirname(stream_network), "streams.txt"), 'w') as checkFile:
        for stream_heap in stream_heaps:
            checkFile.write(str(stream_heap) + '\n')
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
    arcpy.AddMessage("Stream Heaps passed check")


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
    :return: A list of problem streams
    """
    arcpy.AddMessage("Identifying problem streams...")
    problem_streams = []
    for stream_heap in stream_heaps:
        while len(stream_heap.streams) > 0:
            downstream_reach = stream_heap.pop()
            max_upstream_drainage_area = 0.0
            for stream in stream_heap.streams:
                if stream.drainage_area > max_upstream_drainage_area:
                    max_upstream_drainage_area = stream.drainage_area

            if downstream_reach.drainage_area < max_upstream_drainage_area:
                new_problem_stream = ProblemStream(downstream_reach.reach_id,
                                                   downstream_reach.stream_id,
                                                   downstream_reach.drainage_area,
                                                   max_upstream_drainage_area)
                problem_streams.append(new_problem_stream)

    return problem_streams


def check_problem_streams(stream_network, problem_streams):
    """
    A simple function that's meant to write the data to a text file and raise errors if something seems wrong
    :param stream_network: The stream network to be used
    :param problem_streams: The list of problem streams created by find_problem_streams
    :return:
    """
    max_orig_da = 0
    max_orig_da_id = -1
    with open(os.path.join(os.path.dirname(stream_network), "problemStreams.txt"), 'w') as checkFile:
        for problem_stream in problem_streams:
            checkFile.write(str(problem_stream) + '\n')
            if problem_stream.orig_drainage_area > 50:
                arcpy.AddWarning("Reach " + str(problem_stream.reach_id) + " may not be a problem stream")
            if problem_stream.orig_drainage_area > max_orig_da:
                max_orig_da = problem_stream.orig_drainage_area
                max_orig_da_id = problem_stream.reach_id
            if problem_stream.orig_drainage_area > problem_stream.fixed_drainage_area:
                raise Exception("Something weird with the following reach:\n" + str(problem_stream))
    arcpy.AddMessage("Problem Streams passed check")
    arcpy.AddMessage("Max problem DA: " + str(max_orig_da))
    arcpy.AddMessage("Max problem DA ID: " + str(max_orig_da_id))


def fix_problem_streams(stream_network, problem_streams):
    """
    Goes through the stream network and fixes problem streams
    :param stream_network: The stream network to be used
    :param problem_streams: The list of problem streams created by find_problem_streams
    :return:
    """
    arcpy.AddMessage("Fixing Streams...")
    arcpy.AddField_management(stream_network, "Orig_DA", "DOUBLE")
    req_fields = ["ReachID", "iGeo_DA", "Orig_DA"]
    with arcpy.da.UpdateCursor(stream_network, req_fields) as cursor:
        for row in cursor:
            reach_id = row[0]
            drain_area = row[1]
            problem_stream = find_problem_stream(reach_id, problem_streams)
            if problem_stream:
                row[1] = problem_stream.fixed_drainage_area
                row[2] = problem_stream.orig_drainage_area
            else:
                row[2] = drain_area
            cursor.updateRow(row)
    write_problem_streams(stream_network, problem_streams)


def write_problem_streams(stream_network, problem_streams):
    """
    Writes the list of problem streams to a file
    :param stream_network: The stream network to be used
    :param problem_streams: The list of problem streams created by find_problem_streams
    :return:
    """
    with open(os.path.join(os.path.dirname(stream_network), "ProblemStreamsList.txt"), 'w') as writeFile:
        writeFile.write("This is a list of all streams that were changed by the Drainage Area Check\n")
        writeFile.write("Number of streams edited: " + str(len(problem_streams)) + '\n\n')
        for problem_stream in problem_streams:
            writeFile.write("Altered Reach #" + str(problem_stream.reach_id) + '\n')


def find_problem_stream(reach_id, problem_streams):
    """
    Returns the problem stream that goes with the reach ID.
    :param reach_id: The reach ID to check for.
    :param problem_streams: The list of problem streams created by find_problem_streams.
    :return: If the reach ID is present, returns the problem stream. Otherwise, is returns None.
    """
    for problem_stream in problem_streams:
        if problem_stream.reach_id == reach_id:
            return problem_stream
    return None
