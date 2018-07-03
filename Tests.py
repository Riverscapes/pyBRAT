# -------------------------------------------------------------------------------
# Name:        Tests
# Purpose:     Contains a number of tests to check for bugs in the code
#
# Author:      Braden Anderson
#
# Created:     06/2018
# -------------------------------------------------------------------------------


import arcpy


class TestException(Exception):
    pass


def test_reach_id_is_unique(network):
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
                raise TestException("Multiple reaches have a ReachID of " + str(reach_id))
            reach_ids.append(reach_id)


def report_exceptions(exceptions):
    """
    Reports the exceptions found during testing
    :param exceptions: The list of exceptions found during testing
    :return:
    """
    if len(exceptions) == 0:
        arcpy.AddMessage("All tests passed")
    else:
        arcpy.AddMessage("The following exceptions were raised during testing:")
        for exception in exceptions:
            arcpy.AddError(exception)
            arcpy.AddMessage("")