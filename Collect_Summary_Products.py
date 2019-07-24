# -------------------------------------------------------------------------------
# Name:        Collect Summary Products
# Purpose:     Collects any *.ai, *.png, or *.pdf files and automatically copies them
#              into the proper structure
#
# Author:      Braden Anderson
#
# Created:     12/2018
# -------------------------------------------------------------------------------

import shutil
from SupportingFunctions import make_folder
from numpy import median, mean
import os
import xlsxwriter
import arcpy


def main(project_folder, stream_network, watershed_name, excel_file_name=None, dams_shapefile=None, output_folder=None):
    """
    Our main function
    :param project_folder: The BRAT Project that we want to collect the summary products for
    :param: stream_network: The BRAT output on which calculations will be based
    :param: watershed_name: Name of watershed data is based off
    :param: excel_file_name: Output file name
    :param: dams_shapefile: Shapefile of dam points corresponding with stream network provided
    :param: output_folder: Optional folder to save output table to
    :return: Excel workbook with sheets summarizing major BRAT outputs
    """
    if excel_file_name is None:
        excel_file_name = "BRAT_Summary_Tables"
    if not excel_file_name.endswith(".xlsx"):
        excel_file_name += ".xlsx"

    if output_folder:
        output_folder = output_folder
    else:
        summary_prods_folder = os.path.join(project_folder, "Summary_Products")
        create_folder_structure(project_folder, summary_prods_folder)
        output_folder = make_folder(summary_prods_folder, "SummaryTables")

    if (stream_network.count(';') > 0):
        stream_network = merge_networks(summary_prods_folder, stream_network)
    if dams_shapefile is not None:
        if (dams_shapefile.count(';') > 0):
            dams_shapefile = merge_dams(summary_prods_folder, dams_shapefile)

    fields = [f.name for f in arcpy.ListFields(stream_network)]
    create_excel_file(excel_file_name, stream_network, output_folder, watershed_name, fields, dams_shapefile)


def split_multi_inputs(multi_input_parameter):
    """
    Splits an ArcMap Toolbox Multi-Value parameter into a Python list object.
    ArcMap Multi-Value inputs are semi-colon delimited text strings.
    """
    try:
        # Remove single quotes
        multi_input_parameter = multi_input_parameter.replace("'", "")

        # split input tables by semicolon ";"
        return multi_input_parameter.split(";")
    except:
        raise Exception("Could not split multi-input")


def merge_networks(summary_prods_folder, stream_network):
    mergedFile = os.path.join(summary_prods_folder, "MergedNetwork.shp")
    toMerge = split_multi_inputs(stream_network)
    arcpy.CreateFeatureclass_management(summary_prods_folder, "MergedNetwork.shp", None, toMerge[0])
    arcpy.Append_management(toMerge, mergedFile, "NO_TEST")
    return mergedFile


def merge_dams(summary_prods_folder, dams_shapefiles):
    mergedFile = os.path.join(summary_prods_folder, "MergedDams.shp")
    toMerge = split_multi_inputs(dams_shapefiles)
    arcpy.CreateFeatureclass_management(summary_prods_folder, "MergedDams.shp", None, toMerge[0])
    arcpy.Append_management(toMerge, mergedFile, "NO_TEST")
    return mergedFile


def create_excel_file(excel_file_name, stream_network, summary_prods_folder, watershed_name, fields, dams_shapefile):
    workbook = xlsxwriter.Workbook(os.path.join(summary_prods_folder, excel_file_name))
    write_capacity_sheets(workbook, stream_network, watershed_name, fields, dams_shapefile)
    workbook.close()


