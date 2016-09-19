#-------------------------------------------------------------------------------
# Name:        Conflict Probability
# Purpose:     Adds potential for conflict to the BRAT capacity output
#
# Author:      Jordan Gilbert
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
import numpy as np
import os
import sys

def main(
    in_network,
    out_network,
    scratch):

    arcpy.env.overwriteOutput = True

    CrossingLow = 10
    CrossingHigh = 100
    AdjLow = 10
    AdjHigh = 100
    CanalLow = 50
    CanalHigh = 200
    RRLow = 30
    RRHigh = 100

    arcpy.CopyFeatures_management(in_network, out_network)

    #culvert conflict
    culv_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_CulvX")
    culv = np.asarray(culv_array, np.float64)

    culv_prob = np.zeros_like(culv)

    for i in range(len(culv)):
        if culv[i] >= 0 and culv[i] <= CrossingLow:
            culv_prob[i] = 0.9
        elif culv[i] > CrossingLow and culv[i] <= CrossingHigh:
            culv_prob[i] = -0.009889 * culv[i] + 0.99889
        elif culv[i] > CrossingHigh:
            culv_prob[i] = 0.01
        else:
            culv_prob[i] = 0.01

    del culv_array, culv

    # road crossing conflict
    roadx_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RoadX")
    roadx = np.asarray(roadx_array, np.float64)

    roadx_prob = np.zeros_like(roadx)

    for i in range(len(roadx)):
        if roadx[i] >= 0 and roadx[i] <= CrossingLow:
            roadx_prob[i] = 0.9
        elif roadx[i] > CrossingLow and roadx[i] <= CrossingHigh:
            roadx_prob[i] = -0.009889 * roadx[i] + 0.99889
        elif roadx[i] > CrossingHigh:
            roadx_prob[i] = 0.01
        else:
            roadx_prob[i] = 0.01

    del roadx_array, roadx

    # road adjacent conflict
    roadad_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RoadAd")
    roadad = np.asarray(roadad_array, np.float64)

    roadad_prob = np.zeros_like(roadad)

    for i in range(len(roadad)):
        if roadad[i] >= 0 and roadad[i] <= AdjLow:
            roadad_prob[i] = 0.9
        elif roadad[i] > AdjLow and roadad[i] <= AdjHigh:
            roadad_prob[i] = -0.009889 * roadad[i] + 0.99889
        elif roadad[i] > AdjHigh:
            roadad_prob[i] = 0.01
        else:
            roadad_prob[i] = 0.01

    del roadad_array, roadad

    # canal conflict
    canal_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_Canal")
    canal = np.asarray(canal_array, np.float64)

    canal_prob = np.zeros_like(canal)

    for i in range(len(canal)):
        if canal[i] >= 0 and canal[i] <= CanalLow:
            canal_prob[i] = 0.9
        elif canal[i] > CanalLow and canal[i] <= CanalHigh:
            canal_prob[i] = -0.005933 * canal[i] + 1.19665
        elif canal[i] > CanalHigh:
            canal_prob[i] = 0.01
        else:
            canal_prob[i] = 0.01

    # railroad conflict
    rr_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_RR")
    rr = np.asarray(rr_array, np.float64)

    rr_prob = np.zeros_like(rr)

    for i in range(len(rr)):
        if rr[i] >= 0 and rr[i] <= RRLow:
            rr_prob[i] = 0.75
        elif rr[i] > AdjLow and rr[i] <= AdjHigh:
            rr_prob[i] = -0.007 * rr[i] + 0.71
        elif rr[i] > AdjHigh:
            rr_prob[i] = 0.01
        else:
            rr_prob[i] = 0.01

    # land use conflict
    lu_array = arcpy.da.FeatureClassToNumPyArray(out_network, "iPC_LU")
    lu = np.asarray(lu_array, np.float64)

    lu_prob = np.zeros_like(lu)

    for i in range(len(lu)):
        if lu[i] >= 2:
            lu_prob[i] = 0.75
        elif lu[i] >= 1.25 and lu[i] < 2:
            lu_prob[i] = 0.5
        elif lu[i] < 1.25:
            lu_prob[i] = 0.01
        else:
            lu_prob[i] = 0.01

    oPC_Prob = np.fmax(culv_prob, np.fmax(roadx_prob, np.fmax(roadad_prob, np.fmax(canal_prob, np.fmax(rr_prob, lu_prob)))))

    # save the output text file
    fid = np.arange(0, len(oPC_Prob), 1)
    columns = np.column_stack((fid, oPC_Prob))
    out_table = os.path.dirname(in_network) + '/oPC_Prob_Table.txt'
    np.savetxt(out_table, columns, delimiter=',', header='FID, oPC_Prob', comments='')

    opc_prob_table = scratch + '/opc_prob_table'
    arcpy.CopyRows_management(out_table, opc_prob_table)
    arcpy.JoinField_management(in_network, 'FID', opc_prob_table, 'FID', 'oPC_Prob')
    arcpy.Delete_management(out_table)

    return out_network

if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3])
