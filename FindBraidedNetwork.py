# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Name:             Find Braided Reaches in Stream Network                          #
# Purpose:          Find Braided Reaches as part of network preprocessing steps.    #
#                                                                                   #
# Author:           Kelly Whitehead (kelly@southforkresearch.org)                   #
#                   Jesse Langdon                                                   #
#                   South Fork Research, Inc                                        #
#                   Seattle, Washington                                             #
#                                                                                   #
# Created:          2014-Sept-30                                                    #
# Version:          2.0 beta                                                        #
# Modified:         2017-Feb-16                                                     #
# Documentation:    http://gnat.riverscapes.xyz/                                    #
#                                                                                   #
# Copyright:        (c) Kelly Whitehead, Jesse Langdon 2017                         #
#                                                                                   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#!/usr/bin/env python

# Import modules
import os
import sys
import arcpy


def main(fcStreamNetwork, canal, tempDir, is_verbose):
    # Polyline prep
    if is_verbose:
        arcpy.AddMessage("Finding multithreaded streams...")
    listFields = arcpy.ListFields(fcStreamNetwork,"IsMultiCh")
    if len(listFields) is not 1:
        arcpy.AddField_management(fcStreamNetwork, "IsMultiCh", "SHORT", "", "", "", "", "NULLABLE")
    arcpy.CalculateField_management(fcStreamNetwork,"IsMultiCh",0,"PYTHON")

    # Process
    if canal is None:
        findBraidedReaches(fcStreamNetwork, is_verbose)
    else:
        handleCanals(fcStreamNetwork, canal, tempDir, is_verbose)

    return


def handleCanals(streamNetwork, canal, tempFolder, is_verbose):
    if is_verbose:
        arcpy.AddMessage("Removing canals that were given from the stream network for the purposes of multithreadedness...")
    if arcpy.GetInstallInfo()['Version'][0:4] == '10.5':
        streamNetworkNoCanals = os.path.join(tempFolder, "NoCanals.shp")
    else:
        streamNetworkNoCanals = os.path.join('in_memory', 'NoCanals')

    arcpy.Erase_analysis(streamNetwork, canal, streamNetworkNoCanals)
    findBraidedReaches(streamNetworkNoCanals, is_verbose)

    with arcpy.da.UpdateCursor(streamNetworkNoCanals, "IsMultiCh") as cursor: # delete non-braided reaches
        for row in cursor:
            if row[0] == 0:
                cursor.deleteRow()

    arcpy.MakeFeatureLayer_management(streamNetwork,"lyrBraidedReaches")
    arcpy.MakeFeatureLayer_management(streamNetworkNoCanals,"lyrNoCanals")

    arcpy.SelectLayerByLocation_management("lyrBraidedReaches","SHARE_A_LINE_SEGMENT_WITH","lyrNoCanals",'',"NEW_SELECTION")

    arcpy.CalculateField_management("lyrBraidedReaches","IsMultiCh",1,"PYTHON")
    arcpy.CalculateField_management("lyrBraidedReaches","IsMainCh",0,"PYTHON")

    arcpy.Delete_management(streamNetworkNoCanals)


def findBraidedReaches(fcLines, is_verbose):
    if is_verbose:
        arcpy.AddMessage("Calculating multithreadedness...")
    # Clear temporary data
    if arcpy.Exists("in_memory//DonutPolygons"):
        arcpy.Delete_management("in_memory//DonutPolygons")
    if arcpy.Exists("lyrDonuts"):
        arcpy.Delete_management("lyrDonuts")
    if arcpy.Exists("lyrBraidedReaches"):
        arcpy.Delete_management("lyrBraidedReaches")
        
    # Find donut reaches
    arcpy.FeatureToPolygon_management(fcLines,"in_memory/DonutPolygons")
    arcpy.MakeFeatureLayer_management(fcLines,"lyrBraidedReaches")
    arcpy.MakeFeatureLayer_management("in_memory/DonutPolygons","lyrDonuts")
    arcpy.SelectLayerByLocation_management("lyrBraidedReaches","SHARE_A_LINE_SEGMENT_WITH","lyrDonuts",'',"NEW_SELECTION")
    arcpy.CalculateField_management("lyrBraidedReaches","IsMultiCh",1,"PYTHON")
    arcpy.CalculateField_management("lyrBraidedReaches","IsMainCh",0,"PYTHON")

# # Run as Script # # 
if __name__ == "__main__":

    main(sys.argv[1])