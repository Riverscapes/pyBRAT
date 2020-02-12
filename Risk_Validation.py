# -------------------------------------------------------------------------------
# Name:        BRAT Beaver Dam Risk Validation
# Purpose:     Tests the output of BRAT against a shape file of known conflict areas
#
# Author:      Maggie Hallerud
#
# Created:     02/2020
# -------------------------------------------------------------------------------

from SupportingFunctions import write_xml_element_with_path, find_relative_path, find_folder, \
    make_folder, find_available_num_suffix, find_available_num_prefix, make_layer
import os
import arcpy
# import matplotlib as mpl # for plot code
# mpl.use('Agg')
# import matplotlib.pyplot as plt
import scipy.stats as stat
import numpy as np
# import glob
import XMLBuilder
reload(XMLBuilder)
XMLBuilder = XMLBuilder.XMLBuilder


def main(in_network, output_name, conflict_points, da_threshold=None):
    """
    The main function
    :param in_network: The output of BRAT constraints/opportunities model (a polyline shapefile)
    :param conflict_points: A shapefile with points of known beaver dam-human conflict incidents
    :param output_name: The name of the output shape file
    :param da_threshold: Drainage area at which stream is presumably too large for dam building
    :return:
    """
    if da_threshold == "None":
        da_threshold = None

    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = 'in_memory'

    proj_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(in_network))))
    if conflict_points:
        conflict_points = copy_points_to_inputs(proj_path, conflict_points, in_network)

    if output_name.endswith('.shp'):
        output_network = os.path.join(os.path.dirname(in_network), output_name)
    else:
        output_network = os.path.join(os.path.dirname(in_network), output_name + ".shp")
    arcpy.Delete_management(output_network)
        
    # remove Join_Count if already present in conservation restoration output
    fields = [f.name for f in arcpy.ListFields(in_network)]
    if 'Join_Count' in fields:
        arcpy.DeleteField_management(in_network, 'Join_Count')
        
    new_fields = ['Conf_Ct', 'Conf_Dens', 'ConfCategr']
    input_fields = ['SHAPE@LENGTH', 'iGeo_DA']

    arcpy.AddMessage("Adding fields from known points of conflict...")
    set_conflict_attributes(in_network, output_network, conflict_points,
                           new_fields + ['Join_Count'] + input_fields, new_fields, da_threshold)

    if conflict_points:
        clean_up_fields(in_network, output_network, new_fields)

    write_xml(proj_path, in_network, output_network)

    #make_layers(output_network, conflict_points)
    make_electivity_table(output_network)


def copy_points_to_inputs(proj_path, conflict_points, in_network):
    """
    If the given points are not in the inputs,
    :param proj_path: The path to the project root
    :param conflict_points: The path to known points of beaver dam-human conflict
    :param in_network: the input Conservation Restoration Network
    :return: Filepath to points in inputs folder
    """
    if proj_path in conflict_points:
        # The points input is already in our project folder, so we don't need to copy it over
        return

    inputs_folder = find_folder(proj_path, "Inputs")
    conflict_pts_folder = find_folder(inputs_folder, "*[0-9]*_ConflictPoints")
    if conflict_pts_folder is None:
        conflict_pts_folder = make_folder(inputs_folder, find_available_num_prefix(inputs_folder) + "_ConflictPoints")
    new_pts_folder = make_folder(conflict_pts_folder, "Conflict_Points_" + find_available_num_suffix(conflict_pts_folder))
    new_conflict_path = os.path.join(new_pts_folder, os.path.basename(conflict_points))
    coord_sys = arcpy.Describe(in_network).spatialReference

    arcpy.Project_management(conflict_points, new_conflict_path, coord_sys)

    return new_conflict_path


