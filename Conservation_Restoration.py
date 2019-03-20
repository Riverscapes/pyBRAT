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
    arcpy.AddField_management(out_network, "DamStrat", "TEXT", "", "", 40)

    # use old historic capacity field names if new ones not in combined capacity output
    if 'oVC_PT' in fields:
        hist_veg_field_name = 'oVC_PT'
    else:
        hist_veg_field_name = 'oVC_HPE'

    if 'oCC_PT' in fields:
        hist_dams_field_name = 'oCC_PT'
    else:
        hist_dams_field_name = 'oCC_HPE'
    
    fields = ['oPBRC_UI', 'oPBRC_UD', 'oPBRC_CR', hist_veg_field_name, 'oVC_EX', hist_dams_field_name, 'oCC_EX', 'iGeo_Slope', 'mCC_HisDep',
              'iPC_VLowLU', 'iPC_HighLU', 'oPC_Dist', 'iPC_LU', 'iHyd_SPLow', 'iHyd_SP2', 'DamStrat', 'iPC_RoadX']

    # 'oPBRC_UI' (Areas beavers can build dams, but could be undesireable impacts)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:

            curr_dams = row[6]
            infrastructure_dist = row[11]
            landuse = row[12]

            if curr_dams <= 0:
                # if capacity is none risk is negligible
                row[0] = "Negligible Risk"
            else:
                # if infrastructure within 30 m or land use is high
                # if capacity is frequent or pervasive risk is considerable
                # if capaicty is rare or ocassional risk is some
                if infrastructure_dist <= 30 or landuse >= 0.66:
                    if curr_dams >= 5.0:
                        row[0] = "Considerable Risk"
                    else:
                        row[0] = "Some Risk"
                # if infrastructure within 30 to 100 m
                # if capacity is frequent or pervasive risk is some
                # if capaicty is rare or ocassional risk is minor
                elif infrastructure_dist <= 100:
                    if curr_dams >= 5.0:
                        row[0] = "Some Risk"
                    else:
                        row[0] = "Minor Risk"
                # if infrastructure within 100 to 300 m or land use is 0.33 to 0.66 risk is minor
                elif infrastructure_dist <= 300 or landuse >= 0.33:
                    row[0] = "Minor Risk"
                else:
                    row[0] = "Negligible Risk"

            cursor.updateRow(row)

    # 'oPBRC_UD' (Areas beavers can't build dams and why)
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:

            hist_veg = row[3]
            curr_veg = row[4]
            curr_dams = row[6]
            slope = row[7]
            landuse = row[12]
            splow = row[13]
            sp2 = row[14]

            # First deal with vegetation limitations
            # Find places historically veg limited first ('oVC_HPE' None)
            if hist_veg <= 0:
                # 'oVC_EX' Occasional, Frequent, or Pervasive (some areas have oVC_EX > oVC_HPE)
                if curr_veg > 0:
                    row[1] = 'Potential Reservoir or Landuse Conversion'
                else:    
                    row[1] = 'Naturally Vegetation Limited'    
            # 'iGeo_Slope' > 23%
            elif slope > 0.23:
               row[1] = 'Slope Limited'
            # 'oCC_EX' None (Primary focus of this layer is the places that can't support dams now... so why?)
            elif curr_dams <= 0:
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
            hist_dams = row[5]
            curr_dams = row[6]
            mCC_HisDep = row[8]
            iPC_VLowLU = row[9]
            iPC_HighLU = row[10]
            landuse = row[12]

            # default category is 'Other'
            row[2] = 'NA'

            # if it fits one of these, it'll be changed to that
            if opbrc_ui == 'Negligible Risk' or opbrc_ui == 'Minor Risk':
                if mCC_HisDep >= 3:
                    if curr_dams >= 5:
                        row[2] = "Easiest - Low-Hanging Fruit"
                    elif hist_dams > 5 and curr_dams > 1 and (landuse < 10 or landuse > 75):
                        row[2] = "Straight Forward - Quick Return"
                elif hist_dams >= 5 and curr_dams < 1 and (landuse < 10 or landuse > 75):
                    row[2] = "Strategic - Long-Term Investment"

            cursor.updateRow(row)

    # 'newField'  The test field for TNC
    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            # 'oPBRC_UI' Negligible Risk or Minor Risk
            opbrc_ui = row[0]
            hist_veg = row[3]
            curr_veg = row[4]
            hist_dams = row[5]
            curr_dams = row[6]
            slope = row[7]
            hist_dep = row[8]
            iPC_VLowLU = row[9]
            iPC_HighLU = row[10]
            infrastructure_dist = row[11]
            landuse = row[12]
            stream_power = row[14]
            road_crossings = row[16]

            veg_departure = hist_dams - curr_dams
            urban = landuse > 0.66
            ag = 0.33 < landuse <= 0.66
            no_urban = not urban
            hist_to_curr_dams_ratio = 9999
            if curr_dams != 0:
                hist_to_curr_dams_ratio = float(hist_dams) / float(curr_dams)

            # default category is 'Other'
            row[15] = 'Other'

            if hist_to_curr_dams_ratio > 1:
                if hist_dams >= 5:
                    if curr_dams > 1:
                        if urban:
                            row[15] = "Living with Beaver Solutions - urban"
                        if ag:
                            row[15] = "Living with Beaver Solutions - ag"
                        if road_crossings <= 30:
                            row[15] = "Living with Beaver Solutions - road crossings"
                    if 5 <= curr_dams < 15 and no_urban:
                        if veg_departure >= 5:
                            row[15] = "High Restoration Potential - Veg First"
                        else:
                            row[15] = "High Restoration Potential"
                    if 1 <= curr_dams < 5 and no_urban:
                        if veg_departure >= 5:
                            row[15] = "Medium Restoration Potential - Veg First"
                        else:
                            row[15] = "Medium Restoration Potential"
                if 1 <= hist_dams < 5 and 1 <= curr_dams < 5 and no_urban:
                    if veg_departure >= 5:
                        row[15] = "Low Restoration Potential - Veg First"
                    else:
                        row[15] = "Low Restoration Potential"
            if hist_dams >= 15 and curr_dams >= 15 and no_urban and infrastructure_dist > 100:
                row[15] = "Relocation and Conservation"




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
