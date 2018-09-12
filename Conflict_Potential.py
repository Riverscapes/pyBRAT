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
from SupportingFunctions import find_available_num, make_folder, make_layer
reload(make_layer)
reload(make_folder)
reload(find_available_num)


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
    out_network = find_oPC_Score(out_name, in_network, CrossingLow, CrossingHigh, AdjLow, AdjHigh, CanalLow, CanalHigh, RRLow, RRHigh, scratch)

    addxmloutput(projPath, in_network, out_network)

    makeLayers(out_network)


def find_oPC_Score(out_name, in_network, CrossingLow, CrossingHigh, AdjLow, AdjHigh, CanalLow, CanalHigh, RRLow, RRHigh, scratch):
    if out_name.endswith('.shp'):
        out_network = os.path.join(os.path.dirname(in_network), out_name)
    else:
        out_network = os.path.join(os.path.dirname(in_network), out_name + ".shp")

    arcpy.CopyFeatures_management(in_network, out_network)

    # check for oPC_Score field and delete if already exists
    fields = [f.name for f in arcpy.ListFields(out_network)]
    if "oPC_Score" in fields:
        arcpy.DeleteField_management(out_network, "oPC_Score")

    # create segid array for joining output
    segid_np = arcpy.da.FeatureClassToNumPyArray(out_network, "ReachID")
    segid_array = np.asarray(segid_np, np.int64)

    # road crossing conflict
    if "iPC_RoadX" in fields:
        roadx_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RoadX")
        roadx = np.asarray(roadx_array, np.float64)
        roadx_pc = np.empty_like(roadx)
        m = slopeInt(CrossingLow, CrossingHigh)[0]
        b = slopeInt(CrossingLow, CrossingHigh)[1]
        for i in range(len(roadx)):
            if roadx[i] >= 0 and roadx[i] <= CrossingLow:
                roadx_pc[i] = 0.99
            elif roadx[i] > CrossingLow and roadx[i] <= CrossingHigh:
                roadx_pc[i] = m * roadx[i] + b
            elif roadx[i] > CrossingHigh:
                roadx_pc[i] = 0.01
            else:
                roadx_pc[i] = 0.01

        del roadx_array, roadx, m, b
    else:
        roadx_pc = np.zeros_like(segid_array)

    # road adjacent conflict
    if "iPC_RoadAd" in fields:
        roadad_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RoadAd")
        roadad = np.asarray(roadad_array, np.float64)
        #roadad_pc = np.zeros_like(roadad)
        roadad_pc = np.empty_like(roadad)
        m = slopeInt(AdjLow, AdjHigh)[0]
        b = slopeInt(AdjLow, AdjHigh)[1]
        for i in range(len(roadad)):
            if roadad[i] >= 0 and roadad[i] <= AdjLow:
                roadad_pc[i] = 0.99
            elif roadad[i] > AdjLow and roadad[i] <= AdjHigh:
                roadad_pc[i] = m * roadad[i] + b
            elif roadad[i] > AdjHigh:
                roadad_pc[i] = 0.01
            else:
                roadad_pc[i] = 0.01

        del roadad_array, roadad, m, b
    else:
        roadad_pc = np.zeros_like(segid_array)

    # canal conflict
    if "iPC_Canal" in fields:
        canal_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_Canal")
        canal = np.asarray(canal_array, np.float64)
        #canal_pc = np.zeros_like(canal)
        canal_pc = np.empty_like(canal)
        m = slopeInt(CanalLow, CanalHigh)[0]
        b = slopeInt(CanalLow, CanalHigh)[1]
        for i in range(len(canal)):
            if canal[i] >= 0 and canal[i] <= CanalLow:
                canal_pc[i] = 0.99
            elif canal[i] > CanalLow and canal[i] <= CanalHigh:
                canal_pc[i] = m * canal[i] + b
            elif canal[i] > CanalHigh:
                canal_pc[i] = 0.01
            else:
                canal_pc[i] = 0.01

        del canal_array, canal, m, b
    else:
        canal_pc = np.zeros_like(segid_array)

    # railroad conflict
    if "iPC_RR" in fields:
        rr_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RR")
        rr = np.asarray(rr_array, np.float64)
        #rr_pc = np.zeros_like(rr)
        rr_pc = np.empty_like(rr)
        m = slopeInt(RRLow, RRHigh)[0]
        b = slopeInt(RRLow, RRHigh)[1]
        for i in range(len(rr)):
            if rr[i] >= 0 and rr[i] <= RRLow:
                rr_pc[i] = 0.99
            elif rr[i] > RRLow and rr[i] <= RRHigh:
                rr_pc[i] = m * rr[i] + b
            elif rr[i] > RRHigh:
                rr_pc[i] = 0.01
            else:
                rr_pc[i] = 0.01

        del rr_array, rr, m, b
    else:
        rr_pc = np.zeros_like(segid_array)

    # landuse conflict
    if "iPC_LU" in fields:
        lu_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_LU")
        lu = np.asarray(lu_array, np.float64)
        lu_pc = np.empty_like(lu)

        # for i in range(len(lu)):
        #     if lu[i] >= 2:
        #         lu_pc[i] = 0.75
        #     elif lu[i] >= 1.25 and lu[i] < 2:
        #         lu_pc[i] = 0.5
        #     elif lu[i] < 1.25:
        #         lu_pc[i] = 0.01
        #     else:
        #         lu_pc[i] = 0.01

        for i in range(len(lu)):
            if lu[i] >= 1.0:
                lu_pc[i] = 0.99
            elif lu[i] >= 0.66 and lu[i] < 1.0:
                lu_pc[i] = 0.75
            elif lu[i] >= 0.33 and lu[i] < 0.66:
                lu_pc[i] = 0.5
            elif lu[i] > 0 and lu[i] < 0.33:
                lu_pc[i] = 0.25
            else:
                lu_pc[i] = 0.01
    else:
        lu_pc = np.zeros_like(segid_array)

    # get max of all individual conflict potential scores
    # this is our conflict potential output
    oPC_Score = np.fmax(roadx_pc, np.fmax(roadad_pc, np.fmax(canal_pc, np.fmax(rr_pc, lu_pc))))

    # save the output text file
    columns = np.column_stack((segid_array, oPC_Score))
    out_table = os.path.dirname(out_network) + "/oPC_Score_Table.txt"
    np.savetxt(out_table, columns, delimiter = ",", header = "ReachID, oPC_Score", comments = "")

    opc_score_table = scratch + "/opc_score_table"
    arcpy.CopyRows_management(out_table, opc_score_table)

    # join the output to the flowline network
    # create empty dictionary to hold input table field values
    tblDict = {}
    # add values to dictionary
    with arcpy.da.SearchCursor(opc_score_table, ['ReachID', 'oPC_Score']) as cursor:
        for row in cursor:
            tblDict[row[0]] = row[1]
    # populate flowline network out field
    arcpy.AddField_management(out_network, 'oPC_Score', 'DOUBLE')
    with arcpy.da.UpdateCursor(out_network, ['ReachID', 'oPC_Score']) as cursor:
        for row in cursor:
            try:
                aKey = row[0]
                row[1] = tblDict[aKey]
                cursor.updateRow(row)
            except:
                pass
    tblDict.clear()

    arcpy.Delete_management(out_table)
    arcpy.Delete_management(opc_score_table)

    return out_network


# function to calculate slope-intercept equation based on user inputs
def slopeInt(lowValue, highValue):
    x1 = lowValue
    y1 = 0.99
    x2 = highValue
    y2 = 0.01
    m = (y2 - y1)/(x2 - x1) # calculate slope
    b = y1 - (m * x1) # calculate y-intercept
    return [m, b]


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

def makeLayers(out_network):
    """
    Writes the layers
    :param out_network: The output network, which we want to make into a layer
    :return:
    """
    arcpy.AddMessage("Making layers...")

    analyses_folder = os.path.dirname(out_network)
    output_folder = make_folder(analyses_folder, find_available_num(analyses_folder) + "_Conflict")

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')
    conflictLayer = os.path.join(symbologyFolder, "Conflict.lyr")

    make_layer(output_folder, out_network, "Conflict Potential", conflictLayer, is_raster=False)


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
        sys.argv[11],
        sys.argv[12]
    )
