# user defined arguments

in_network = r"Path.shp"
in_perennial = r"Path.shp"

# start of script
import arcpy
from arcpy.sa import *
import os

arcpy.CheckOutExtension('Spatial')
arcpy.env.overwriteOutput = True

pf = os.path.dirname(in_perennial)

network_lyr = arcpy.MakeFeatureLayer_management(in_network, 'network_lyr')
quer = """ "ClusterID" > 0 """
arcpy.SelectLayerByAttribute_management(network_lyr, 'NEW_SELECTION', quer)
clusters = arcpy.CopyFeatures_management(network_lyr,  os.path.join(pf, 'clusters.shp'))

clusters_lyr = arcpy.MakeFeatureLayer_management(clusters, 'clusters_lyr')

arcpy.SelectLayerByLocation_management(clusters_lyr, 'SHARE_A_LINE_SEGMENT_WITH', in_perennial)

isPerennialList = []
with arcpy.da.SearchCursor(clusters_lyr, 'ClusterID') as cursor:
    for row in cursor:
        if row[0] not in isPerennialList:
            isPerennialList.append(row[0])

quer = """ "StreamName" = '' """
arcpy.SelectLayerByAttribute_management(clusters_lyr, 'NEW_SELECTION', quer)
arcpy.SelectLayerByAttribute_management(clusters_lyr, 'SWITCH_SELECTION')

isNamedList = []
with arcpy.da.SearchCursor(clusters_lyr, 'ClusterID') as cursor:
    for row in cursor:
        if row[0] not in isPerennialList:
            isPerennialList.append(row[0])

arcpy.SelectLayerByAttribute_management(clusters_lyr, 'CLEAR_SELECTION')

with arcpy.da.UpdateCursor(in_network, ['ClusterID', 'IsMultiCh']) as cursor:
    for row in cursor:
        if row[0] not in isPerennialList and row[0] not in isNamedList:
            row[1] = 0
        cursor.updateRow(row)

arcpy.Delete_management(clusters)