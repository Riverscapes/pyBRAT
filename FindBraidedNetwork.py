# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Name:        Find Braided Reaches in Stream Network                         #
# Purpose:     Find Braided Reaches as part of network preprocessing steps.   #
#                                                                             #
# Author:      Kelly Whitehead (kelly@southforkresearch.org)                  #
#              Jesse Langdon                                                  #
#              South Fork Research, Inc                                       #
#              Seattle, Washington                                            #
#                                                                             #
# Created:     2014-Sept-30                                                   #
# Version:     2.0 beta                                                       #
# Modified:    2017-Feb-16                                                    #
#                                                                             #
# Copyright:   (c) Kelly Whitehead, Jesse Langdon 2017                        #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#!/usr/bin/env python

# Import modules
import sys
import arcpy


def main(fcStreamNetwork):

    # Polyline prep
    listFields = arcpy.ListFields(fcStreamNetwork,"IsBraided")
    if len(listFields) is not 1:
        arcpy.AddField_management(fcStreamNetwork, "IsBraided", "SHORT", "", "", "", "", "NULLABLE")
    arcpy.CalculateField_management(fcStreamNetwork,"IsBraided",0,"PYTHON")

    # Process
    findBraidedReaches(fcStreamNetwork)

    return


def findBraidedReaches(fcLines):

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
    arcpy.CalculateField_management("lyrBraidedReaches","IsBraided",1,"PYTHON")

# # Run as Script # # 
if __name__ == "__main__":

    main(sys.argv[1])