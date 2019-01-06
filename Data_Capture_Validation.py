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
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import scipy.stats as stat
import numpy as np
import XMLBuilder
reload(XMLBuilder)
XMLBuilder = XMLBuilder.XMLBuilder
from SupportingFunctions import write_xml_element_with_path, find_relative_path, find_folder, make_folder, find_available_num_suffix

def main(in_network, dams, output_name):
    """
    The main function
    :param in_network: The output of BRAT (a polyline shapefile)
    :param dams: A shapefile containing a point for each dam
    :param output_name: The name of the output shape file
    :return:
    """
    arcpy.env.overwriteOutput = True

    proj_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(in_network))))
    copy_dams_to_inputs(proj_path, dams)

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

    if dams:
        plot_name = observed_v_predicted_plot(output_network)

    write_xml(proj_path, in_network, output_network, plot_name)


def copy_dams_to_inputs(proj_path, dams):
    """
    If the given dams are not in the inputs,
    :param proj_path: The path to the project root
    :param dams: The path to the given dams
    :return:
    """
    if proj_path in dams:
        # The dams input is already in our project folder, so we don't need to copy it over
        return

    inputs_folder = find_folder(proj_path, "Inputs")
    beaver_dams_folder = find_folder(inputs_folder, "BeaverDams")
    if beaver_dams_folder is None:
        beaver_dams_folder = make_folder(inputs_folder, "BeaverDams")

    new_dam_folder = make_folder(beaver_dams_folder, "Beaver_Dam_" + find_available_num_suffix(beaver_dams_folder))
    new_dam_path = os.path.join(new_dam_folder, os.path.basename(dams))

    arcpy.Copy_management(dams, new_dam_path)


def set_dam_attributes(brat_output, output_path, dams, req_fields, new_fields):
    """
    Sets all the dam info and updates the output file with that data
    :param brat_output: The polyline we're basing our stuff off of
    :param output_path: The polyline shapefile with BRAT output
    :param dams: The points shapefile of observed dams
    :param damFields: The fields we want to update for dam attributes
    :return:
    """
    arcpy.Snap_edit(dams, [[brat_output, 'EDGE', '60 Meters']])
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



def observed_v_predicted_plot(output_network):
    x, y = clean_values(output_network)
    # set up plot
    fig = plt.figure()
    fig.add_axes()
    ax = fig.add_subplot(111)
    ax.set(title='Predicted vs. Observed Dam Counts (per reach)',
               xlabel='Predicted Number of Dams',
               ylabel='Observed Number of Dams')
    # set axis range
    if max(x) > max(y):
        ax.set_xlim(0, round(max(x)+2), 1)
        ax.set_ylim(0, round(max(x)+2), 1)
    else:
        ax.set_xlim(0, round(max(y)+2), 1)
        ax.set_ylim(0, round(max(y)+2), 1)
    # plot data points, regression line, 1:1 reference
    plot_points(x, y, ax)
    plot_regression(x, y, ax)
    ax.plot([0, 10], [0, 10], color='blue', linewidth=1.5, linestyle=":", label='Line of Perfect Agreement')
    # add legend
    legend = plt.legend(loc="upper left", bbox_to_anchor=(1,1))
    # save plot
    analysis_folder = os.path.join(os.path.dirname(os.path.dirname(output_network)), "02_Analyses")
    comparison_folder = find_folder(analysis_folder, "Inter-Comparison")
    if comparison_folder is None:
        comparison_folder = make_folder(analysis_folder, "03_Inter-Comparison")
    new_comparison_folder = make_folder(comparison_folder, "Inter-Comparison" + find_available_num_suffix(comparison_folder))
    plot_name = os.path.join(new_comparison_folder, "Predicted_vs_Expected_Plot.png")
    plt.savefig(plot_name, bbox_extra_artists=(legend,), bbox_inches='tight')
    return plot_name



def clean_values(output_network):
    # pull e_DamCt (observed) and oCC_EX (predicted) from output network
    mCC_EX_CT = arcpy.da.FeatureClassToNumPyArray(output_network, ['mCC_EX_CT']).astype(np.float)
    e_DamCt = arcpy.da.FeatureClassToNumPyArray(output_network, ['e_DamCt']).astype(np.float)
    # pull out none values
    x = mCC_EX_CT[np.isnan(e_DamCt)==False]
    y = e_DamCt[np.isnan(e_DamCt)==False]
    # pull out observed values of zero
    X1 = x[np.equal(y, 0)==False]
    Y1 = y[np.equal(y, 0)==False]
    return X1, Y1



def plot_points(x, y, axis):
    # generate some random jitter between 0 and 1
    jitter = (np.random.rand(*x.shape)-0.5)/x.std()
    # plot points with predicted dams < observed dams in red
    red_x = x[np.greater(y, x)== True] 
    red_y = y[np.greater(y, x)== True]
    jitter_red = jitter[np.greater(y, x)==True]
    jitter_red_x = np.add(red_x, jitter_red)
    jitter_red_y = np.add(red_y, jitter_red)
    axis.scatter(jitter_red_x, jitter_red_y, color="red", label = "BRAT Underestimate")
    # plot points with expected dams >= observed dams in blue
    blue_x = x[np.greater_equal(x, y)== True]
    blue_y = y[np.greater_equal(x, y)== True]
    jitter_blue = jitter[np.greater_equal(x, y)==True]
    jitter_blue_x = np.add(blue_x, jitter_blue)
    jitter_blue_y = np.add(blue_y, jitter_blue)
    axis.scatter(jitter_blue_x, jitter_blue_y, color="blue", label="BRAT Accurate")



def plot_regression(x, y, axis):
    # calculate regression equation of e_DamCt ~ mCC_EX_CT and assign to variable
    regression = stat.linregress(x, y)
    model_x = np.arange(0.0, round(max(x))+2, 0.1)
    model_y = regression.slope * model_x + regression.intercept
    # plot regression line
    axis.plot(model_x, model_y,  color='black', linewidth=2.0, linestyle='-', label='Regression line')
    # calculate prediction intervals and plot as shaded areas
    n = len(x)
    error = stat.t.ppf(1-0.025, n-2) * regression.stderr
    upper_CI = model_y + error
    lower_CI = model_y - error
    axis.fill_between(model_x, y1=upper_CI, y2=lower_CI, facecolor='red', alpha=0.3, label = "95% Confidence Interval")
    # in-plot legend
    axis.legend(loc='best', frameon=False)



def write_xml(proj_path, in_network, out_network, plot_name):
    xml_file_path = os.path.join(proj_path, "project.rs.xml")

    if not os.path.exists(xml_file_path):
        arcpy.AddWarning("XML file not found. Could not update XML file")
        return

    xml_file = XMLBuilder(xml_file_path)
    in_network_rel_path = find_relative_path(in_network, proj_path)

    path_element = xml_file.find_by_text(in_network_rel_path)
    analysis_element = xml_file.find_element_parent(xml_file.find_element_parent(path_element))

    write_xml_element_with_path(xml_file, analysis_element, "Vector", "BRAT Summary Report", out_network, proj_path)
    write_xml_element_with_path(xml_file, analysis_element, "Plot", "Observed vs. Predicted Plot", plot_name, proj_path)

    xml_file.write()


