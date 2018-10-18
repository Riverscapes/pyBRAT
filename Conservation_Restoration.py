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


def main(projPath, in_network):

    arcpy.env.overwriteOutput = True

    # out_network = os.path.dirname(in_network) + "/" + out_name + ".shp"
    # arcpy.CopyFeatures_management(in_network, out_network)
    out_network = in_network

    # check for oPBRC fields and delete if exists
    fields = [f.name for f in arcpy.ListFields(out_network)]
    if "oPBRC_UI" in fields:
        arcpy.DeleteField_management(out_network, "oPBRC_UI")
    if "oPBRC_UD" in fields:
        arcpy.DeleteField_management(out_network, "oPBRC_UD")
    if "oPBRC_CR" in fields:
        arcpy.DeleteField_management(out_network, "oPBRC_CR")

    arcpy.AddField_management(out_network, "oPBRC_UI", "TEXT", "", "", 30)
    arcpy.AddField_management(out_network, "oPBRC_UD", "TEXT", "", "", 30)
    arcpy.AddField_management(out_network, "oPBRC_CR", "TEXT", "", "", 40)

    fields = ['oPBRC_UI', 'oPBRC_UD', 'oPBRC_CR', 'oVC_PT', 'oVC_EX', 'oCC_PT', 'oCC_EX', 'iGeo_Slope', 'mCC_HisDep', 'iPC_VLowLU', 'iPC_HighLU']

    # 'oPBRC_UI' (Areas beavers can build dams, but could be undesireable impacts)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            # 'oCC_EX' > 0 (i.e. where beavers can build dams currently)
            if row[6] > 0:
               row[0] = 'THINKING' # PLACEHOLDER UNTIL WE FIGURE THIS OUT 

            
            # If 'oCC_EX' = 0 now, then neglible risk
            else:
                row[0] = 'Negligible'
            cursor.updateRow(row)
            # LOGIC WE WILL CLEAN UP SOON... WE SHOULD EXPOSE ALL THRESHOLDS AS PARAMETERS TO USER
            #row[0] = 'Considerable Risk'
            #("oPC_Dist" < 30 OR "iPC_LU" > 0.6) AND ("oCC_EX" >= 15)
            #row[0] = 'Some Risk'
            #("oPC_Dist" < 100 OR "iPC_LU" > 0.6) AND ("oCC_EX" >= 5 AND "oCC_EX" < 15) 
            #row[0] = 'Minior Risk'
            #"(oPC_Dist" < 300 OR "iPC_LU" > 0.3) AND ("oCC_EX" > 0 AND "oCC_EX" < 5) 
            #row[0] = 'Negligible Risk'
            
            
    # 'oPBRC_UD' (Areas beavers can't build dams and why)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            # First deal with vegetation limitations
            # oVC_PT' None - Find places historically veg limited first.
            if row[3] <= 0:
                 # 'oVC_EX' Occasional, Frequent, or Pervasive (some areas have oVC_EX > oVC_PT)
                if row[4] > 0:
                    row[1] = 'Potential Reservoir or Landuse Conversion'
                else:    
                    row[1] = 'Naturally Vegetation Limited'    
            # 'iGeo_Slope' > 23%
            elif row[7] > 0.23:
               row[1] = 'Slope Limited'
            # 'oCC_EX' None (Primary focus of this layer is the places that can't support dams now... so why?)
            elif row[6] <= 0:
                    # 'oVC_EX' Rare, Occasional, Frequent, or Pervasive (i.e. its not currently veg limited)
                    if row[4] > 0:
                        row[1] = 'Stream Power Limited'                    
                    # 'oVC_EX' None 
                    else:
                        row[1] = 'Anthropogenically Limited'
            else:
                row[1] = 'Dam Building Possible'
            cursor.updateRow(row)

    # 'oPBRC_CR' (Conservation & Restoration Opportunties)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            # 'oPBRC_UI' Negligible or Minor
            if row[0] == 'Negligible' or row[0] == 'Minor':
                # 'oCC_EX' Frequent or Pervasive
                # 'mCC_HisDep' <= 3
                if row[6] >= 5 and row[8] <= 3:
                    row[2] = 'Easiest - Low-Hanging Fruit'
                # 'oCC_EX' Occasional, Frequent, or Pervasive
                # 'oCC_PT' Frequent or Pervasive
                # 'mCC_HisDep' <= 3
                # 'iPC_VLowLU'(i.e., Natural) > 75
                # 'iPC_HighLU' (i.e., Developed) < 10
                elif row[6] > 1 and row[8] <= 3 and row[5] >= 5 and row[9] > 75 and row[10] < 10:
                    row[2] = 'Straight Forward - Quick Return'
                # 'oCC_EX' Rare or Occasional
                # 'oCC_PT' Frequent or Pervasive
                # 'iPC_VLowLU'(i.e., Natural) > 75
                # 'iPC_HighLU' (i.e., Developed) < 10
                elif row[6] > 0 and row[6] < 5 and row[5] >= 5 and row[9] > 75 and row[10] < 10:
                    row[2] = 'Strategic - Long-Term Investment'
                else:
                    row[2] = 'NA'
            else:
                row[2] = 'NA'
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
