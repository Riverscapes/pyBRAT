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
import XMLBuilder
reload(XMLBuilder)
XMLBuilder = XMLBuilder.XMLBuilder
from SupportingFunctions import write_xml_element_with_path, find_relative_path


def main(in_network, dams, output_name):
    """
    The main function
    :param in_network: The output of BRAT (a polyline shapefile)
    :param dams: A shapefile containing a point for each dam
    :param output_name: The name of the output shape file
    :return:
    """
    arcpy.env.overwriteOutput = True

    copy_dams_to_inputs(dams)

    if output_name.endswith('.shp'):
        output_network = os.path.join(os.path.dirname(in_network), output_name)
    else:
        output_network = os.path.join(os.path.dirname(in_network), output_name + ".shp")
    arcpy.Delete_management(output_network)

    dam_fields = ['e_DamCt', 'e_DamDens', 'e_DamPcC']
    other_fields = ['Ex_Categor', 'Pt_Categor', 'mCC_EXtoPT']
    new_fields = dam_fields + other_fields

    input_fields = ['SHAPE@LENGTH', 'oCC_EX', 'oCC_PT']

    if dams:
        arcpy.AddMessage("Adding fields that need dam input...")
        set_dam_attributes(in_network, output_network, dams, dam_fields + ['Join_Count'] + input_fields, new_fields)
    else:
        arcpy.CopyFeatures_management(in_network, output_network)
        add_fields(output_network, other_fields)

    arcpy.AddMessage("Adding fields that don't need dam input...")
    set_other_attributes(output_network, other_fields + input_fields)

    if dams:
        clean_up_fields(in_network, output_network, new_fields)

    write_xml(in_network, output_network)


def copy_dams_to_inputs(dams):
    """
    
    :param dams:
    :return:
    """


def set_dam_attributes(brat_output, output_path, dams, req_fields, new_fields):
    """
    Sets all the dam info and updates the output file with that data
    :param brat_output: The polyline we're basing our stuff off of
    :param output_path: The polyline shapefile with BRAT output
    :param dams: The points shapefile of observed dams
    :param damFields: The fields we want to update for dam attributes
    :return:
    """
    arcpy.Snap_edit(dams, [[brat_output, 'EDGE', '30 Meters']])
    arcpy.SpatialJoin_analysis(brat_output,
                               dams,
                               output_path,
                               join_operation='JOIN_ONE_TO_ONE',
                               join_type='KEEP_ALL',
                               match_option='INTERSECT')
    add_fields(output_path, new_fields)

    with arcpy.da.UpdateCursor(output_path, req_fields) as cursor:
        for row in cursor:
            dam_num = row[-4]        # fourth to last attribute
            seg_length = row[-3]   # third to last attribute
            if seg_length is None:
                seg_length = 0
            oCC_EX = row[-2]        # second to last attribute
            oCC_PT = row[-1]        # last attribute

            row[0] = dam_num
            row[1] = dam_num / seg_length * 1000
            if oCC_PT == 0:
                row[2] = 0
            else:
                row[2] = dam_num / oCC_PT

            cursor.updateRow(row)

    arcpy.DeleteField_management(output_path, ["Join_Count", "TARGET_FID"])



def add_fields(output_path, new_fields):
    """
    Adds the fields we want to our output shape file
    :param output_path: Our output shape file
    :param new_fields: All the fields we want to add
    :return:
    """
    text_fields = ['Ex_Categor', 'Pt_Categor']
    for field in new_fields:
        if field in text_fields:
            arcpy.AddField_management(output_path, field, field_type="TEXT", field_length=50)
        else: # we assume that the default is doubles
            arcpy.AddField_management(output_path, field, field_type="DOUBLE", field_precision=0, field_scale=0)


def set_other_attributes(output_path, fields):
    """
    Sets the attributes of all other things we want to do
    :param output_path: The polyline shapefile with BRAT output
    :param fields: The fields we want to update
    :return:
    """
    with arcpy.da.UpdateCursor(output_path, fields) as cursor:
        for row in cursor:
            seg_length = row[-3] # third to last attribute
            if seg_length is None:
                seg_length = 0
            oCC_EX = row[-2] # second to last attribute
            oCC_PT = row[-1] # last attribute

            # Handles Ex_Categor
            row[0] = handle_category(oCC_EX)

            # Handles Pt_Categor
            row[1] = handle_category(oCC_PT)

            # Handles mCC_EXtoPT
            if oCC_PT != 0:
                row[4] = oCC_EX / oCC_PT
            else:
                row[4] = 0

            cursor.updateRow(row)


def handle_category(oCC_variable):
    """
    Returns a string based on the oCC value given to it
    :param oCC_variable: A number
    :return: String
    """
    if oCC_variable == 0:
        return "None"
    elif 0 < oCC_variable <= 1:
        return "Rare"
    elif 1 < oCC_variable <= 5:
        return "Occasional"
    elif 5 < oCC_variable <= 15:
        return "Frequent"
    elif 15 < oCC_variable <= 40:
        return "Pervasive"
    else:
        return "UNDEFINED"


def clean_up_fields(brat_network, out_network, new_fields):
    """
    Removes unnecessary fields
    :param brat_network: The original, unmodified stream network
    :param out_network: The output network
    :param new_fields: All the fields we added
    :return:
    """
    original_fields = [field.baseName for field in arcpy.ListFields(brat_network)]
    desired_fields = original_fields + new_fields
    output_fields = [field.baseName for field in arcpy.ListFields(out_network)]

    remove_fields = []
    for field in output_fields:
        if field not in desired_fields:
            remove_fields.append(field)

    if len(remove_fields) > 0:
        arcpy.DeleteField_management(out_network, remove_fields)


def write_xml(in_network, out_network):
    proj_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(in_network))))

    xml_file_path = os.path.join(proj_path, "project.rs.xml")
    xml_file = XMLBuilder(xml_file_path)
    in_network_rel_path = find_relative_path(in_network, proj_path)

    path_element = xml_file.find_by_text(in_network_rel_path)
    analysis_element = xml_file.find_element_parent(xml_file.find_element_parent(path_element))

    write_xml_element_with_path(xml_file, analysis_element, "Vector", "BRAT Summary Report", out_network, proj_path)

    xml_file.write()