def write_capacity_sheets(workbook, stream_network, watershed_name, fields, dams_shapefile):
    summary_worksheet = workbook.add_worksheet("Watershed Summary")
    write_summary_worksheet(summary_worksheet, stream_network, watershed_name, workbook, fields, dams_shapefile)
    if 'oCC_EX' in fields:
        density_correlations_worksheet = workbook.add_worksheet("Density Correlations")
        write_density_correlations_worksheet(density_correlations_worksheet, stream_network, watershed_name, workbook)
        exist_build_cap_worksheet = workbook.add_worksheet("Existing Dam Building Capacity")
        write_exist_build_cap_worksheet(exist_build_cap_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Existing dam building capacity worksheet could not be built because oCC_EX not in fields")
    if 'mCC_EX_CT' in fields:
        exist_complex_worksheet = workbook.add_worksheet("Existing Dam Complex Size")
        write_exist_complex_worksheet(exist_complex_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Existing dam complex size worksheet could not be built because mCC_EX_CT not in fields")
    if 'oCC_HPE' in fields:
        hist_build_cap_worksheet = workbook.add_worksheet("Historic Dam Building Capacity")
        write_hist_build_cap_worksheet(hist_build_cap_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Historic dam builiding capacity worksheet could not be built because oCC_HPE not in fields")
    if 'mCC_HPE_CT' in fields:
        hist_complex_worksheet = workbook.add_worksheet("Historic Dam Complex Size")
        write_hist_complex_worksheet(hist_complex_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Existing dam complex size worksheet could not be built because mCC_HPE_CT not in fields")
    if 'mCC_HPE_CT' in fields and 'mCC_EX_CT' in fields:
        hist_vs_exist_worksheet = workbook.add_worksheet("Existing vs. Historic Capacity")
        write_hist_vs_exist_worksheet(hist_vs_exist_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning(
            "Existing vs. Historic worksheet could not be built because mCC_EX_CT or mCC_HPE_CT not in fields")
    if 'oPBRC_CR' in fields:
        cons_rest_worksheet = workbook.add_worksheet("Conservation Restoration")
        write_conservation_restoration(cons_rest_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Conservation restoration worksheet could not be built because oPBRC_CR not in fields")
    if 'oPBRC_UD' in fields:
        unsuitable_worksheet = workbook.add_worksheet("Unsuitable or Limited")
        write_unsuitable_worksheet(unsuitable_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning(
            "Unsuitable/limited dam opportunities worksheet could not be built because oPBRC_UD not in fields")
    if 'oPBRC_UI' in fields:
        risk_worksheet = workbook.add_worksheet("Undesirable Dams")
        write_risk_worksheet(risk_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Risk worksheet could not be built because oPBRC_UI not in fields")
    if 'ConsVRest' in fields:
        strategies_worksheet = workbook.add_worksheet("Management Strategies")
        write_strategies_worksheet(strategies_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Strategies worksheet could not be built because ConsVRest not in fields")
    if 'mCC_EXvHPE' in fields:
        historic_remaining_worksheet = workbook.add_worksheet("% Historic Capacity Remaining")
        write_historic_remaining_worksheet(historic_remaining_worksheet, stream_network, watershed_name, workbook)
    if 'BRATvSurv' in fields:
        validation_worksheet = workbook.add_worksheet("Predicted vs. Surveyed")
        write_validation_worksheet(validation_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Predicted vs. surveyed worksheet could not be built because BRATvSurv not in fields")
    if 'e_DamCt' in fields:
        electivity_worksheet = workbook.add_worksheet("Electivity Index")
        write_electivity_worksheet(electivity_worksheet, stream_network, watershed_name, workbook)
    else:
        arcpy.AddWarning("Electivity index worksheet could not be built because e_DamCt not in fields")


# Maggie's code
def make_capacity_table(output_network, mcc_hpe):
    brat_table = arcpy.da.TableToNumPyArray(output_network,
                                            ['iGeo_Len', 'mCC_EX_CT', 'oCC_EX', 'ExCategor', 'oCC_HPE', 'mCC_HPE_CT',
                                             'HpeCategor'], skip_nulls=True)
    tot_length = brat_table['iGeo_Len'].sum()
    total_ex_capacity = brat_table['mCC_EX_CT'].sum()
    total_hpe_capacity = brat_table[mcc_hpe].sum()
    capacity_table = []

    ex_pervasive = add_capacity_category(brat_table, 'Existing', 'Pervasive', tot_length)
    # ex_frequent_pervasive = add_capacity_category(brat_table, 'Existing', 'Frequent-Pervasive', tot_length)
    ex_frequent = add_capacity_category(brat_table, 'Existing', 'Frequent', tot_length)
    # ex_occasional_frequent = add_capacity_category(brat_table, 'Existing', 'Occasional-Frequent', tot_length)
    ex_occasional = add_capacity_category(brat_table, 'Existing', 'Occasional', tot_length)
    # ex_rare_occasional = add_capacity_category(brat_table, 'Existing', 'Rare-Occasional', tot_length)
    ex_rare = add_capacity_category(brat_table, 'Existing', 'Rare', tot_length)
    # ex_none_rare = add_capacity_category(brat_table, 'Existing', 'None-Rare', tot_length)
    ex_none = add_capacity_category(brat_table, 'Existing', 'None', tot_length)

    hist_pervasive = add_capacity_category(brat_table, 'Historic', 'Pervasive', tot_length)
    # hist_frequent_pervasive = add_capacity_category(brat_table, 'Historic', 'Frequent-Pervasive', tot_length)
    hist_frequent = add_capacity_category(brat_table, 'Historic', 'Frequent', tot_length)
    # hist_occasional_frequent = add_capacity_category(brat_table, 'Historic', 'Occasional-Frequent', tot_length)
    hist_occasional = add_capacity_category(brat_table, 'Historic', 'Occasional', tot_length)
    # hist_rare_occasional = add_capacity_category(brat_table, 'Historic', 'Rare-Occasional', tot_length)
    hist_rare = add_capacity_category(brat_table, 'Historic', 'Rare', tot_length)
   #  hist_none_rare = add_capacity_category(brat_table, 'Historic', 'None-Rare', tot_length)
    hist_none = add_capacity_category(brat_table, 'Historic', 'None', tot_length)


# Maggie's code
def add_capacity_category(brat_table, type, category, tot_length):
    if type == 'Existing':
        cat_tbl = brat_table[brat_table['ExCategor'] == category]
    else:
        cat_tbl = brat_table[brat_table['HpeCategor'] == category]
    length = cat_tbl['iGeo_Len'].sum()
    length_km = length / 1000
    network_prop = 100 * length / tot_length
    est_dams = cat_tbl['mCC_EX_CT'].sum()
    return length, length_km, network_prop, est_dams


# Writing the side headers for complex size
def write_categories_complex(worksheet, watershed_name):
    column_sizeA = worksheet.set_column('A:A', column_calc(30, watershed_name))
    row = 2
    col = 0
    worksheet.write(row, col, "No Dams", column_sizeA)
    row += 1
    worksheet.write(row, col, "Single Dam")
    row += 1
    worksheet.write(row, col, "Small Complex (2-3 Dams)")
    row += 1
    worksheet.write(row, col, "Medium Complex (4-5 dams)")
    row += 1
    worksheet.write(row, col, "Large Complex (>5 dams)")
    row += 1
    worksheet.write(row, col, "Total")


# Writing the side headers for build capacity
def write_categories_build_cap(worksheet, watershed_name):
    column_sizeA = worksheet.set_column('A:A', column_calc(30, watershed_name))
    row = 2
    col = 0
    worksheet.write(row, col, "None: 0", column_sizeA)
    row += 1
    worksheet.write(row, col, "Rare: 0 - 1")
    row += 1
    worksheet.write(row, col, "Occasional: 1 - 5")
    row += 1
    worksheet.write(row, col, "Frequent: 5 - 15")
    row += 1
    worksheet.write(row, col, "Pervasive: 15 - 40")
    row += 1
    worksheet.write(row, col, "Total")


def write_categories_hist_vs_exist(worksheet, watershed_name):
    column_sizeA = worksheet.set_column('A:A', column_calc(30, watershed_name))
    row = 3
    col = 0
    worksheet.write(row, col, "None: 0", column_sizeA)
    row += 1
    worksheet.write(row, col, "Rare: 0 - 1")
    row += 1
    worksheet.write(row, col, "Occasional: 1 - 5")
    row += 1
    worksheet.write(row, col, "Frequent: 5 - 15")
    row += 1
    worksheet.write(row, col, "Pervasive: 15 - 40")
    row += 1
    worksheet.write(row, col, "Total")


# Writing the data into the worksheet
def write_data(data1, data2, data3, data4, data5, total_length, worksheet, workbook):
    KM_TO_MILES_RATIO = 0.62137
    data1 = data1 / 1000
    data2 = data2 / 1000
    data3 = data3 / 1000
    data4 = data4 / 1000
    data5 = data5 / 1000

    # Set the column size.
    column_sizeB = worksheet.set_column('B:B', 20)
    column_sizeC = worksheet.set_column('C:C', 20)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    # Adds the percent sign and puts it in percent form.
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent = worksheet.set_column('D:D', 10, percent_format)
    # Formats to not show decimal places
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')

    col = 1
    row = 2
    worksheet.write(row, col, data1, cell_format1)
    col += 1
    worksheet.write(row, col, data1 * KM_TO_MILES_RATIO, cell_format1)
    col += 1
    worksheet.write(row, col, data1 / total_length, percent)

    col = 1
    row = 3
    worksheet.write(row, col, data2, cell_format1)
    col += 1
    worksheet.write(row, col, data2 * KM_TO_MILES_RATIO, cell_format1)
    col += 1
    worksheet.write(row, col, data2 / total_length, percent)

    col = 1
    row = 4
    worksheet.write(row, col, data3, cell_format1)
    col += 1
    worksheet.write(row, col, data3 * KM_TO_MILES_RATIO, cell_format1)
    col += 1
    worksheet.write(row, col, data3 / total_length, percent)

    col = 1
    row = 5
    worksheet.write(row, col, data4, cell_format1)
    col += 1
    worksheet.write(row, col, data4 * KM_TO_MILES_RATIO, cell_format1)
    col += 1
    worksheet.write(row, col, data4 / total_length, percent)

    col = 1
    row = 6
    worksheet.write(row, col, data5, cell_format1)
    col += 1
    worksheet.write(row, col, data5 * KM_TO_MILES_RATIO, cell_format1)
    col += 1
    worksheet.write(row, col, data5 / total_length, percent)

    # Calculating Total for Stream Length(Km)
    worksheet.write(7, 1, '=SUM(B3:B7)', cell_format1)
    # Calculating Total for Stream Length (mi)
    worksheet.write(7, 2, '=SUM(C3:C7)', cell_format1)
    # Calculating total percentage.
    worksheet.write(7, 3, '=SUM(D3:D7)', percent)


# Getting the data for Complex Size
# loop through multiple streams
def search_cursor(fields, data, total, stream_network, is_complex, is_capacity_total, worksheet, workbook):
    split_input = stream_network.split(";")
    if is_capacity_total:
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for capacity, dam_complex_size in cursor:
                    total += dam_complex_size
                    if capacity == 0:
                        data[0] += dam_complex_size
                    elif capacity <= 1:
                        data[1] += dam_complex_size
                    elif capacity <= 5:
                        data[2] += dam_complex_size
                    elif capacity <= 15:
                        data[3] += dam_complex_size
                    else:
                        data[4] += dam_complex_size
        return data

    elif is_complex:
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, dam_complex_size in cursor:
                    total += length
                    if dam_complex_size == 0:
                        data[0] += length
                    elif dam_complex_size <= 1:
                        data[1] += length
                    elif dam_complex_size <= 3:
                        data[2] += length
                    elif dam_complex_size <= 5:
                        data[3] += length
                    else:
                        data[4] += length
        total = total / 1000
        write_data(data[0], data[1], data[2], data[3], data[4], total, worksheet, workbook)
    else:
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, capacity in cursor:
                    total += length
                    if capacity == 0:
                        data[0] += length/1000
                    elif capacity <= 1:
                        data[1] += length/1000
                    elif capacity <= 5:
                        data[2] += length/1000
                    elif capacity <= 15:
                        data[3] += length/1000
                    else:
                        data[4] += length/1000
        total = total / 1000
        return data


def column_calc(minimum, watershed):
    if minimum > (len(watershed) + 10):
        return minimum
    else:
        return (len(watershed) + 10)


def write_summary_worksheet(worksheet, stream_network, watershed_name, workbook, fields_list, dams):

    # formatting

    column_sizeA = worksheet.set_column('A:A', column_calc(40, watershed_name))
    column_sizeB = worksheet.set_column('B:B', 10)
    column_sizeC = worksheet.set_column('C:C', 5)
    column_sizeD = worksheet.set_column('D:D', 57)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent_format.set_align('right')
    percent1 = worksheet.set_column('E:E', 8, percent_format)
    color = workbook.add_format()
    color.set_bg_color('C0C0C0')
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')

    # categories

    row = 0
    col = 0
    worksheet.write(row, col, watershed_name, column_sizeA)
    row += 2
    worksheet.write(row, col, "Total Stream Length (Km)")
    row += 1
    worksheet.write(row, col, "Total Stream Length (mi)")
    row += 1
    worksheet.write(row, col, "Existing Complex Size")
    row += 1
    worksheet.write(row, col, "Historic Complex Size")
    row += 1
    worksheet.write(row, col, "Existing Capacity")
    row += 1
    worksheet.write(row, col, "Historic Capacity")
    row += 1
    worksheet.write(row, col, "Existing Vegetation Capacity")
    row += 1
    worksheet.write(row, col, "Historic Vegetation Capacity")
    row += 1
    worksheet.write(row, col, "Total Length (Km) Observed > 80% Predicted")
    row += 1
    if dams is not None:
        worksheet.write(row, col, "Number Dams Snapped")
        row += 1
        worksheet.write(row, col, "Total Dam Count")

    row = 6
    col = 3
    worksheet.write(row, col, "% Reaches Within Capacity Estimate")
    row += 1
    worksheet.write(row, col, "% Network \"Easiest - Low-Hanging Fruit\"")
    row += 1
    worksheet.write(row, col, "% Network \"Dam Building Possible\"")
    row += 1
    worksheet.write(row, col, "% Network \"Negligible Risk\"")
    row += 1
    worksheet.write(row, col, "% Observed > 80% Predicted")
    row += 1
    worksheet.write(row, col, "% Total Dams Snapped to Network")

    split_input = stream_network.split(";")

    # total stream lengths

    totalStreamLengthKm = 0.0
    totalStreamLengthMi = 0.0
    fields = ['SHAPE@Length']
    for streams in split_input:
        with arcpy.da.SearchCursor(streams, fields) as cursor:
            for length, in cursor:
                totalStreamLengthKm += length

    totalStreamLengthKm /= 1000
    totalStreamLengthMi = totalStreamLengthKm / 1.609344

    # total complex sizes

    fields = ['SHAPE@Length', "mCC_EX_CT"]
    if fields[1] in fields_list:
        totalExistingComplex = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, dam_complex_size in cursor:
                    totalExistingComplex += dam_complex_size
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        totalExistingComplex = "N/A"

    fields = ['SHAPE@Length', "mCC_HPE_CT"]
    if fields[1] in fields_list:
        totalHistoricComplex = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, dam_complex_size in cursor:
                    totalHistoricComplex += dam_complex_size
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        totalHistoricComplex = "N/A"

    # total vegetation capacity

    fields = ['SHAPE@Length', "oVC_EX"]
    if fields[1] in fields_list:
        totalExistingVeg = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, density in cursor:
                    totalExistingVeg += ((length / 1000) * density)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        totalExistingVeg = "N/A"

    fields = ['SHAPE@Length', "oVC_Hpe"]
    if fields[1] in fields_list:
        totalHistoricVeg = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, density in cursor:
                    totalHistoricVeg += ((length / 1000) * density)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        totalHistoricVeg = "N/A"

    # Existing Capacity

    fields = ['SHAPE@Length', "oCC_EX"]
    if fields[1] in fields_list:
        totalExistingCapacity = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, density in cursor:
                    totalExistingCapacity += ((length / 1000) * density)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        totalExistingCapacity = "N/A"

    # Historic Capacity

    fields = ['SHAPE@Length', "oCC_HPE"]
    if fields[1] in fields_list:
        totalHistoricCapacity = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, density in cursor:
                    totalHistoricCapacity += ((length / 1000) * density)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        totalHistoricCapacity = "N/A"

    # observed vs. predicted

    fields = ['SHAPE@Length', "e_DamDens", "oCC_EX"]
    if (fields[1] in fields_list) and (fields[2] in fields_list):
        totalSurveyedGreaterLength = 0.0
        totalSurveyedGreaterCount = 0.0
        reachCount = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, surveyed, predicted in cursor:
                    reachCount += 1
                    if (surveyed > (predicted * .8)):
                        totalSurveyedGreaterLength += (length / 1000)
                        totalSurveyedGreaterCount += 1
                    else:
                        pass
        totalSurveyedGreaterPercent = float(totalSurveyedGreaterCount) / float(reachCount)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        totalSurveyedGreaterPercent = "N/A"
        totalSurveyedGreaterLength = "N/A"

    # dams snapped
    if not dams == None:
        dam_fields = [f.name for f in arcpy.ListFields(dams)]
        if "Snapped" in dam_fields:
            totalSnapped = 0.0
            notSnapped = 0.0
            percentSnapped = 0.0
            with arcpy.da.SearchCursor(dams, "Snapped") as cursor:
                for snapped in cursor:
                    if snapped[0] == "Not snapped to network":
                        notSnapped += 1
                    elif snapped[0] == "Snapped to network":
                        totalSnapped += 1
                    else:
                        pass

            percentSnapped = float(totalSnapped) / (float(totalSnapped) + float(notSnapped))
        else:
            arcpy.AddWarning("Could not complete summary worksheet: \"Snapped\" field in Dams shapefile missing")
            totalSnapped = "N/A"
            percentSnapped = "N/A"
    else:
        arcpy.AddWarning("Could not complete summary worksheet: Dams shapefile missing")
        totalSnapped = "N/A"
        percentSnapped = "N/A"

    # dam census density and dams count

    if not dams == None:
        damCensusCount = 0.0
        damCensusDensity = 0.0
        with arcpy.da.SearchCursor(dams, 'SHAPE@Length') as cursor:
            for length in cursor:
                damCensusDensity += 1
                damCensusCount += 1
        damCensusDensity /= totalStreamLengthKm

    else:
        arcpy.AddWarning("Could not complete summary worksheet: Dams shapefile missing")
        damCensusCount = "N/A"
        damCensusDensity = "N/A"

    # percent estimated correctly

    estimateRight = 0
    estimateWrong = 0
    estimateWrongShort = 0

    fields = ['SHAPE@Length', 'BRATvSurv']
    if fields[1] in fields_list:
        percentCorrectEstimate = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, valid in cursor:
                    if valid >= 1:
                        estimateRight += 1
                    elif valid == -1:
                        estimateRight += 1
                    elif valid < 1:
                        estimateWrong += 1
                        if length < 150:
                            estimateWrongShort += 1
                    else:
                        pass

        percentCorrectEstimate = float(estimateRight) / (float(estimateWrong) + float(estimateRight))
        percentUnder = float(estimateWrongShort) / float(estimateWrong)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        percentCorrectEstimate = "N/A"

    # percent network "Easiest-Low Hanging Fruit"

    fields = ['SHAPE@Length', "oPBRC_CR"]
    easiestLength = 0.0
    if fields[1] in fields_list:
        percentEasiest = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, category in cursor:
                    if category == "Easiest - Low-Hanging Fruit":
                        easiestLength += length
                    else:
                        pass
        percentEasiest = easiestLength / (totalStreamLengthKm * 1000)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        percentEasiest = "N/A"

    # percent network "Dam Building Possible"

    fields = ['SHAPE@Length', "oPBRC_UD"]
    possibleLength = 0.0
    if fields[1] in fields_list:
        percentPossible = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, category in cursor:
                    if category == "Dam Building Possible":
                        possibleLength += length
                    else:
                        pass
        percentPossible = possibleLength / (totalStreamLengthKm * 1000)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        percentPossible = "N/A"

    # percent network "Negligible Risk"

    fields = ['SHAPE@Length', "oPBRC_UI"]
    negligibleLength = 0.0
    if fields[1] in fields_list:
        percentNegligible = 0.0
        for streams in split_input:
            with arcpy.da.SearchCursor(streams, fields) as cursor:
                for length, category in cursor:
                    if category == "Negligible Risk":
                        negligibleLength += length
                    else:
                        pass

        percentNegligible = negligibleLength / (totalStreamLengthKm * 1000)
    else:
        arcpy.AddWarning("Could not complete summary worksheet: {0} not in fields.".format(fields[1]))
        percentNegligible = "N/A"


    # output all calculations


    row = 2
    col = 1
    worksheet.write(row, col, totalStreamLengthKm, cell_format1)
    row += 1
    worksheet.write(row, col, totalStreamLengthMi, cell_format1)
    row += 1
    worksheet.write(row, col, totalExistingComplex, cell_format1)
    row += 1
    worksheet.write(row, col, totalHistoricComplex, cell_format1)
    row += 1
    worksheet.write(row, col, totalExistingCapacity, cell_format1)
    row += 1
    worksheet.write(row, col, totalHistoricCapacity, cell_format1)
    row += 1
    worksheet.write(row, col, totalExistingVeg, cell_format1)
    row += 1
    worksheet.write(row, col, totalHistoricVeg, cell_format1)
    row += 1
    worksheet.write(row, col, totalSurveyedGreaterLength, cell_format1)
    row += 1
    worksheet.write(row, col, totalSnapped, cell_format1)
    row += 1
    worksheet.write(row, col, damCensusCount, cell_format1)
    row = 6
    col = 4
    worksheet.write(row, col, percentCorrectEstimate, percent1)
    row += 1
    worksheet.write(row, col, percentEasiest, percent1)
    row += 1
    worksheet.write(row, col, percentPossible, percent1)
    row += 1
    worksheet.write(row, col, percentNegligible, percent1)
    row += 1
    worksheet.write(row, col, totalSurveyedGreaterPercent, percent1)
    row += 1
    worksheet.write(row, col, percentSnapped, percent1)
    row += 1
    worksheet.write(row, col, percentUnder, percent1)
    row = 12
    col = 3
    if dams is not None and estimateWrong > 0:
        worksheet.write(row, col, (str(estimateWrongShort) + " / " + str(
            estimateWrong) + " reaches above capacity estimate were less than 150m"))


def write_density_correlations_worksheet(worksheet, stream_network, watershed_name, workbook):
    # formatting

    column_sizeA = worksheet.set_column('A:A', column_calc(25, watershed_name))
    column_sizeB = worksheet.set_column('B:B', 20)
    column_sizeC = worksheet.set_column('C:C', 11)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x02)
    cell_format1.set_align('right')
    split_input = stream_network.split(";")


    # These lists hold all of the data that needs to be printed

    categories = ['Low Flow Values', 'High Flow Values', 'Stream Slope Values', 'Stream Power Low', 'Stream Power High']
    fields = ['iHyd_QLow', 'iHyd_Q2', 'iGeo_Slope', 'iHyd_SPLow', 'iHyd_SP2']
    column0 = [watershed_name, '']
    column1 = ['oCC_EX', '']
    column2 = ['', '', fields[0], '', '', '', fields[1], '', '', '', fields[2],
               '', '', '', fields[3], '', '', '', fields[4]]
    for field, category in zip(fields, categories):
        column0.append(category)
        column1.append("Mean Dam Density")
        dataList = []
        densityList = []

        for streams in split_input:
            with arcpy.da.SearchCursor(streams, [field, 'oCC_EX']) as cursor:
                for data, density in cursor:
                    dataList.append(data)
                    densityList.append(density)

        dataList, densityList = zip(*sorted(zip(dataList, densityList)))
        totalLength = len(dataList)
        bin1 = totalLength/3
        bin2 = (totalLength/3) + (totalLength/3)
        bin3 = totalLength

        roundedTemp1 = str(round(dataList[bin1], 2))
        column0.append('0 to ' + roundedTemp1)
        roundedTemp1 = str(round(dataList[bin1 + 1], 2))
        roundedTemp2 = str(round(dataList[bin2], 2))
        column0.append(roundedTemp1 + ' to ' + roundedTemp2)
        roundedTemp1 = str(round(dataList[bin2 + 1], 2))
        roundedTemp2 = str(round(dataList[bin3 - 1], 2))
        column0.append(roundedTemp1 + ' to ' + roundedTemp2)

        n=totalLength/3
        splitList = [densityList[i * n:(i + 1) * n] for i in range((len(densityList) + n - 1) // n )]

        for bin in splitList:
            meanForBin = mean(bin)
            if meanForBin > 0:
                column1.append(meanForBin)
            else:
                pass

    columnList = [column0, column1, column2]

    for columnNumber, column in enumerate(columnList):
        for rowNumber, row in enumerate(column):
            worksheet.set_row(rowNumber, None, cell_format1)
            worksheet.write(rowNumber, columnNumber, row)

    worksheet.set_row(0, None, header_format)
    worksheet.set_row(2, None, header_format)
    worksheet.set_row(6, None, header_format)
    worksheet.set_row(10, None, header_format)
    worksheet.set_row(14, None, header_format)
    worksheet.set_row(18, None, header_format)


def write_exist_complex_worksheet(exist_complex_worksheet, stream_network, watershed_name, workbook):
    is_complex = True

    write_header(exist_complex_worksheet, watershed_name)
    write_categories_complex(exist_complex_worksheet, watershed_name)

    fields = ['SHAPE@Length', "mCC_EX_CT"]
    no_dams_length = 0.0
    one_dam_length = 0.0
    some_dams_length = 0.0
    more_dams_length = 0.0
    many_dams_length = 0.0
    total_length = 0.0

    exist_complex_worksheet.write(1, 0, fields[1])

    search_cursor(fields, [no_dams_length, one_dam_length, some_dams_length, more_dams_length, many_dams_length],
                  total_length, stream_network, is_complex, False, exist_complex_worksheet, workbook)


def write_exist_build_cap_worksheet(exist_build_cap_worksheet, stream_network, watershed_name, workbook):
    is_complex = False
    write_header(exist_build_cap_worksheet, watershed_name)

    write_categories_build_cap(exist_build_cap_worksheet, watershed_name)

    fields = ['SHAPE@Length', "oCC_EX"]
    values = [0, 0, 0, 0, 0]
    total_length = 0.0

    exist_build_cap_worksheet.write(1, 0, fields[1])

    values = search_cursor(fields, values, total_length, stream_network, is_complex, False, exist_build_cap_worksheet, workbook)

    write_capacity_values(values, exist_build_cap_worksheet, workbook)


def write_hist_complex_worksheet(hist_complex_worksheet, stream_network, watershed_name, workbook):
    is_complex = True
    write_header(hist_complex_worksheet, watershed_name)
    write_categories_complex(hist_complex_worksheet, watershed_name)

    fields = ['SHAPE@Length', "mCC_HPE_CT"]
    no_dams_length = 0.0
    one_dam_length = 0.0
    some_dams_length = 0.0
    more_dams_length = 0.0
    many_dams_length = 0.0
    total_length = 0.0

    hist_complex_worksheet.write(1, 0, fields[1])

    search_cursor(fields, [no_dams_length, one_dam_length, some_dams_length, more_dams_length, many_dams_length],
                  total_length, stream_network, is_complex, False, hist_complex_worksheet, workbook)


def write_hist_build_cap_worksheet(hist_build_cap_worksheet, stream_network, watershed_name, workbook):
    is_complex = False
    write_header(hist_build_cap_worksheet, watershed_name)
    write_categories_build_cap(hist_build_cap_worksheet, watershed_name)

    fields = ['SHAPE@Length', "oCC_HPE"]
    values = [0, 0, 0, 0, 0]
    total_length = 0.0

    hist_build_cap_worksheet.write(1, 0, fields[1])

    values = search_cursor(fields, values, total_length, stream_network, is_complex, False, hist_build_cap_worksheet, workbook)

    write_capacity_values(values, hist_build_cap_worksheet, workbook)


def write_capacity_values (values, worksheet, workbook):
    column_sizeB = worksheet.set_column('B:B', 20)
    column_sizeC = worksheet.set_column('C:C', 20)
    column_sizeD = worksheet.set_column('D:D', 15)

    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent_format.set_align('right')
    percent1 = worksheet.set_column('D:D', 15, percent_format)
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    row = 2
    col = 1
    worksheet.write(row, col, values[0], cell_format1)
    row += 1
    worksheet.write(row, col, values[1], cell_format1)
    row += 1
    worksheet.write(row, col, values[2], cell_format1)
    row += 1
    worksheet.write(row, col, values[3], cell_format1)
    row += 1
    worksheet.write(row, col, values[4], cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(B3:B7)", cell_format1)

    row = 2
    col = 2
    worksheet.write(row, col, "=B3*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B4*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B5*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B6*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B7*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, '=SUM(C3:C7)', cell_format1)

    row = 2
    col = 3
    worksheet.write(row, col, '=(B3/$B$8)', percent1)
    row += 1
    worksheet.write(row, col, '=(B4/$B$8)', percent1)
    row += 1
    worksheet.write(row, col, '=(B5/$B$8)', percent1)
    row += 1
    worksheet.write(row, col, '=(B6/$B$8)', percent1)
    row += 1
    worksheet.write(row, col, '=(B7/$B$8)', percent1)
    row += 1
    worksheet.write(row, col, '=SUM(D3:D7)', percent1)


def write_hist_vs_exist_worksheet(hist_vs_exist_worksheet, stream_network, watershed_name, workbook):
    column_sizeA = hist_vs_exist_worksheet.set_column('A:A', column_calc(25, watershed_name))
    column_sizeB = hist_vs_exist_worksheet.set_column('B:B', 20)
    column_sizeC = hist_vs_exist_worksheet.set_column('C:C', 20)
    column_sizeD = hist_vs_exist_worksheet.set_column('D:D', 25)
    column_sizeE = hist_vs_exist_worksheet.set_column('E:E', 2)
    column_sizeF = hist_vs_exist_worksheet.set_column('F:F', 20)
    column_sizeG = hist_vs_exist_worksheet.set_column('G:G', 20)
    column_sizeH = hist_vs_exist_worksheet.set_column('H:H', 25)
    column_sizeI = hist_vs_exist_worksheet.set_column('I:I', 2)
    column_sizeJ = hist_vs_exist_worksheet.set_column('J:J', 20)
    column_sizeK = hist_vs_exist_worksheet.set_column('K:K', 5)
    column_sizeL = hist_vs_exist_worksheet.set_column('L:L', 30)
    column_sizeM = hist_vs_exist_worksheet.set_column('M:M', 30)
    column_sizeN = hist_vs_exist_worksheet.set_column('N:N', 5)
    column_sizeO = hist_vs_exist_worksheet.set_column('O:O', 15)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    hist_vs_exist_worksheet.set_row(0, None, header_format)
    hist_vs_exist_worksheet.set_row(1, None, header_format)
    hist_vs_exist_worksheet.set_row(2, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent1 = hist_vs_exist_worksheet.set_column('C:C', 20, percent_format)
    percent2 = hist_vs_exist_worksheet.set_column('G:G', 20, percent_format)
    percent3 = hist_vs_exist_worksheet.set_column('O:O', 8, percent_format)
    percent4 = hist_vs_exist_worksheet.set_column('J:J', 20, percent_format)
    color = workbook.add_format()
    color.set_bg_color('#C0C0C0')
    hist_vs_exist_worksheet.write("A3", "", color)
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format2 = workbook.add_format()
    cell_format2.set_num_format(0x02)

    # Headers
    row = 0
    col = 0
    hist_vs_exist_worksheet.write(row, col, watershed_name, column_sizeA)
    row += 1
    col += 2
    hist_vs_exist_worksheet.write(row, col, "Existing Capacity")
    col += 4
    hist_vs_exist_worksheet.write(row, col, "Historic Capacity")
    row += 1
    col = 0
    hist_vs_exist_worksheet.write(row, col, "Category")
    col += 1
    hist_vs_exist_worksheet.write(row, col, "Stream Length (km)", column_sizeB)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "% of Stream Network", column_sizeC)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "Estimated Dam Capacity", column_sizeD)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "", column_sizeE)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "Stream Length (km)", column_sizeF)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "% of Stream Network", column_sizeG)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "Estimated Dam Capacity", column_sizeH)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "", column_sizeI)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "% Capacity of Historic", column_sizeJ)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "", column_sizeK)
    col += 1
    row = 2
    col = 11
    hist_vs_exist_worksheet.write(row, col, "Estimated Existing Dams/km total", column_sizeL)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "Estimated Historic Dams/km total", column_sizeM)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "", column_sizeN)
    col += 1
    hist_vs_exist_worksheet.write(row, col, "%loss", column_sizeO)

    # Categories:
    write_categories_hist_vs_exist(hist_vs_exist_worksheet, watershed_name)

    # Existing - Stream Length: Starting at B4 - B8 get numbers from Existing Capacity, B7 - B3
    row = 3
    col = 1
    hist_vs_exist_worksheet.write(row, col, "=('Existing Dam Building Capacity'!B3)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Existing Dam Building Capacity'!B4)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Existing Dam Building Capacity'!B5)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Existing Dam Building Capacity'!B6)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Existing Dam Building Capacity'!B7)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Existing Dam Building Capacity'!B8)", cell_format1)

    # Existing - % of Stream Network
    row = 3
    col = 2
    hist_vs_exist_worksheet.write(row, col, '=(B4/$B$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(B5/$B$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(B6/$B$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(B7/$B$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(B8/$B$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=SUM(C4:C8)', percent1)

    # Existing - estimated dam capacity
    fields = ["oCC_EX", "mCC_EX_CT"]
    total_capacity = 0
    values = [0, 0, 0, 0, 0]
    values = search_cursor(fields, values, total_capacity, stream_network, False, True, hist_vs_exist_worksheet, workbook)
    row = 3
    col = 3
    hist_vs_exist_worksheet.write(row, col, values[0])
    row += 1
    hist_vs_exist_worksheet.write(row, col, values[1])
    row += 1
    hist_vs_exist_worksheet.write(row, col, values[2])
    row += 1
    hist_vs_exist_worksheet.write(row, col, values[3])
    row += 1
    hist_vs_exist_worksheet.write(row, col, values[4])
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=SUM(D4:D8)")

    # Historic - Stream Length: Starting at B4 - B8 get numbers from Existing Capacity, B7 - B3
    row = 3
    col = 5
    hist_vs_exist_worksheet.write(row, col, "=('Historic Dam Building Capacity'!B3)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Historic Dam Building Capacity'!B4)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Historic Dam Building Capacity'!B5)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Historic Dam Building Capacity'!B6)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Historic Dam Building Capacity'!B7)", cell_format1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=('Historic Dam Building Capacity'!B8)", cell_format1)

    # Historic - % of Stream Network
    row = 3
    col = 6
    hist_vs_exist_worksheet.write(row, col, '=(F4/$F$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(F5/$F$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(F6/$F$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(F7/$F$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(F8/$F$9)', percent1)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=SUM(G4:G8)', percent1)

    # Historic - estimated dam capacity
    fields = ["oCC_HPE", "mCC_HPE_CT"]
    total_capacity = 0
    values = [0, 0, 0, 0, 0]
    values= search_cursor(fields, values, total_capacity, stream_network, False, True, hist_vs_exist_worksheet, workbook)
    row = 3
    col = 7
    hist_vs_exist_worksheet.write(row, col, values[0])
    row += 1
    hist_vs_exist_worksheet.write(row, col, values[1])
    row += 1
    hist_vs_exist_worksheet.write(row, col, values[2])
    row += 1
    hist_vs_exist_worksheet.write(row, col, values[3])
    row += 1
    hist_vs_exist_worksheet.write(row, col, values[4])
    row += 1
    hist_vs_exist_worksheet.write(row, col, "=SUM(H4:H8)")

    # % Capacity of Historic
    row = 3
    col = 9
    # Checking if the cell to the left equals zero. This is to prevent div by zero errors
    if values[0] == 0:
        hist_vs_exist_worksheet.write(row, col, 0, percent1)
    else:
        hist_vs_exist_worksheet.write(row, col, '=(D4/H4)', percent4)
    row += 1
    if values[1] == 0:
        hist_vs_exist_worksheet.write(row, col, 0, percent1)
    else:
        hist_vs_exist_worksheet.write(row, col, '=(D5/H5)', percent4)
    row += 1
    if values[2] == 0:
        hist_vs_exist_worksheet.write(row, col, 0)
    else:
        hist_vs_exist_worksheet.write(row, col, '=(D6/H6)', percent4)
    row += 1
    if values[3] == 0:
        hist_vs_exist_worksheet.write(row, col, 0)
    else:
        hist_vs_exist_worksheet.write(row, col, '=(D7/H7)', percent4)
    row += 1
    if values[4] == 0:
        hist_vs_exist_worksheet.write(row, col, 0)
    else:
        hist_vs_exist_worksheet.write(row, col, '=(D8/H8)', percent4)
    row += 1
    hist_vs_exist_worksheet.write(row, col, '=(D9/H9)', percent1)

    # totals
    hist_vs_exist_worksheet.write(3, 11, '=(D9/B9)', cell_format2)
    hist_vs_exist_worksheet.write(3, 12, '=(H9/F9)', cell_format2)
    hist_vs_exist_worksheet.write(3, 14, '=1-$J$9', percent3)


def write_conservation_restoration(worksheet, stream_network, watershed_name, workbook):
    column_sizeA = worksheet.set_column('A:A', column_calc(30, watershed_name))
    column_sizeB = worksheet.set_column('B:B', 20)
    column_sizeC = worksheet.set_column('C:C', 20)
    column_sizeD = worksheet.set_column('D:D', 15)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent = worksheet.set_column('D:D', 10, percent_format)
    color = workbook.add_format()
    color.set_bg_color('#C0C0C0')
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')

    # headers
    row = 0
    col = 0
    worksheet.write(row, col, watershed_name, column_sizeA)
    row += 1
    worksheet.write(row, col, "oPBRC_CR")
    col += 1
    worksheet.write(row, col, "Stream Length (km)", column_sizeB)
    col += 1
    worksheet.write(row, col, "Stream Length (mi)", column_sizeC)
    col += 1
    worksheet.write(row, col, "Percent", column_sizeD)

    # categories
    row = 2
    col = 0
    worksheet.write(row, col, "Easiest - Low-Hanging Fruit")
    row += 1
    worksheet.write(row, col, "Straight Forward - Quick Return")
    row += 1
    worksheet.write(row, col, "Strategic - Long-Term Investment")
    row += 1
    worksheet.write(row, col, "Other")
    row += 1
    worksheet.write(row, col, "Total")

    # calculate fields
    easy = 0
    mod = 0
    strateg = 0
    other = 0
    total = 0
    split_input = stream_network.split(";")
    for streams in split_input:
        with arcpy.da.SearchCursor(streams, ['SHAPE@Length', 'oPBRC_CR']) as cursor:
            for length, category in cursor:
                total += length
                if category == "Easiest - Low-Hanging Fruit":
                    easy += length
                elif category == "Straight Forward - Quick Return":
                    mod += length
                elif category == "Strategic - Long-Term Investment":
                    strateg += length
                else:
                    other += length
    # convert from m to km
    easy /= 1000
    mod /= 1000
    strateg /= 1000
    other /= 1000

    # write fields
    row = 2
    col = 1
    worksheet.write(row, col, easy, cell_format1)
    row += 1
    worksheet.write(row, col, mod, cell_format1)
    row += 1
    worksheet.write(row, col, strateg, cell_format1)
    row += 1
    worksheet.write(row, col, other, cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(B3:B6)", cell_format1)

    # calculate km to mi
    col += 1
    row = 2
    worksheet.write(row, col, "=B3*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B4*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B5*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B6*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(C3:C6)", cell_format1)

    # calculate percents
    col += 1
    row = 2
    worksheet.write(row, col, '=B3/B7', percent)
    row += 1
    worksheet.write(row, col, '=B4/B7', percent)
    row += 1
    worksheet.write(row, col, '=B5/B7', percent)
    row += 1
    worksheet.write(row, col, '=B6/B7', percent)
    row += 1
    worksheet.write(row, col, '=B7/B7', percent)


def write_unsuitable_worksheet(worksheet, stream_network, watershed_name, workbook):
    column_sizeA = worksheet.set_column('A:A', column_calc(36, watershed_name))
    column_sizeB = worksheet.set_column('B:B', 20)
    column_sizeC = worksheet.set_column('C:C', 20)
    column_sizeD = worksheet.set_column('D:D', 15)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent = worksheet.set_column('D:D', 10, percent_format)
    color = workbook.add_format()
    color.set_bg_color('#C0C0C0')
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')

    # headers
    row = 0
    col = 0
    worksheet.write(row, col, watershed_name, column_sizeA)
    row += 1
    worksheet.write(row, col, "oPBRC_UD")
    col += 1
    worksheet.write(row, col, "Stream Length (km)", column_sizeB)
    col += 1
    worksheet.write(row, col, "Stream Length (mi)", column_sizeC)
    col += 1
    worksheet.write(row, col, "Percent", column_sizeD)

    # categories
    row = 2
    col = 0
    worksheet.write(row, col, "Anthropogenicallly Limited")
    row += 1
    worksheet.write(row, col, "Naturally Vegetation Limited")
    row += 1
    worksheet.write(row, col, "Slope Limited")
    row += 1
    worksheet.write(row, col, "Stream Power Limited")
    row += 1
    worksheet.write(row, col, "Potential Reservoir or Landuse Change")
    row += 1
    worksheet.write(row, col, "Dam Building Possible")
    row += 1
    worksheet.write(row, col, "Stream Size Limited")
    row += 1
    worksheet.write(row, col, "Total")

    # calculate fields
    anth = 0
    veg = 0
    slope = 0
    stream = 0
    reservoir = 0
    dams = 0
    tbd = 0
    total = 0
    split_input = stream_network.split(";")
    for streams in split_input:
        with arcpy.da.SearchCursor(streams, ['SHAPE@Length', 'oPBRC_UD']) as cursor:
            for length, category in cursor:
                total += length
                if category == "Anthropogenically Limited":
                    anth += length
                elif category == "Naturally Vegetation Limited":
                    veg += length
                elif category == "Slope Limited":
                    slope += length
                elif category == "Stream Power Limited":
                    stream += length
                elif category == "Potential Reservoir or Landuse Change":
                    reservoir += length
                elif category == "Dam Building Possible":
                    dams += length
                elif category == "...TBD...":
                    tbd += length
                else:
                    pass
    # convert m to km
    anth /= 1000
    veg /= 1000
    slope /= 1000
    stream /= 1000
    reservoir /= 1000
    dams /= 1000
    tbd /= 1000

    row = 2
    col = 1
    worksheet.write(row, col, anth, cell_format1)
    row += 1
    worksheet.write(row, col, veg, cell_format1)
    row += 1
    worksheet.write(row, col, slope, cell_format1)
    row += 1
    worksheet.write(row, col, stream, cell_format1)
    row += 1
    worksheet.write(row, col, reservoir, cell_format1)
    row += 1
    worksheet.write(row, col, dams, cell_format1)
    row += 1
    worksheet.write(row, col, tbd, cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(B3:B9)", cell_format1)

    # calculate km to mi
    col += 1
    row = 2
    worksheet.write(row, col, "=B3*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B4*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B5*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B6*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B7*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B8*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B9*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(C3:C9)", cell_format1)

    # calculate percents
    col += 1
    row = 2
    worksheet.write(row, col, '=B3/B10', percent)
    row += 1
    worksheet.write(row, col, '=B4/B10', percent)
    row += 1
    worksheet.write(row, col, '=B5/B10', percent)
    row += 1
    worksheet.write(row, col, '=B6/B10', percent)
    row += 1
    worksheet.write(row, col, '=B7/B10', percent)
    row += 1
    worksheet.write(row, col, '=B8/B10', percent)
    row += 1
    worksheet.write(row, col, '=B9/B10', percent)
    row += 1
    worksheet.write(row, col, '=B10/B10', percent)


def write_risk_worksheet(worksheet, stream_network, watershed_name, workbook):
    column_sizeA = worksheet.set_column('A:A', column_calc(25, watershed_name))
    column_sizeB = worksheet.set_column('B:B', 20)
    column_sizeC = worksheet.set_column('C:C', 20)
    column_sizeD = worksheet.set_column('D:D', 15)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent = worksheet.set_column('D:D', 10, percent_format)
    color = workbook.add_format()
    color.set_bg_color('#C0C0C0')
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')

    # headers
    row = 0
    col = 0
    worksheet.write(row, col, watershed_name, column_sizeA)
    row += 1
    worksheet.write(row, col, "oPBRC_UI")
    col += 1
    worksheet.write(row, col, "Stream Length (km)", column_sizeB)
    col += 1
    worksheet.write(row, col, "Stream Length (mi)", column_sizeC)
    col += 1
    worksheet.write(row, col, "Percent", column_sizeD)

    # categories
    row = 2
    col = 0
    worksheet.write(row, col, "Considerable Risk")
    row += 1
    worksheet.write(row, col, "Some Risk")
    row += 1
    worksheet.write(row, col, "Minor Risk")
    row += 1
    worksheet.write(row, col, "Negligible Risk")
    row += 1
    worksheet.write(row, col, "Total")

    # calculate fields
    cons = 0
    some = 0
    minr = 0
    negl = 0
    total = 0
    split_input = stream_network.split(";")
    for streams in split_input:
        with arcpy.da.SearchCursor(streams, ['SHAPE@Length', 'oPBRC_UI']) as cursor:
            for length, category in cursor:
                total += length
                if category == "Considerable Risk":
                    cons += length
                elif category == "Some Risk":
                    some += length
                elif category == "Minor Risk":
                    minr += length
                elif category == "Negligible Risk":
                    negl += length
                else:
                    pass
    # convert m to km
    cons /= 1000
    some /= 1000
    minr /= 1000
    negl /= 1000

    # write values
    row = 2
    col = 1
    worksheet.write(row, col, cons, cell_format1)
    row += 1
    worksheet.write(row, col, some, cell_format1)
    row += 1
    worksheet.write(row, col, minr, cell_format1)
    row += 1
    worksheet.write(row, col, negl, cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(B3:B6)", cell_format1)

    # calculate km to mi
    col += 1
    row = 2
    worksheet.write(row, col, "=B3*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B4*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B5*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B6*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(C3:C6)", cell_format1)

    # calculate percents
    col += 1
    row = 2
    worksheet.write(row, col, '=B3/B7', percent)
    row += 1
    worksheet.write(row, col, '=B4/B7', percent)
    row += 1
    worksheet.write(row, col, '=B5/B7', percent)
    row += 1
    worksheet.write(row, col, '=B6/B7', percent)
    row += 1
    worksheet.write(row, col, '=B7/B7', percent)


def write_strategies_worksheet(worksheet, stream_network, watershed_name, workbook):
    column_sizeA = worksheet.set_column('A:A', column_calc(40, watershed_name))
    column_sizeB = worksheet.set_column('B:B', 20)
    column_sizeC = worksheet.set_column('C:C', 20)
    column_sizeD = worksheet.set_column('D:D', 15)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent = worksheet.set_column('D:D', 10, percent_format)
    color = workbook.add_format()
    color.set_bg_color('#C0C0C0')
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')

    # headers
    row = 0
    col = 0
    worksheet.write(row, col, watershed_name, column_sizeA)
    row += 1
    worksheet.write(row, col, "ConsVRest")
    col += 1
    worksheet.write(row, col, "Stream Length (km)", column_sizeB)
    col += 1
    worksheet.write(row, col, "Stream Length (mi)", column_sizeC)
    col += 1
    worksheet.write(row, col, "Percent", column_sizeD)

    # categories
    row = 2
    col = 0
    worksheet.write(row, col, "Immediate - Beaver Conservation")
    row += 1
    worksheet.write(row, col, "Immediate - Beaver Translocation")
    row += 1
    worksheet.write(row, col, "Medium Term - Riparian Veg Restoration")
    row += 1
    worksheet.write(row, col, "Long Term - Riparian Veg Reestablishment")
    row += 1
    worksheet.write(row, col, "Low Capacity Habitat")
    row += 1
    worksheet.write(row, col, "Total")

    # calculate fields
    cons = 0
    trns = 0
    rest = 0
    veg = 0
    low = 0
    total = 0
    split_input = stream_network.split(";")
    for streams in split_input:
        with arcpy.da.SearchCursor(streams, ['SHAPE@Length', 'ConsVRest']) as cursor:
            for length, category in cursor:
                total += length
                if category == "Immediate - Beaver Conservation":
                    cons += length
                elif category == "Immediate - Potential Beaver Translocation":
                    trns += length
                elif category == "Mid Term - Process-based Riparian Vegetation Resto":
                    rest += length
                elif category == "Long Term: Riparian Vegetation Reestablishment":
                    veg += length
                elif category == "Low Capacity Habitat":
                    low += length
                else:
                    pass
    # convert m to km
    cons /= 1000
    trns /= 1000
    rest /= 1000
    veg /= 1000
    low /= 1000

    # write length km

    row = 2
    col = 1
    worksheet.write(row, col, cons, cell_format1)
    row += 1
    worksheet.write(row, col, trns, cell_format1)
    row += 1
    worksheet.write(row, col, rest, cell_format1)
    row += 1
    worksheet.write(row, col, veg, cell_format1)
    row += 1
    worksheet.write(row, col, low, cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(B3:B7)", cell_format1)

    # calculate km to mi
    col += 1
    row = 2
    worksheet.write(row, col, "=B3*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B4*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B5*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B6*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B7*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(C3:C7)", cell_format1)

    # calculate percents
    col += 1
    row = 2
    worksheet.write(row, col, '=B3/B8', percent)
    row += 1
    worksheet.write(row, col, '=B4/B8', percent)
    row += 1
    worksheet.write(row, col, '=B5/B8', percent)
    row += 1
    worksheet.write(row, col, '=B6/B8', percent)
    row += 1
    worksheet.write(row, col, '=B7/B8', percent)
    row += 1
    worksheet.write(row, col, '=B8/B8', percent)


def write_validation_worksheet(worksheet, stream_network, watershed_name, workbook):
    column_sizeA = worksheet.set_column('A:A', column_calc(40, watershed_name))
    column_sizeB = worksheet.set_column('B:B', 18)
    column_sizeC = worksheet.set_column('C:C', 15)
    column_sizeD = worksheet.set_column('D:D', 20)
    column_sizeE = worksheet.set_column('E:E', 20)
    column_sizeF = worksheet.set_column('F:F', 15)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    worksheet.set_row(2, None, header_format)
    worksheet.set_row(7, None, header_format)
    worksheet.set_row(12, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent = worksheet.set_column('C:C', 20, percent_format)
    percent2 = worksheet.set_column('F:F', 15, percent_format)
    color = workbook.add_format()
    color.set_bg_color('#C0C0C0')
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')

    row = 0
    col = 0
    worksheet.write(row, col, watershed_name, column_sizeA)
    row += 1
    worksheet.write(row, col, "BRATvSurv")

    landUseCategories = ["Urban", "Undeveloped", "Agriculture or Mixed Use"]
    for counter, category in enumerate(landUseCategories):

        col = 0
        row = 2 + (5*counter)

        worksheet.write(row, col, category)
        col+=1
        worksheet.write(row, col, "Number of Reaches", column_sizeB)
        col += 1
        worksheet.write(row, col, "Percent of Reaches", column_sizeC)
        col += 1
        worksheet.write(row, col, "Stream Length (km)", column_sizeD)
        col += 1
        worksheet.write(row, col, "Stream Length (mi)", column_sizeE)
        col += 1
        worksheet.write(row, col, "Percent Length", column_sizeF)

        # categories
        row = 3 + (5 * counter)
        col = 0
        worksheet.write(row, col, "Fewer dams than predicted existing capacity")
        row += 1
        worksheet.write(row, col, "More dams than predicted existing capacity")
        row += 1
        worksheet.write(row, col, "No surveyed dams")
        row += 1
        worksheet.write(row, col, "Total")

        # percent of reaches
        totalRow = 7 + (5 * counter)
        row = 3 + (5 * counter)
        col = 2
        worksheet.write(row, col, "=B{}/B{}".format(row + 1, totalRow), percent)
        row += 1
        worksheet.write(row, col, "=B{}/B{}".format(row + 1, totalRow), percent)
        row += 1
        worksheet.write(row, col, "=B{}/B{}".format(row + 1, totalRow), percent)
        row += 1
        worksheet.write(row, col, "=SUM(C{}:C{})".format(totalRow-3, totalRow-1), percent)

        # calculate km to mi
        row = 3 + (5 * counter)
        col = 4
        worksheet.write(row, col, "=D{}*0.62137".format(row + 1), cell_format1)
        row += 1
        worksheet.write(row, col, "=D{}*0.62137".format(row + 1), cell_format1)
        row += 1
        worksheet.write(row, col, "=D{}*0.62137".format(row + 1), cell_format1)
        row += 1
        worksheet.write(row, col, "=SUM(E{}:E{})".format(totalRow - 3, totalRow - 1), cell_format1)

        # calculate percents
        row = 3 + (5 * counter)
        col = 5
        worksheet.write(row, col, "=D{}/D{}".format(row + 1, totalRow), percent2)
        row += 1
        worksheet.write(row, col, "=D{}/D{}".format(row + 1, totalRow), percent2)
        row += 1
        worksheet.write(row, col, "=D{}/D{}".format(row + 1, totalRow), percent2)
        row += 1
        worksheet.write(row, col, "=D{}/D{}".format(row + 1, totalRow), percent2)



        # calculate fields
        few_km = 0
        few = 0
        more_km = 0
        more = 0
        none_km = 0
        none = 0
        split_input = stream_network.split(";")
        for streams in split_input:
            if category == "Urban":
                with arcpy.da.SearchCursor(streams, ['SHAPE@Length', 'BRATvSurv', 'iPC_HighLU']) as cursor:
                    for length, valid, land in cursor:
                        if land > 20:
                            if valid == -1:
                                none_km += length
                                none += 1
                            elif valid >= 1:
                                few_km += length
                                few += 1
                            elif valid < 1:
                                more_km += length
                                more += 1
                            else:
                                pass
                        else:
                            pass
            elif category == "Undeveloped":
                with arcpy.da.SearchCursor(streams, ['SHAPE@Length', 'BRATvSurv', 'iPC_HighLU', 'iPC_VLowLU']) as cursor:
                    for length, valid, landHigh, landLow in cursor:
                        if (not landHigh > 20) and (landLow > 90):
                            if valid == -1:
                                none_km += length
                                none += 1
                            elif valid >= 1:
                                few_km += length
                                few += 1
                            elif valid < 1:
                                more_km += length
                                more += 1
                            else:
                                pass
                        else:
                            pass
            else:
                with arcpy.da.SearchCursor(streams, ['SHAPE@Length', 'BRATvSurv', 'iPC_HighLU', 'iPC_VLowLU']) as cursor:
                    for length, valid, landHigh, landLow in cursor:
                        if (not landHigh > 20) and (not landLow > 90):
                            if valid == -1:
                                none_km += length
                                none += 1
                            elif valid >= 1:
                                few_km += length
                                few += 1
                            elif valid < 1:
                                more_km += length
                                more += 1
                            else:
                                pass
                        else:
                            pass
        few_km /= 1000
        more_km /= 1000
        none_km /= 1000

        # raw number of reaches
        totalRow = 7 + (5 * counter)
        row = 3 + (5 * counter)
        col = 1
        worksheet.write(row, col, few)
        row += 1
        worksheet.write(row, col, more)
        row += 1
        worksheet.write(row, col, none)
        row += 1
        worksheet.write(row, col, "=SUM(B{}:B{})".format(totalRow - 3, totalRow - 1), cell_format1)

        # length per category
        row = 3 + (5 * counter)
        col = 3
        worksheet.write(row, col, few_km, cell_format1)
        row += 1
        worksheet.write(row, col, more_km, cell_format1)
        row += 1
        worksheet.write(row, col, none_km, cell_format1)
        row += 1
        worksheet.write(row, col, "=SUM(D{}:D{})".format(totalRow - 3, totalRow - 1), cell_format1)

    row = 18
    col = 0
    worksheet.write(row, col, "Total")
    col+= 1
    worksheet.write(row, col, "=SUM(B7,B12,B17)", cell_format1)
    col += 2
    worksheet.write(row, col, "=SUM(D7,D12,D17)", cell_format1)


def write_historic_remaining_worksheet(worksheet, stream_network, watershed_name, workbook):
    column_sizeA = worksheet.set_column('A:A', column_calc(40, watershed_name))
    column_sizeB = worksheet.set_column('B:B', 18)
    column_sizeC = worksheet.set_column('C:C', 20)
    column_sizeD = worksheet.set_column('D:D', 20)
    column_sizeE = worksheet.set_column('E:E', 15)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent = worksheet.set_column('D:D', 20, percent_format)
    color = workbook.add_format()
    color.set_bg_color('#C0C0C0')
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')

    row = 0
    col = 0
    worksheet.write(row, col, watershed_name, column_sizeA)
    row += 1
    worksheet.write(row, col, "mCC_EXvHPE")

    col = 0
    row = 1

    worksheet.write(row, col, "Percent Historic Capacity Remaining")
    col+=1
    worksheet.write(row, col, "Stream Length (km)", column_sizeB)
    col += 1
    worksheet.write(row, col, "Stream Length (mi)", column_sizeC)
    col += 1
    worksheet.write(row, col, "Percent Length", column_sizeD)

    # categories
    row = 2
    col = 0
    worksheet.write(row, col, "0 - 25%")
    row += 1
    worksheet.write(row, col, "25 - 50%")
    row += 1
    worksheet.write(row, col, "50 - 75%")
    row += 1
    worksheet.write(row, col, "75 - 100%")
    row += 1
    worksheet.write(row, col, "> 100%")
    row += 1
    worksheet.write(row, col, "Total")

    # calculate km to mi
    row = 2
    col = 2
    worksheet.write(row, col, "=B3*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B4*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B5*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B6*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=B7*0.62137", cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(C3:C7)", cell_format1)

    # calculate percents
    row = 2
    col = 3
    worksheet.write(row, col, "=B3/$B$8", percent)
    row += 1
    worksheet.write(row, col, "=B4/$B$8", percent)
    row += 1
    worksheet.write(row, col, "=B5/$B$8", percent)
    row += 1
    worksheet.write(row, col, "=B6/$B$8", percent)
    row += 1
    worksheet.write(row, col, "=B7/$B$8", percent)
    row += 1
    worksheet.write(row, col, "=SUM(D3:D7)", percent)



    # calculate fields
    zero_25 = 0
    twentyfive_50 = 0
    fifty_75 = 0
    seventyfive_100 = 0
    hundred_plus = 0
    split_input = stream_network.split(";")
    for streams in split_input:
        with arcpy.da.SearchCursor(streams, ['SHAPE@Length', 'mCC_EXvHPE']) as cursor:
            for length, percent in cursor:
                if percent <= 0.25:
                    zero_25 += length
                elif percent <= 0.50:
                    twentyfive_50 += length
                elif percent <= 0.75:
                    fifty_75 += length
                elif percent <= 1.0:
                    seventyfive_100 += length
                else:
                    hundred_plus += length
        
    zero_25 /= 1000
    twentyfive_50 /= 1000
    fifty_75 /= 1000
    seventyfive_100 /= 1000
    hundred_plus /= 1000

    # length in km per category
    row = 2
    col = 1
    worksheet.write(row, col, zero_25, cell_format1)
    row += 1
    worksheet.write(row, col, twentyfive_50, cell_format1)
    row += 1
    worksheet.write(row, col, fifty_75, cell_format1)
    row += 1
    worksheet.write(row, col, seventyfive_100, cell_format1)
    row += 1
    worksheet.write(row, col, hundred_plus, cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(B3:B7)")


def write_electivity_worksheet(worksheet, stream_network, watershed_name, workbook):
    # Formatting

    worksheet.set_column('A:A', column_calc(20, watershed_name))
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 22)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('G:G', 35)
    worksheet.set_column('H:H', 42)
    worksheet.set_column('I:I', 42)
    worksheet.set_column('J:J', 30)
    worksheet.set_column('K:K', 15)
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.set_row(0, None, header_format)
    worksheet.set_row(1, None, header_format)
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent_format.set_align('right')
    percent1 = worksheet.set_column('E:E', 22, percent_format)
    percent2 = worksheet.set_column('J:J', 20, percent_format)
    color = workbook.add_format()
    color.set_bg_color('C0C0C0')
    cell_format1 = workbook.add_format()
    cell_format1.set_num_format(0x01)
    cell_format1.set_align('right')
    cell_format2 = workbook.add_format()
    cell_format2.set_num_format('0.0000')
    cell_format2.set_align('right')

    # Create Column Labels
    row = 0
    col = 0
    worksheet.write(row, col, watershed_name)
    row += 1
    worksheet.write(row, col, "Segment Type")
    col += 1
    worksheet.write(row, col, "Stream Length (m)")
    col += 1
    worksheet.write(row, col, "Stream Length (Km)")
    col += 1
    worksheet.write(row, col, "Stream Length (mi)")
    col += 1
    worksheet.write(row, col, "% of Drainage Network")
    col += 1
    worksheet.write(row, col, "Surveyed Dams Count")
    col += 1
    worksheet.write(row, col, "BRAT Estimated Capacity Dam Count")
    col += 1
    worksheet.write(row, col, "Average Surveyed Dam Density (Dams/Km)")
    col += 1
    worksheet.write(row, col, "Average BRAT Predicted Density (Dams/Km)")
    col += 1
    worksheet.write(row, col, "% Modeled Capacity")
    col += 1
    worksheet.write(row, col, "Electivity Index")

    # Create Row Labels
    row = 2
    col = 0
    worksheet.write(row, col, "None")
    row += 1
    worksheet.write(row, col, "Rare")
    row += 1
    worksheet.write(row, col, "Occasional")
    row += 1
    worksheet.write(row, col, "Frequent")
    row += 1
    worksheet.write(row, col, "Pervasive")
    row += 1
    worksheet.write(row, col, "Total")
    row += 1

    # Column B (Stream Length Meters) 
    row = 2
    col = 1
    worksheet.write(row, col, "=C3*1000", cell_format1)
    row += 1
    worksheet.write(row, col, "=C4*1000", cell_format1)
    row += 1
    worksheet.write(row, col, "=C5*1000", cell_format1)
    row += 1
    worksheet.write(row, col, "=C6*1000", cell_format1)
    row += 1
    worksheet.write(row, col, "=C7*1000", cell_format1)
    row += 1
    worksheet.write(row, col, "=C8*1000", cell_format1)

    # Column C (Stream Length Kilometers) These values have already been calculated, so I'm just pulling them from the other Worksheet

    row = 2
    col = 2
    worksheet.write(row, col, "='Existing Dam Building Capacity'!B3", cell_format1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!B4", cell_format1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!B5", cell_format1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!B6", cell_format1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!B7", cell_format1)
    row += 1
    worksheet.write(row, col, "=='Existing Dam Building Capacity'!B8", cell_format1)

    # Column D (Stream Length Miles) These values have already been calculated, so I'm just pulling them from the other Worksheet

    row = 2
    col = 3
    worksheet.write(row, col, "='Existing Dam Building Capacity'!C3", cell_format1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!C4", cell_format1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!C5", cell_format1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!C6", cell_format1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!C7", cell_format1)
    row += 1
    worksheet.write(row, col, "=='Existing Dam Building Capacity'!C8", cell_format1)

    # Column E (Percent of Drainage Network) These values have already been calculated, so I'm just pulling them from the other Worksheet

    row = 2
    col = 4
    worksheet.write(row, col, "='Existing Dam Building Capacity'!D3", percent1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!D4", percent1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!D5", percent1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!D6", percent1)
    row += 1
    worksheet.write(row, col, "='Existing Dam Building Capacity'!D7", percent1)
    row += 1
    worksheet.write(row, col, "N/A", cell_format1)

    # Column F (Number of Surveyed Dams)

    none = 0.0
    rare = 0.0
    occ = 0.0
    freq = 0.0
    per = 0.0

    split_input = stream_network.split(";")
    fields = ['oCC_EX', "e_DamCt"]
    for streams in split_input:
        with arcpy.da.SearchCursor(streams, fields) as cursor:
            for capacity, dam_complex_size in cursor:
                if capacity == 0:
                    none += float(dam_complex_size)
                elif capacity <= 1:
                    rare += float(dam_complex_size)
                elif capacity <= 5:
                    occ += float(dam_complex_size)
                elif capacity <= 15:
                    freq += float(dam_complex_size)
                else:
                    per += float(dam_complex_size)
    row = 2
    col = 5
    worksheet.write(row, col, none, cell_format1)
    row += 1
    worksheet.write(row, col, rare, cell_format1)
    row += 1
    worksheet.write(row, col, occ, cell_format1)
    row += 1
    worksheet.write(row, col, freq, cell_format1)
    row += 1
    worksheet.write(row, col, per, cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(F3:F7)", cell_format1)

    # Column G (BRAT estimated Capacity)

    none = 0.0
    rare = 0.0
    occ = 0.0
    freq = 0.0
    per = 0.0

    split_input = stream_network.split(";")
    fields = ['oCC_EX', "mCC_EX_CT"]
    for streams in split_input:
        with arcpy.da.SearchCursor(streams, fields) as cursor:
            for capacity, dam_complex_size in cursor:
                if capacity == 0:
                    none += float(dam_complex_size)
                elif capacity <= 1:
                    rare += float(dam_complex_size)
                elif capacity <= 5:
                    occ += float(dam_complex_size)
                elif capacity <= 15:
                    freq += float(dam_complex_size)
                else:
                    per += float(dam_complex_size)
    row = 2
    col = 6
    worksheet.write(row, col, none, cell_format1)
    row += 1
    worksheet.write(row, col, rare, cell_format1)
    row += 1
    worksheet.write(row, col, occ, cell_format1)
    row += 1
    worksheet.write(row, col, freq, cell_format1)
    row += 1
    worksheet.write(row, col, per, cell_format1)
    row += 1
    worksheet.write(row, col, "=SUM(G3:G7)", cell_format1)

    # Column H (Average Surveyed Dam Density)

    row = 2
    col = 7
    worksheet.write(row, col, "=F3/C3", cell_format2)
    row += 1
    worksheet.write(row, col, "=F4/C4", cell_format2)
    row += 1
    worksheet.write(row, col, "=F5/C5", cell_format2)
    row += 1
    worksheet.write(row, col, "=F6/C6", cell_format2)
    row += 1
    worksheet.write(row, col, "=F7/C7", cell_format2)
    row += 1
    worksheet.write(row, col, "=F8/C8", cell_format2)

    # Column I (Average Surveyed Dam Density)

    row = 2
    col = 8
    worksheet.write(row, col, "=G3/C3", cell_format2)
    row += 1
    worksheet.write(row, col, "=G4/C4", cell_format2)
    row += 1
    worksheet.write(row, col, "=G5/C5", cell_format2)
    row += 1
    worksheet.write(row, col, "=G6/C6", cell_format2)
    row += 1
    worksheet.write(row, col, "=G7/C7", cell_format2)
    row += 1
    worksheet.write(row, col, "=G8/C8", cell_format2)

    # Column J (Percent Modeled Capacity)

    row = 2
    col = 9
    worksheet.write(row, col, "=IF(I3>0,H3/I3,\"N/A\")", percent2)
    row += 1
    worksheet.write(row, col, "=IF(I4>0,H4/I4,\"N/A\")", percent2)
    row += 1
    worksheet.write(row, col, "=IF(I5>0,H5/I5,\"N/A\")", percent2)
    row += 1
    worksheet.write(row, col, "=IF(I6>0,H6/I6,\"N/A\")", percent2)
    row += 1
    worksheet.write(row, col, "=IF(I7>0,H7/I7,\"N/A\")", percent2)
    row += 1
    worksheet.write(row, col, "=IF(I8>0,H8/I8,\"N/A\")", percent2)

    # Column K (Electivity Index)

    row = 2
    col = 10
    worksheet.write(row, col, "=(F3/$F$8) / E3", cell_format2)
    row += 1
    worksheet.write(row, col, "=(F4/$F$8) / E4", cell_format2)
    row += 1
    worksheet.write(row, col, "=(F5/$F$8) / E5", cell_format2)
    row += 1
    worksheet.write(row, col, "=(F6/$F$8) / E6", cell_format2)
    row += 1
    worksheet.write(row, col, "=(F7/$F$8) / E7", cell_format2)
    row += 1
    worksheet.write(row, col, "N/A", cell_format2)


def write_header(worksheet, watershed_name):
    row = 0
    col = 0
    worksheet.write(row, col, watershed_name)
    row += 1
    col += 1
    worksheet.write(row, col, "Stream Length (Km)")
    col += 1
    worksheet.write(row, col, "Stream Length (mi)")
    col += 1
    worksheet.write(row, col, "Percent")


def create_folder_structure(project_folder, summary_prods_folder):
    make_folder(project_folder, summary_prods_folder)
    
    ai_folder = os.path.join(summary_prods_folder, "AI")
    png_folder = os.path.join(summary_prods_folder, "PNG")
    pdf_folder = os.path.join(summary_prods_folder, "PDF")
    kmz_folder = os.path.join(summary_prods_folder, "KMZ")
    lpk_folder = os.path.join(summary_prods_folder, "LPK")

    ai_files = []
    png_files = []
    pdf_files = []
    kmz_files = []
    lpk_files = []

    for root, dirs, files in os.walk(project_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if "\\SummaryProducts\\" in root:
                # We don't want to add anything that's already in our summary product area
                pass
            elif file.endswith(".ai"):
                ai_files.append(file_path)
            elif file.endswith(".png"):
                png_files.append(file_path)
            elif file.endswith(".pdf"):
                pdf_files.append(file_path)
            elif file.endswith(".kmz"):
                kmz_files.append(file_path)
            elif file.endswith(".lpk"):
                lpk_files.append(file_path)

    
    copy_all_files(summary_prods_folder, ai_folder, ai_files)
    copy_all_files(summary_prods_folder, kmz_folder, kmz_files)
    copy_all_files(summary_prods_folder, lpk_folder, lpk_files)
    copy_to_input_output_structure(summary_prods_folder, png_folder, png_files)
    copy_to_input_output_structure(summary_prods_folder, pdf_folder, pdf_files)


def copy_to_input_output_structure(folder_base, files):
    """
    Copies our files into a "inputs, intermediates, outputs" folder structure
    :param folder_base: The base folder that we want to copy our files into
    :param files: A list of files that we want to copy
    :return:
    """
    output_folder = make_folder(folder_base, "Outputs")
    inputs_folder = make_folder(folder_base, "Inputs")
    intermed_folder = make_folder(folder_base, "Intermediates")

    for file in files:
        if "\\Inputs\\" in file:
            shutil.copy(file, inputs_folder)
        elif "\\01_Intermediates\\" in file:
            shutil.copy(file, intermed_folder)
        elif "\\02_Analyses\\" in file:
            shutil.copy(file, output_folder)
        else:
            shutil.copy(file, folder_base)


def copy_all_files(summary_folder, new_folder, files):
    # only make these folders if specific outputs need to be copied in
    if len(files)>0:
        make_folder(summary_folder, new_folder)
    for file in files:
        shutil.copy(file, new_folder)


if __name__ == "__main__":
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6])