def set_conflict_attributes(brat_output, output_path, conflict_points, req_fields, new_fields, da_threshold):
    """
    Sets all the dam info and updates the output file with that data
    :param brat_output: The polyline we're basing everything on
    :param output_path: The polyline shapefile with BRAT output
    :param conflict_points: The points shapefile of known points of beaver dam-human conflict
    :param req_fields: The fields needed to calculate new fields
    :param new_fields: Fields to add to the network
    :param da_threshold:
    :return: Drainage area at which stream is presumably too large for dam building
    """
    # snap points within 5 meters to network if above DA threshold, otherwise snap points within 60 meters
    if da_threshold:
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(brat_output)))), 'Temp')
        tmp_above_threshold = arcpy.MakeFeatureLayer_management(brat_output, 'tmp_above_threshold')
        above_threshold_shp = os.path.join(temp_dir, 'tmp_above_da_threshold.shp')
        tmp_below_threshold = arcpy.MakeFeatureLayer_management(brat_output, 'tmp_below_threshold')
        below_threshold_shp = os.path.join(temp_dir, 'tmp_below_da_threshold.shp')
        quer_above = """"{}" >= {}""".format('iGeo_DA', 65)
        quer_below = """"{}" < {}""".format('iGeo_DA', 65)
        arcpy.SelectLayerByAttribute_management(tmp_above_threshold, 'NEW_SELECTION', quer_above)
        arcpy.CopyFeatures_management(tmp_above_threshold, above_threshold_shp)
        arcpy.SelectLayerByAttribute_management(tmp_below_threshold, 'NEW_SELECTION', quer_below)
        arcpy.CopyFeatures_management(tmp_below_threshold, below_threshold_shp)
        arcpy.Snap_edit(conflict_points, [[above_threshold_shp, 'EDGE', '5 Meters']])
        arcpy.Snap_edit(conflict_points, [[below_threshold_shp, 'EDGE', '60 Meters']])
    # snap all points within 60 meters to network if no DA threshold provided
    else:
        arcpy.Snap_edit(conflict_points, [[brat_output, 'EDGE', '60 Meters']])

    # should select all points snapped to network
    arcpy.SpatialJoin_analysis(brat_output, conflict_points, output_path,
                               join_operation='JOIN_ONE_TO_ONE', join_type='KEEP_ALL', match_option='INTERSECT')

    # add new fields to network
    add_fields(output_path, new_fields)

    # calculate new field values
    with arcpy.da.UpdateCursor(output_path, req_fields) as cursor:
        for row in cursor:
            join_ct = row[-3]        # third to last attribute
            seg_length = row[-2]   # second to last attribute
            if seg_length is None:
                seg_length = 0
            igeo_da = row[-1]       # last attribute

            # Conf_Ct: set equal to join count from known conflict points
            row[0] = join_ct
            # Conf_Dens: calculate density of known conflict incidents
            row[1] = join_ct / seg_length * 1000
            # ConfCategr: categories relating to conflict frequency along reach
            if row[0] == 1:
                row[2] = "No Conflict"
            elif row[1] == 1:
                row[2] = "One incident"
            else:
                row[2] = "Multiple incidents"

            cursor.updateRow(row)

    arcpy.DeleteField_management(output_path, ["Join_Count", "TARGET_FID"])

    add_snapped_attribute(conflict_points, brat_output)


def add_snapped_attribute(conflict_points, brat_output):
    """ Adds attribute to points indicating whether point was snapped to network, and therefore used in the validation
    : param conflict_points: Shapefile of snapped known points of beaver dam-human conflict
    : param brat_output: Path to network with BRAT constraints/opportunities results
    : return:
    """
    out_pts = os.path.join(os.path.dirname(conflict_points), 'ConflictPoints_Snapped.shp')
    arcpy.SpatialJoin_analysis(conflict_points, brat_output, out_pts,
                               join_operation='JOIN_ONE_TO_ONE', join_type='KEEP_ALL', match_option='INTERSECT')
    arcpy.AddField_management(out_pts, 'Snapped', 'TEXT')
    with arcpy.da.UpdateCursor(out_pts, ['Join_Count', 'Snapped']) as cursor:
        for row in cursor:
            if row[0] > 0:
                row[1] = 'Snapped to network'
            else:
                row[1] = 'Not snapped to network'
            cursor.updateRow(row)
    # clean up points fields
    conflict_fields = [f.name for f in arcpy.ListFields(conflict_points)]
    conflict_fields.append('Snapped')
    out_fields = [f.name for f in arcpy.ListFields(out_pts)]
    for field in out_fields:
        if field not in conflict_fields:
            arcpy.DeleteField_management(out_pts, field)
    # only keep edited points shapefile and rename as original filename
    arcpy.Delete_management(conflict_points)
    arcpy.Rename_management(out_pts, conflict_points)


