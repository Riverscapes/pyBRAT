# -------------------------------------------------------------------------------
# Name:        Conservation Restoration
# Purpose:     Adds the conservation and restoration model to the BRAT capacity output
#
# Author:      Sara Bangen
#
# Created:     06/2018
# Copyright:   (c) Bangen 2018
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
import sys
import os
import projectxml
import uuid
from SupportingFunctions import make_layer, make_folder, find_available_num


def main(projPath, in_network, out_name):

    arcpy.env.overwriteOutput = True

    out_network = os.path.dirname(in_network) + "/" + out_name + ".shp"
    arcpy.CopyFeatures_management(in_network, out_network)

    # check for oPBRC fields and delete if exists
    fields = [f.name for f in arcpy.ListFields(out_network)]
    if "oPBRC_UI" in fields:
        arcpy.DeleteField_management(out_network, "oPBRC_UI")
    if "oPBRC_UD" in fields:
        arcpy.DeleteField_management(out_network, "oPBRC_UD")
    if "oPBRC_CR" in fields:
        arcpy.DeleteField_management(out_network, "oPBRC_CR")

    arcpy.AddField_management(out_network, "oPBRC_UI", "TEXT", "", "", 25)
    arcpy.AddField_management(out_network, "oPBRC_UD", "TEXT", "", "", 50)
    arcpy.AddField_management(out_network, "oPBRC_CR", "TEXT", "", "", 25)

    fields = ['oPBRC_UI', 'oPBRC_UD', 'oPBRC_CR', 'oVC_PT', 'oVC_EX', 'oCC_PT', 'oCC_EX', 'iGeo_Slope']

    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            # 'oCC_EX' None
            if row[6] <= 0:
                # 'oVC_EX' Occasional, Frequent, or Pervasive
                if row[4] >= 1:
                    # 'iGeo_Slope' >= 23%
                    if row[7] >= 23:
                        row[1] = 'Unsuitable: Slope Limited'
                    # 'iGeo_Slope' < 23%
                    else:
                        row[1] = 'Unsuitable: Hydrologically Limited'
                # oVC_PT' None
                elif row[3] <= 0:
                    row[1] = 'Unsuitable: Vegetation Limited'
                else:
                    row[1] = 'Unsuitable: Anthropogenically Limited'
            else:
                row[1] = 'NA'
            cursor.updateRow(row)

    makeLayers(out_network)

    return out_network


def makeLayers(out_network):
    """
    Writes the layers
    :param out_network: The output network, which we want to make into a layer
    :return:
    """
    arcpy.AddMessage("Making layers...")
    analyses_folder = os.path.dirname(out_network)
    output_folder = make_folder(analyses_folder, find_available_num(analyses_folder) + "_Management")

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')
    managementLayer = os.path.join(symbologyFolder, "Beaver_Management_Zones_v2.lyr")
    managementLayer2 = os.path.join(symbologyFolder, "Dam_Building_Not_Likely.lyr")
    managementLayer3 = os.path.join(symbologyFolder, "Restoration_Conservation_Opportunities.lyr")

    make_layer(output_folder, out_network, "Beaver Management Zones", managementLayer, is_raster=False)
    make_layer(output_folder, out_network, "Unsuitable or Limited Opportunities", managementLayer2, is_raster=False)
    make_layer(output_folder, out_network, "Restoration or Conservation Opportunities", managementLayer3, is_raster=False)



def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])
