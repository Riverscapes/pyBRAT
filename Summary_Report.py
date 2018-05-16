# -------------------------------------------------------------------------------
# Name:        BRAT Validation
# Purpose:     Tests the output of BRAT against a shape file of beaver dams
#
# Author:      Braden Anderson
#
# Created:     05/2018
# -------------------------------------------------------------------------------

import os
import arcpy

def main(bratOutput, dams, outputName):
    """
    The main function
    :param bratOutput: The output of BRAT (a polyline shapefile)
    :param dams: A shapefile containing a point for each dam
    :param outputName: The name of the output shape file
    :return:
    """
    if outputName.endswith('.shp'):
        out_network = os.path.join(os.path.dirname(bratOutput), outputName)
    else:
        out_network = os.path.join(os.path.dirname(bratOutput), outputName + ".shp")
    arcpy.Delete_management(out_network)

    damFields = ['e_DamCt', 'e_DamDens', 'e_DamPcC']
    otherFields = ['Ex_Categor', 'Pt_Categor', 'mCC_EX_Ct', 'mCC_PT_Ct', 'mCC_EXtoPT']
    newFields = damFields + otherFields

    inputFields = ['SHAPE@LENGTH', 'oCC_EX', 'oCC_PT']

    if dams:
        arcpy.AddMessage("Adding fields that need dam input...")
        setDamAttributes(bratOutput, out_network, dams, damFields + ['Join_Count'] + inputFields, newFields)
    else:
        arcpy.CopyFeatures_management(bratOutput, out_network)
        addFields(out_network, otherFields)

    arcpy.AddMessage("Adding fields that don't need dam input...")
    setOtherAttributes(out_network, otherFields + inputFields)


def setDamAttributes(bratOutput, outputPath, dams, reqFields, newFields):
    """
    Sets all the dam info and updates the output file with that data
    :param bratOutput: The polyline we're basing our stuff off of
    :param outputPath: The polyline shapefile with BRAT output
    :param dams: The points shapefile of observed dams
    :param damFields: The fields we want to update for dam attributes
    :return:
    """
    arcpy.Snap_edit(dams, [[bratOutput, 'EDGE', '30 Meters']])
    arcpy.SpatialJoin_analysis(bratOutput,
                               dams,
                               outputPath,
                               join_operation='JOIN_ONE_TO_ONE',
                               join_type='KEEP_ALL',
                               match_option='INTERSECT')
    addFields(outputPath, newFields)

    with arcpy.da.UpdateCursor(outputPath, reqFields) as cursor:
        for row in cursor:
            damNum = row[-4]        # fourth to last attribute
            segLength = row[-3]   # third to last attribute
            oCC_EX = row[-2]        # second to last attribute
            oCC_PT = row[-1]        # last attribute

            row[0] = damNum
            row[1] = damNum / segLength * 1000
            try:
                row[2] = damNum / oCC_PT
            except ZeroDivisionError:
                row[2] = 0

            cursor.updateRow(row)

    arcpy.DeleteField_management(outputPath, ["Join_Count", "TARGET_FID"])



def addFields(outputPath, newFields):
    """
    Adds the fields we want to our output shape file
    :param outputPath: Our output shape file
    :param newFields: All the fields we want to add
    :return:
    """
    textFields = ['Ex_Categor', 'Pt_Categor']
    for field in newFields:
        if field in textFields:
            arcpy.AddField_management(outputPath, field, field_type="TEXT", field_length=50)
        else: # we assume that the default is doubles
            arcpy.AddField_management(outputPath, field, field_type="DOUBLE", field_precision=0, field_scale=0)


def setOtherAttributes(outputPath, fields):
    """
    Sets the attributes of all other things we want to do
    :param outputPath: The polyline shapefile with BRAT output
    :param fields: The fields we want to update
    :return:
    """
    with arcpy.da.UpdateCursor(outputPath, fields) as cursor:
        for row in cursor:
            segLength = row[-3] # third to last attribute
            oCC_EX = row[-2] # second to last attribute
            oCC_PT = row[-1] # last attribute

            # Handles Ex_Categor
            row[0] = handleCategory(oCC_EX)

            # Handles Pt_Categor
            row[1] = handleCategory(oCC_PT)

            # Handles mCC_EX_Ct
            row[2] = (oCC_EX * segLength) / 1000

            # Handles mCC_PT_Ct
            row[3] = (oCC_PT * segLength) / 1000

            # Handles mCC_EXtoPT
            if oCC_PT != 0:
                row[4] = oCC_EX / oCC_PT
            else:
                row[4] = 0

            cursor.updateRow(row)


def handleCategory(oCCVariable):
    """
    Returns a string based on the oCC value given to it
    :param oCCVariable: A number
    :return: String
    """
    if oCCVariable == 0:
        return "None"
    elif 0 < oCCVariable <= 1:
        return "Rare"
    elif 1 < oCCVariable <= 5:
        return "Occasional"
    elif 5 < oCCVariable <= 15:
        return "Frequent"
    elif 15 < oCCVariable <= 40:
        return "Pervasive"
    else:
        return "UNDEFINED"