def add_fields(output_path, new_fields):
    """
    Adds the fields we want to our output shape file
    :param output_path: Our output shape file
    :param new_fields: All the fields we want to add
    :return:
    """
    text_fields = ['ConfCategr']
    for field in new_fields:
        if field in text_fields:
            arcpy.AddField_management(output_path, field, field_type="TEXT", field_length=50)
        else:  # we assume that the default is doubles
            arcpy.AddField_management(output_path, field, field_type="DOUBLE", field_precision=0, field_scale=0)


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


def make_layers(output_network, dams):
    """
    Makes the layers for the modified output
    :param output_network: The path to the network that we'll make a layer from
    :param dams: Filepath to dams in the project folder
    :return:
    """
    arcpy.AddMessage("Making layers...")
    analysis_folder = os.path.dirname(output_network)
    validation_folder_name = find_available_num_prefix(analysis_folder) + "_Validation"
    validation_folder = make_folder(analysis_folder, validation_folder_name)

    trib_code_folder = os.path.dirname(os.path.abspath(__file__))
    symbology_folder = os.path.join(trib_code_folder, 'BRATSymbology')

    dam_symbology = os.path.join(symbology_folder, "SurveyedBeaverDamLocations.lyr")
    historic_remaining_symbology = os.path.join(symbology_folder, "PercentofHistoricDamCapacityRemaining.lyr")
    pred_v_surv_symbology = os.path.join(symbology_folder, "PredictedDamCountvs.SurveyedDamCount.lyr")
    management_strategies_symbology = os.path.join(symbology_folder, "CurrentBeaverDamManagementStrategies.lyr")
    occupancy_symbology = os.path.join(symbology_folder, "PercentofExistingCapacityOccupiedbySurveyedDams.lyr")

    make_layer(validation_folder, output_network, "Percent of Historic Dam Capacity Remaining",
               historic_remaining_symbology, is_raster=False, symbology_field="mCC_EXvHPE")

    if dams is not None:
        make_layer(os.path.dirname(dams), dams, "Surveyed Beaver Dam Locations",
                   dam_symbology, is_raster=False, symbology_field="Snapped")
        make_layer(validation_folder, output_network, "Predicted Dam Count vs. Surveyed Dam Count",
                   pred_v_surv_symbology, is_raster=False, symbology_field="BRATvSurv")
        make_layer(validation_folder, output_network, "Current Beaver Dam Management Strategies",
                   management_strategies_symbology, is_raster=False, symbology_field="ConsVRest")
        make_layer(validation_folder, output_network, "Occupancy Rate of Surveyed Beaver Dams",
                   occupancy_symbology, is_raster=False, symbology_field="e_DamPcC")

        
