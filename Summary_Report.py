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

def main(projectFolder, bratOutput, dams, outputName):
    """
    The main function
    :param projectFolder: The base folder of the project
    :param bratOutput: The output of BRAT (a polyline shapefile)
    :param dams: A shapefile containing a point for each dam
    :param outputName: The name of the output shape file
    :return:
    """
    outputPath = os.path.join(os.path.dirname(bratOutput), outputName + ".shp")
    arcpy.CopyFeatures_management(bratOutput, outputPath)
    damFields = ['e_DamCt', 'e_DamDens', 'e_DamPcC']
    otherFields = ['Ex_Categor', 'Pt_Categor', 'mCC_EX_Ct', 'mCC_PT_Ct', 'mCC_EXtoPT']
    newFields = damFields + otherFields
    textFields = ['Ex_Categor', 'Pt_Categor']

    for field in newFields:
        if field in textFields:
            arcpy.AddField_management(outputPath, field, field_length=50)
        else: # we assume that the default is doubles
            arcpy.AddField_management(outputPath, field, field_precision=0, field_scale=0)

    inputFields = ['SHAPE@LENGTH', 'oCC_EX', 'oCC_PT']

    if dams:
        setDamAttributes(outputPath, dams, damFields)

    setOtherAttributes(outputPath, )


def setDamAttributes(outputPath, dams, damFields):
    """
    Sets all the dam info
    :param outputPath: The polyline shapefile with BRAT output
    :param dams: The points shapefile of observed dams
    :param damFields: The fields we want to update for dam attributes
    :return:
    """