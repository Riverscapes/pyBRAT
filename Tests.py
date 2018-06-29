# -------------------------------------------------------------------------------
# Name:        Tests
# Purpose:     Contains a number of tests to check for bugs in the code
#
# Author:      Braden Anderson
#
# Created:     06/2018
# -------------------------------------------------------------------------------


import arcpy


def reach_id_is_unique(network):
    """
    Makes sure that the Reach ID is unique
    :param network: The network to test
    :return:
    """
    reach_ids = []
    with arcpy.da.SearchCursor(network, ['ReachID']) as cursor:
        for row in cursor:
            reach_id = row[0]
            if reach_id in reach_ids:
                raise Exception("Multiple reachs have the same ReachID")
            reach_ids.append(reach_id)