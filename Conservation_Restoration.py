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

    # use old historic capacity field names if new ones not in combined capacity output
    if 'oVC_PT' in fields:
        ovc_hpe = 'oVC_PT'
    else:
        ovc_hpe = 'oVC_HPE'

    if 'oCC_PT' in fields:
        occ_hpe = 'oCC_PT'
    else:
        occ_hpe = 'oCC_HPE'
    
    fields = ['oPBRC_UI', 'oPBRC_UD', 'oPBRC_CR', ovc_hpe, 'oVC_EX', occ_hpe, 'oCC_EX', 'iGeo_Slope', 'mCC_HisDep', 'iPC_VLowLU', 'iPC_HighLU', 'oPC_Dist', 'iPC_LU', 'iHyd_SPLow', 'iHyd_SP2', 'iPC_Canal']

    # 'oPBRC_UI' (Areas beavers can build dams, but could be undesireable impacts)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:

            occ_ex = row[6]
            opc_dist = row[11]
            ipc_lu = row[12]
            ipc_canal = row[15]
            
            if occ_ex <= 0:
                # if capacity is none risk is negligible
                row[0] = "Negligible Risk"
            elif ipc_canal <=20:
                # if canals are within 20 meters (usually means canal is on the reach)
                row[0] = "Considerable Risk"
            else:
                # if infrastructure within 30 m or land use is high
                # if capacity is frequent or pervasive risk is considerable
                # if capaicty is rare or ocassional risk is some
                if opc_dist <= 30 or ipc_lu >= 0.66:
                    if occ_ex >= 5.0:
                        row[0] = "Considerable Risk"
                    else:
                        row[0] = "Some Risk"
                # if infrastructure within 30 to 100 m
                # if capacity is frequent or pervasive risk is some
                # if capaicty is rare or ocassional risk is minor
                elif opc_dist <= 100:
                    if occ_ex >= 5.0:
                        row[0] = "Some Risk"
                    else:
                        row[0] = "Minor Risk"
                # if infrastructure within 100 to 300 m or land use is 0.33 to 0.66 risk is minor
                elif opc_dist <= 300 or ipc_lu >= 0.33:
                    row[0] = "Minor Risk"
                else:
                    row[0] = "Negligible Risk"

            cursor.updateRow(row)

    # 'oPBRC_UD' (Areas beavers can't build dams and why)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:

            ovc_hpe = row[3]
            ovc_ex = row[4]
            occ_ex = row[6]
            slope = row[7]
            landuse = row[12]
            splow = row[13]
            sp2 = row[14]

            # First deal with vegetation limitations
            # Find places historically veg limited first ('oVC_HPE' None)
            if ovc_hpe <= 0:
                # 'oVC_EX' Occasional, Frequent, or Pervasive (some areas have oVC_EX > oVC_HPE)
                if ovc_ex > 0:
                    row[1] = 'Potential Reservoir or Landuse Conversion'
                else:    
                    row[1] = 'Naturally Vegetation Limited'    
            # 'iGeo_Slope' > 23%
            elif slope > 0.23:
               row[1] = 'Slope Limited'
            # 'oCC_EX' None (Primary focus of this layer is the places that can't support dams now... so why?)
            elif occ_ex <= 0:
                if landuse > 0.3:
                    row[1] = "Anthropogenically Limited"
                elif splow >= 190 or sp2 >= 2400:
                    row[1] = "Stream Power Limited"
                else:
                    row[1] = "...TBD..."
            else:
                row[1] = 'Dam Building Possible'

            cursor.updateRow(row)

    # 'oPBRC_CR' (Conservation & Restoration Opportunties)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            # 'oPBRC_UI' Negligible Risk or Minor Risk
            opbrc_ui = row[0]
            occ_hpe = row[5]
            occ_ex = row[6]
            mCC_HisDep = row[8]
            iPC_VLowLU = row[9]
            iPC_HighLU = row[10]
            if opbrc_ui == 'Negligible Risk' or opbrc_ui == 'Minor Risk':
                # 'oCC_EX' Frequent or Pervasive
                # 'mCC_HisDep' <= 3
                if occ_ex >= 5 and mCC_HisDep <= 3:
                    row[2] = 'Easiest - Low-Hanging Fruit'
                # 'oCC_EX' Occasional, Frequent, or Pervasive
                # 'oCC_HPE' Frequent or Pervasive
                # 'mCC_HisDep' <= 3
                # 'iPC_VLowLU'(i.e., Natural) > 75
                # 'iPC_HighLU' (i.e., Developed) < 10
                elif occ_ex > 1 and mCC_HisDep <= 3 and occ_hpe >= 5 and iPC_VLowLU > 75 and iPC_HighLU < 10:
                    row[2] = 'Straight Forward - Quick Return'
                # 'oCC_EX' Rare or Occasional
                # 'oCC_HPE' Frequent or Pervasive
                # 'iPC_VLowLU'(i.e., Natural) > 75
                # 'iPC_HighLU' (i.e., Developed) < 10
                elif occ_ex > 0 and occ_ex < 5 and occ_hpe >= 5 and iPC_VLowLU > 75 and iPC_HighLU < 10:
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
