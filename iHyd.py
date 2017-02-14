# -------------------------------------------------------------------------------
# Name:        iHYD
# Purpose:     Adds the hydrologic attributes to the BRAT input table
#
# Author:      Jordan
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
import numpy as np
import os
import sys


def main(
    in_network,
    region,
    scratch):

    arcpy.env.overwriteOutput = True

    DA_array = arcpy.da.FeatureClassToNumPyArray(in_network, "iGeo_DA")
    DA = np.asarray(DA_array, np.float32)
    DAsqm = np.zeros_like(DA)
    DAsqm = DA * 0.3861021585424458

    Qlow = np.zeros_like(DA)
    Q2 = np.zeros_like(DA)

    arcpy.AddMessage("Adding Qlow and Q2 to network")
    # # # Add in regional curve equations here # # #

    if float(region) == 101:  # example 1 (box elder county)
        Qlow = 0.019875 * (DAsqm ** 0.6634) * (10 ** (0.6068 * 2.04))
        Q2 = 14.5 * DAsqm ** 0.328

    elif float(region) == 102:  # example 2 (upper green generic)
        Qlow = 4.2758 * (DAsqm ** 0.299)
        Q2 = 22.2 * (DAsqm ** 0.608) * ((42 - 40) ** 0.1)

    elif float(region) == 24:  # oregon region 5
        Qlow = 1.31397 * (10 ** -20.5528) * (DAsqm ** 0.9225) * (16.7 ** 3.1868) * (6810 ** 3.8546)
        Q2 = 1.06994 * (10 ** -9.3221) * (DAsqm ** 0.9418) * (16.7 ** 2.692) * (6810 ** 1.5663)

    else:
        raise Exception("region value is out of range")

    fid = np.arange(0, len(DA), 1)
    columns = np.column_stack((fid, Qlow))
    columns2 = np.column_stack((columns, Q2))
    out_table = os.path.dirname(in_network) + "/ihyd_Q_Table.txt"
    np.savetxt(out_table, columns2, delimiter=",", header="FID, iHyd_QLow, iHyd_Q2", comments="")

    ihyd_q_table = scratch + "/ihyd_q_table"
    arcpy.CopyRows_management(out_table, ihyd_q_table)
    arcpy.JoinField_management(in_network, "FID", ihyd_q_table, "FID", ["iHyd_QLow", "iHyd_Q2"])
    arcpy.Delete_management(out_table)

    # make sure Q2 is greater than Qlow
    cursor = arcpy.da.UpdateCursor(in_network, ["iHyd_QLow", "iHyd_Q2"])
    for row in cursor:
        if row[1] < row[0]:
            row[1] = row[0] + 5
        else:
            pass
        cursor.updateRow(row)
    del row
    del cursor

    arcpy.AddMessage("Adding stream power to network")
    # calculate Qlow stream power
    arcpy.AddField_management(in_network, "iHyd_SPLow", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(in_network, ["iGeo_Slope", "iHyd_QLow", "iHyd_SPLow"])
    for row in cursor:
        index = (1000 * 9.80665) * row[0] * (row[1] * 0.028316846592)
        row[2] = index
        cursor.updateRow(row)
    del row
    del cursor

    # calculate Q2 stream power
    arcpy.AddField_management(in_network, "iHyd_SP2", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(in_network, ["iGeo_Slope", "iHyd_Q2", "iHyd_SP2"])
    for row in cursor:
        index = (1000 * 9.80665) * row[0] * (row[1] * 0.028316846592)
        row[2] = index
        cursor.updateRow(row)
    del row
    del cursor

    return in_network

if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3])
