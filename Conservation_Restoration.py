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
from SupportingFunctions import make_layer, make_folder, find_available_num_prefix, find_relative_path, write_xml_element_with_path
import XMLBuilder
reload(XMLBuilder)
XMLBuilder = XMLBuilder.XMLBuilder


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

    arcpy.AddField_management(out_network, "oPBRC_UI", "TEXT", "", "", 30)
    arcpy.AddField_management(out_network, "oPBRC_UD", "TEXT", "", "", 30)
    arcpy.AddField_management(out_network, "oPBRC_CR", "TEXT", "", "", 40)

    fields = ['oPBRC_UI', 'oPBRC_UD', 'oPBRC_CR', 'oVC_HPE', 'oVC_EX', 'oCC_HPE', 'oCC_EX', 'iGeo_Slope', 'mCC_HisDep', 'iPC_VLowLU', 'iPC_HighLU', 'oPC_Dist', 'iPC_LU']

    # 'oPBRC_UI' (Areas beavers can build dams, but could be undesireable impacts)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            occ_ex = row[6]
            opc_dist = row[11]
            ipc_lu = row[12]

            if (opc_dist < 30 or ipc_lu > 0.6) and occ_ex >= 15:
                row[0] = "Considerable Risk"
            elif (opc_dist < 100 or ipc_lu > 0.6) and (5 <= occ_ex < 15):
                row[0] = "Some Risk"
            elif (opc_dist < 300 or ipc_lu > 0.3) and (0 < occ_ex < 5):
                row[0] = "Minor Risk"
            else:
                row[0] = "Negligible Risk"

            cursor.updateRow(row)
            
            
    # 'oPBRC_UD' (Areas beavers can't build dams and why)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            # First deal with vegetation limitations
            # oVC_HPE' None - Find places historically veg limited first.
            if row[3] <= 0:
                 # 'oVC_EX' Occasional, Frequent, or Pervasive (some areas have oVC_EX > oVC_HPE)
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
            # 'oPBRC_UI' Negligible Risk or Minor Risk
            if row[0] == 'Negligible Risk' or row[0] == 'Minor Risk':
                # 'oCC_EX' Frequent or Pervasive
                # 'mCC_HisDep' <= 3
                if row[6] >= 5 and row[8] <= 3:
                    row[2] = 'Easiest - Low-Hanging Fruit'
                # 'oCC_EX' Occasional, Frequent, or Pervasive
                # 'oCC_HPE' Frequent or Pervasive
                # 'mCC_HisDep' <= 3
                # 'iPC_VLowLU'(i.e., Natural) > 75
                # 'iPC_HighLU' (i.e., Developed) < 10
                elif row[6] > 1 and row[8] <= 3 and row[5] >= 5 and row[9] > 75 and row[10] < 10:
                    row[2] = 'Straight Forward - Quick Return'
                # 'oCC_EX' Rare or Occasional
                # 'oCC_HPE' Frequent or Pervasive
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

    write_xml(in_network, out_network)

    return out_network


def makeLayers(out_network):
    """
    Writes the layers
    :param out_network: The output network, which we want to make into a layer
    :return:
    """
    arcpy.AddMessage("Making layers...")
    analyses_folder = os.path.dirname(out_network)
    output_folder = make_folder(analyses_folder, find_available_num_prefix(analyses_folder) + "_Management")

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')
    management_zones_symbology = os.path.join(symbologyFolder, "Beaver_Management_Zones_v2.lyr")
    limitations_dams_symbology = os.path.join(symbologyFolder, "Unsuitable_Limited_Dam_Building_Opportunities.lyr")
    undesirable_dams_symbology = os.path.join(symbologyFolder, "Areas_Beavers_Can_Build_Dams_but_could_be_Undesirable.lyr")
    conservation_restoration_symbology = os.path.join(symbologyFolder, "Possible_Beaver_Dam_Conservation_Restoration_Opportunities.lyr")

    # make_layer(output_folder, out_network, "Beaver Management Zones", management_zones_symbology, is_raster=False)
    make_layer(output_folder, out_network, "Unsuitable or Limited Opportunities", limitations_dams_symbology, is_raster=False, symbology_field ='pPBRC_UD')
    make_layer(output_folder, out_network, "Risk of Undesirable Dams", undesirable_dams_symbology, is_raster=False, symbology_field ='pPBRC_UI')
    make_layer(output_folder, out_network, "Restoration or Conservation Opportunities", conservation_restoration_symbology, is_raster=False, symbology_field ='pPBRC_CR')

def write_xml(in_network, out_network):
    proj_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(in_network))))

    xml_file_path = os.path.join(proj_path, "project.rs.xml")

    if not os.path.exists(xml_file_path):
        arcpy.AddWarning("XML file not found. Could not update XML file")
        return

    xml_file = XMLBuilder(xml_file_path)
    in_network_rel_path = find_relative_path(in_network, proj_path)

    path_element = xml_file.find_by_text(in_network_rel_path)
    analysis_element = xml_file.find_element_parent(xml_file.find_element_parent(path_element))

    write_xml_element_with_path(xml_file, analysis_element, "Vector", "BRAT Conservation and Restoration Output", out_network, proj_path)

    xml_file.write()


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])
