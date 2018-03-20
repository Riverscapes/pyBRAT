# -------------------------------------------------------------------------------
# Name:        Conflict Probability
# Purpose:     Adds potential for conflict to the BRAT capacity output
#
# Author:      Jordan Gilbert
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
import numpy as np
import os
import sys
import projectxml
import uuid


def main(
    projPath,
    in_network,
    CrossingLow,
    CrossingHigh,
    AdjLow,
    AdjHigh,
    CanalLow,
    CanalHigh,
    RRLow,
    RRHigh,
    out_name):

    scratch = 'in_memory'

    arcpy.env.overwriteOutput = True

    # CrossingLow = 10
    # CrossingHigh = 100
    # AdjLow = 10
    # AdjHigh = 100
    # CanalLow = 50
    # CanalHigh = 200
    # RRLow = 30
    # RRHigh = 100

    # function to calculate slope-intercept equation based on user inputs
    def slopeInt(lowValue, highValue):
        x1 = lowValue
        y1 = 0.99
        x2 = highValue
        y2 = 0.01
        m = (y2 - y1)/(x2 - x1) # calculate slope
        b = y1 - (m * x1) # calculate y-intercept
        return [m, b]

    if out_name.endswith('.shp'):
        out_network = os.path.dirname(in_network) + "/" + out_name
    else:
        out_network = os.path.dirname(in_network) + "/" + out_name + ".shp"

    arcpy.CopyFeatures_management(in_network, out_network)

    # check for oPC_Prob field and delete if already exists
    fields = [f.name for f in arcpy.ListFields(out_network)]
    if "oPC_Prob" in fields:
        arcpy.DeleteField_management(out_network, "oPC_Prob")

    # create segid array for joining output
    segid_np = arcpy.da.FeatureClassToNumPyArray(out_network, "SegID")
    segid_array = np.asarray(segid_np, np.int64)

    # road crossing conflict
    if "iPC_RoadX" in fields:
        roadx_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RoadX")
        roadx = np.asarray(roadx_array, np.float64)
        #roadx_prob = np.zeros_like(roadx)
        roadx_prob = np.empty_like(roadx)
        m = slopeInt(CrossingLow, CrossingHigh)[0]
        b = slopeInt(CrossingLow, CrossingHigh)[1]
        for i in range(len(roadx)):
            if roadx[i] >= 0 and roadx[i] <= CrossingLow:
                roadx_prob[i] = 0.99
            elif roadx[i] > CrossingLow and roadx[i] <= CrossingHigh:
                roadx_prob[i] = m * roadx[i] + b
            elif roadx[i] > CrossingHigh:
                roadx_prob[i] = 0.01
            else:
                roadx_prob[i] = 0.01

        del roadx_array, roadx, m, b
    else:
        roadx_prob = np.zeros_like(segid_array)

    # road adjacent conflict
    if "iPC_RoadAd" in fields:
        roadad_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RoadAd")
        roadad = np.asarray(roadad_array, np.float64)
        #roadad_prob = np.zeros_like(roadad)
        roadad_prob = np.empty_like(roadad)
        m = slopeInt(AdjLow, AdjHigh)[0]
        b = slopeInt(AdjLow, AdjHigh)[1]
        for i in range(len(roadad)):
            if roadad[i] >= 0 and roadad[i] <= AdjLow:
                roadad_prob[i] = 0.99
            elif roadad[i] > AdjLow and roadad[i] <= AdjHigh:
                roadad_prob[i] = m * roadad[i] + b
            elif roadad[i] > AdjHigh:
                roadad_prob[i] = 0.01
            else:
                roadad_prob[i] = 0.01

        del roadad_array, roadad, m, b
    else:
        roadad_prob = np.zeros_like(segid_array)

    # canal conflict
    if "iPC_Canal" in fields:
        canal_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_Canal")
        canal = np.asarray(canal_array, np.float64)
        #canal_prob = np.zeros_like(canal)
        canal_prob = np.empty_like(canal)
        m = slopeInt(CanalLow, CanalHigh)[0]
        b = slopeInt(CanalLow, CanalHigh)[1]
        for i in range(len(canal)):
            if canal[i] >= 0 and canal[i] <= CanalLow:
                canal_prob[i] = 0.99
            elif canal[i] > CanalLow and canal[i] <= CanalHigh:
                canal_prob[i] = m * canal[i] + b
            elif canal[i] > CanalHigh:
                canal_prob[i] = 0.01
            else:
                canal_prob[i] = 0.01

        del canal_array, canal, m, b
    else:
        canal_prob = np.zeros_like(segid_array)

    # railroad conflict
    if "iPC_RR" in fields:
        rr_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RR")
        rr = np.asarray(rr_array, np.float64)
        #rr_prob = np.zeros_like(rr)
        rr_prob = np.empty_like(rr)
        m = slopeInt(RRLow, RRHigh)[0]
        b = slopeInt(RRLow, RRHigh)[1]
        for i in range(len(rr)):
            if rr[i] >= 0 and rr[i] <= RRLow:
                rr_prob[i] = 0.99
            elif rr[i] > RRLow and rr[i] <= RRHigh:
                rr_prob[i] = m * rr[i] + b
            elif rr[i] > RRHigh:
                rr_prob[i] = 0.01
            else:
                rr_prob[i] = 0.01

        del rr_array, rr, m, b
    else:
        rr_prob = np.zeros_like(segid_array)

    oPC_Prob = np.fmax(roadx_prob, np.fmax(roadad_prob, np.fmax(canal_prob, rr_prob)))

    # save the output text file
    columns = np.column_stack((segid_array, oPC_Prob))
    out_table = os.path.dirname(out_network) + "/oPC_Prob_Table.txt"
    np.savetxt(out_table, columns, delimiter = ",", header = "SegID, oPC_Prob", comments = "")

    opc_prob_table = scratch + "/opc_prob_table"
    arcpy.CopyRows_management(out_table, opc_prob_table)

    # join the output to the flowline network
    # create empty dictionary to hold input table field values
    tblDict = {}
    # add values to dictionary
    with arcpy.da.SearchCursor(opc_prob_table, ['SegID', 'oPC_Prob']) as cursor:
        for row in cursor:
            tblDict[row[0]] = row[1]
    # populate flowline network out field
    arcpy.AddField_management(out_network, 'oPC_Prob', 'DOUBLE')
    with arcpy.da.UpdateCursor(out_network, ['SegID', 'oPC_Prob']) as cursor:
        for row in cursor:
            try:
                aKey = row[0]
                row[1] = tblDict[aKey]
                cursor.updateRow(row)
            except:
                pass
    tblDict.clear()

    arcpy.Delete_management(out_table)
    arcpy.Delete_management(opc_prob_table)

    addxmloutput(projPath, in_network, out_network)


def addxmloutput(projPath, in_network, out_network):
    """add the capacity output to the project xml file"""

    # xml file
    xmlfile = projPath + "/project.rs.xml"

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

    exxml.addOutput("BRAT Analysis", "Vector", "BRAT Conflict Output", out_network[out_network.find("02_Analyses"):],
                    outrz, guid=getUUID())

    exxml.write()


def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
        sys.argv[8],
        sys.argv[9],
        sys.argv[10],
        sys.argv[11]
    )