def make_electivity_table(output_network):
    """
    Makes table with totals and electivity indices for modeled capacity categories
    (i.e., none, rare, occasional, frequent, pervasive)
    :param output_network: The stream network output by the BRAT model with fields added from capacity tools
    :return:
    """
    # convert network data to numpy table
    brat_table = arcpy.da.TableToNumPyArray(output_network,
                                            ['iGeo_Len', 'ConfCt', 'ConfDens', 'oPBRC_UI'],
                                            skip_nulls=True)
    tot_length = brat_table['iGeo_Len'].sum()
    tot_known_conflict = brat_table['ConfCt'].sum()
    avg_conf_dens = tot_known_conflict/(tot_length/1000)
    electivity_table = ['', 'm', 'km', '%', '# of incidents', 'incidents/km', '%']
    #add_electivity_category(brat_table, 'Negligible Risk', electivity_table, tot_length, tot_known_conflict)
    #add_electivity_category(brat_table, 'Minor Risk', electivity_table, tot_length, tot_known_conflict)
    #add_electivity_category(brat_table, 'Considerable Risk', electivity_table, tot_length, tot_known_conflict)
    #add_electivity_category(brat_table, 'Major Risk', electivity_table, tot_length, tot_known_conflict)
    add_electivity_category(brat_table, 'Negligible Risk', electivity_table, tot_length, tot_known_conflict)
    add_electivity_category(brat_table, 'Minor Risk', electivity_table, tot_length, tot_known_conflict)
    add_electivity_category(brat_table, 'Some Risk', electivity_table, tot_length, tot_known_conflict)
    add_electivity_category(brat_table, 'Considerable Risk', electivity_table, tot_length, tot_known_conflict)
    electivity_table.append(['Total', tot_length, tot_length/1000, 'NA', tot_known_conflict,
                             avg_conf_dens, 'NA'])

    # set up proper folder structure and save CSV there
    project_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(output_network))))
    summary_folder = make_folder(project_folder, "Summary_Products")
    tables_folder = make_folder(summary_folder, "SummaryTables")
    out_csv = os.path.join(tables_folder, 'Electivity_Index.csv')
    np.savetxt(out_csv, electivity_table, fmt='%s', delimiter=',',
               header="Segment Type, Stream Length, Stream Length,"
                      " % of Drainage Network, Known Conflict,"
                      " Average Incident Density, % of Incidents")


def add_electivity_category(brat_table, category, output_table, tot_length, tot_known_conflict):
    """
    Calculates values for each modeled capacity category and adds to output table
    :param brat_table: The output BRAT Table
    :param category: The oCC category to add
    :param output_table: The table to output data to
    :param tot_length: The total length of the network
    :param tot_known_conflict: The total number of known conflicts in the network
    :return:
    """
    cat_tbl = brat_table[brat_table['oPBRC_UI'] == category]
    length = cat_tbl['iGeo_Len'].sum()
    length_km = length/1000
    network_prop = 100*cat_tbl['iGeo_Len'].sum()/tot_length
    conf_pts = cat_tbl['Conf_Ct'].sum()
    conf_dens = pts/length_km
    brat_dens = brat_cc/length_km
    prop_conf = 100*conf_pts/tot_known_conflict
    #electivity = (surv_dams/tot_surv_dams)/(network_prop/100)
    output_table.append([category, length, length_km, network_prop, conf_pts,
                         conf_dens, prop_conf])


def write_xml(proj_path, in_network, out_network):
    """
    Writes relevant data into the XML
    :param proj_path:  The file path to the BRAT project folder
    :param in_network: The input Conservation Restoration network
    :param out_network: The newly created Data Validation network
    :param plot_name: The file path to the created plot
    :return:
    """
    xml_file_path = os.path.join(proj_path, "project.rs.xml")

    if not os.path.exists(xml_file_path):
        arcpy.AddWarning("XML file not found. Could not update XML file")
        return

    xml_file = XMLBuilder(xml_file_path)
    in_network_rel_path = find_relative_path(in_network, proj_path)

    path_element = xml_file.find_by_text(in_network_rel_path)
    analysis_element = xml_file.find_element_parent(xml_file.find_element_parent(path_element))

    write_xml_element_with_path(xml_file, analysis_element, "Vector", "BRAT Risk Validation", out_network, proj_path)

    xml_file.write()


if __name__ == "__main__":
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3],
         sys.argv[4])
