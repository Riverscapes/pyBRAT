# -------------------------------------------------------------------------------
# Name:        Conservation Restoration
# Purpose:     Adds the conservation and restoration model to the BRAT capacity output
#
# Author:      Jordan Gilbert
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
import sys
import os
import projectxml
import uuid


def main(projPath, in_network, out_name):

    arcpy.env.overwriteOutput = True

    out_network = os.path.dirname(in_network) + "/" + out_name + ".shp"
    arcpy.CopyFeatures_management(in_network, out_network)

    # check for oPBRC field and delete if exists
    network_fields = [f.name for f in arcpy.ListFields(out_network)]
    if "oPBRC" in network_fields:
        arcpy.DeleteField_management(out_network, "oPBRC")

    LowConflict = 0.25
    IntConflict = 0.5
    HighConflict = 0.75

    arcpy.AddField_management(out_network, "oPBRC", "TEXT", "", "", 60)

    cursor = arcpy.da.UpdateCursor(out_network, ["oCC_EX", "oCC_PT", "oPC_Prob", "oPBRC"])
    for row in cursor:

        if row[0] == 0:  # no existing capacity
            if row[1] > 5:
                if row[2] <= IntConflict:
                    row[3] = "Long Term Possibility Restoration Zone"
                else:
                    row[3] = "Unsuitable: Anthropogenically Limited"
            elif row[1] > 1:
                row[3] = "Unsuitable: Anthropogenically Limited"
            else:
                row[3] = "Unsuitable: Naturally Limited"

        elif row[0] > 0 and row[0] <= 1:  # rare existing capacity
            if row[1] > 5:
                if row[2] <= IntConflict:
                    row[3] = "Quick Return Restoration Zone"
                else:
                    row[3] = "Living with Beaver (Low Source)"
            elif row[1] > 1:
                if row[2] <= IntConflict:
                    row[3] = "Long Term Possibility Restoration Zone"
                else:
                    row[3] = "Living with Beaver (Low Source)"
            else:
                row[3] = "Unsuitable: Naturally Limited"

        elif row[0] > 1 and row[0] <= 5:  # occasional existing capacity
            if row[1] > 5:
                if row[2] <= IntConflict:
                    row[3] = "Long Term Possibility Restoration Zone"
                else:
                    row[3] = "Living with Beaver (Low Source)"
            else:
                row[3] = "Unsuitable: Naturally Limited"

        elif row[0] > 5 and row[0] <= 15:  # frequent existing capacity
            if row[1] > 15:
                if row[2] <= IntConflict:
                    row[3] = "Quick Return Restoration Zone"
                else:
                    row[3] = "Living with Beaver (High Source)"
            else:
                if row[2] <= IntConflict:
                    row[3] = "Low Hanging Fruit - Potential Restoration/Conservation Zone"
                else:
                    row[3] = "Living with Beaver (High Source)"

        elif row[0] > 15 and row[0] <= 50: # pervasive existing capacity
            if row[2] <= IntConflict:
                row[3] = "Low Hanging Fruit - Potential Restoration/Conservation Zone"
            else:
                row[3] = "Living with Beaver (High Source)"

        else:
            row[3] = "NOT PREDICTED - Requires Manual Attention"

        cursor.updateRow(row)

    del row
    del cursor

    addxmloutput(projPath, in_network, out_network)

    return out_network


def addxmloutput(projPath, in_network, out_network):
    """add the capacity output to the project xml file"""

    # xml file
    xmlfile = projPath + "/brat.xml"

    # make sure xml file exists
    if not os.path.exists(xmlfile):
        raise Exception("xml file for project does not exist. Return to table builder tool.")

    # open xml and add output
    exxml = projectxml.ExistingXML(xmlfile)

    realizations = exxml.rz.findall("BRAT")
    for i in range(len(realizations)):
        a = realizations[i].findall(".//Path")
        for j in range(len(a)):
            if os.path.abspath(a[j].text) == os.path.abspath(in_network[in_network.find("02_Analyses"):]):
                outrz = realizations[i]

    exxml.addOutput("Analysis", "Vector", "BRAT Management Output", out_network[out_network.find("02_Analyses"):], outrz,
                    guid=getUUID())

    exxml.write()


def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])
