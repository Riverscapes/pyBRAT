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
import os
import xlsxwriter
import arcpy

def main(project_folder, stream_network, watershed_name, excel_file_name=None):
    """
    Our main function
    :param project_folder: The BRAT Project that we want to collect the summary products for
    :return:
    """
    if excel_file_name is None:
        excel_file_name = "Stats_Summary"
    if not excel_file_name.endswith(".xlsx"):
        excel_file_name += ".xlsx"

    summary_prods_folder = make_folder(project_folder, "Summary_Products")

    create_folder_structure(project_folder, summary_prods_folder)

    create_excel_file(excel_file_name, stream_network, summary_prods_folder, watershed_name)


def create_excel_file(excel_file_name, stream_network, summary_prods_folder, watershed_name):
    workbook = xlsxwriter.Workbook(os.path.join(summary_prods_folder, excel_file_name))
    write_capacity_sheets(workbook, stream_network, watershed_name)
    workbook.close()


def write_capacity_sheets(workbook, stream_network, watershed_name):
    exist_complex_worksheet = workbook.add_worksheet("Existing Dam Complex Size")
    exist_build_cap_worksheet = workbook.add_worksheet("Existing Dam Building Capacity")
    hist_complex_worksheet = workbook.add_worksheet("Historic Dam Complex Size")
    hist_build_cap_worksheet = workbook.add_worksheet("Historic Dam Building Capacity")
    hist_vs_exist_worksheet = workbook.add_worksheet("Existing and Historic Capacity")

    write_exist_complex_worksheet(exist_complex_worksheet, stream_network, watershed_name, workbook)
    write_exist_build_cap_worksheet(exist_build_cap_worksheet, stream_network, watershed_name, workbook)
    write_hist_complex_worksheet()


# Writing the side headers for complex size
def write_categories_complex(worksheet):
    column_sizeA = worksheet.set_column('A:A', 30)
    row = 2
    col = 0
    worksheet.write(row, col, "No Dams", column_sizeA)
    row += 1
    worksheet.write(row, col, "Single Dam")
    row += 1
    worksheet.write(row, col, "Small Complex (1-3 Dams)")
    row += 1
    worksheet.write(row, col, "Medium Complex (3-5 dams)")
    row += 1
    worksheet.write(row, col, "Large Complex (>5 dams)")
    row += 1
    worksheet.write(row, col, "Total")


# Writing the side headers for build capacity
def write_categories_build_cap(worksheet):
    column_sizeA = worksheet.set_column('A:A', 30)
    row = 2
    col = 0
    worksheet.write(row, col, "None:0", column_sizeA)
    row += 1
    worksheet.write(row, col, "Rare: < 1")
    row += 1
    worksheet.write(row, col, "Occasional: 2 - 5")
    row += 1
    worksheet.write(row, col, "Frequent: 6 - 15 ")
    row += 1
    worksheet.write(row, col, "Pervasive: 16 - 40")
    row += 1
    worksheet.write(row, col, "Total")


# Writing the data into the worksheet
def write_data(data1, data2, data3, data4, data5, total_length, worksheet, workbook):
    KM_TO_MILES_RATIO = 0.6214
    # Set the column size.
    column_sizeB = worksheet.set_column('B:B', 20)
    column_sizeC = worksheet.set_column('C:C', 20)
    # Adds the percent sign and puts it in percent form.
    percent_format = workbook.add_format({'num_format': '0.00%'})
    percent = worksheet.set_column('D:D', 10, percent_format)

    col = 1
    row = 2
    worksheet.write(row, col, data1, column_sizeB)
    col += 1
    worksheet.write(row, col, data1 * KM_TO_MILES_RATIO, column_sizeC)
    col += 1
    worksheet.write(row, col, data1 / total_length, percent)

    col = 1
    row = 3
    worksheet.write(row, col, data2)
    col += 1
    worksheet.write(row, col, data2 * KM_TO_MILES_RATIO)
    col += 1
    worksheet.write(row, col, data2 / total_length, percent)

    col = 1
    row = 4
    worksheet.write(row, col, data3)
    col += 1
    worksheet.write(row, col, data3 * KM_TO_MILES_RATIO)
    col += 1
    worksheet.write(row, col, data3 / total_length, percent)

    col = 1
    row = 5
    worksheet.write(row, col, data4)
    col += 1
    worksheet.write(row, col, data4 * KM_TO_MILES_RATIO)
    col += 1
    worksheet.write(row, col, data4 / total_length, percent)

    col = 1
    row = 6
    worksheet.write(row, col, data5)
    col += 1
    worksheet.write(row, col, data5 * KM_TO_MILES_RATIO)
    col += 1
    worksheet.write(row, col, data5 / total_length, percent)

    # Calculating Total for Stream Length(Km)
    worksheet.write(7, 1, '=SUM(B3:B7)')
    # Calculating Total for Stream Length (mi)
    worksheet.write(7, 2, '=SUM(C3:C7)')
    # Calculating total percentage.
    worksheet.write(7, 3, '=SUM(D3:D7)', percent)


# Getting the data for Complex Size
def search_cursor(fields, data1, data2, data3, data4, data5, total, stream_network, is_complex, worksheet, workbook):
    if is_complex:
        with arcpy.da.SearchCursor(stream_network, fields) as cursor:
            for length, ex_dam_complex_size in cursor:
                total += length
                if ex_dam_complex_size == 0:
                    data1 += length
                elif ex_dam_complex_size <= 1:
                    data2 += length
                elif ex_dam_complex_size <= 3:
                    data3 += length
                elif ex_dam_complex_size <= 5:
                    data4 += length
                else:
                    data5 += length
    else:
        with arcpy.da.SearchCursor(stream_network, fields) as cursor:
            for length, ex_build_cap_size in cursor:
                total += length
                if ex_build_cap_size == 0:
                    data1 += length
                elif ex_build_cap_size <= 1:
                    data2 += length
                elif ex_build_cap_size <= 5:
                    data3 += length
                elif ex_build_cap_size <= 15:
                    data4 += length
                elif ex_build_cap_size <= 40:
                    data5 += length
    write_data(data1, data2, data3, data4, data5, total, worksheet, workbook)


def write_exist_complex_worksheet(exist_complex_worksheet, stream_network, watershed_name, workbook):
    is_complex = True

    write_header(exist_complex_worksheet, watershed_name)
    write_categories_complex(exist_complex_worksheet)

    fields = ['SHAPE@Length', "mCC_EX_CT"]
    no_dams_length = 0.0
    one_dam_length = 0.0
    some_dams_length = 0.0
    more_dams_length = 0.0
    many_dams_length = 0.0
    total_length = 0.0

    search_cursor(fields, no_dams_length, one_dam_length, some_dams_length, more_dams_length, many_dams_length, total_length, stream_network, is_complex, exist_complex_worksheet, workbook)

    # Writing the chart
    # chart = workbook.add_chart({'type': 'bar'})
    # chart.add_series({
    #    'name': '=Sheet1!$A$1',
    #    'categories': '=Sheet1!$A$3:$A$7',
    #    'values': '=Sheet1!$C$3:$C$7',
    # })

    # chart.add_series({
    #    'name': ['Sheet1', 0, 2],
    #   'categories': ['Sheet1', 1, 0, 6, 0],
    #    'values': ['Sheet1', 1, 2, 6, 2],
    # })

    # chart.set_title({'name': '=Sheet!$A$1'})
    # exist_complex_worksheet.insert_chart('G3', chart)


def write_exist_build_cap_worksheet(exist_build_cap_worksheet, stream_network, watershed_name, workbook):
    is_complex = False
    write_header(exist_build_cap_worksheet, watershed_name)

    write_categories_build_cap(exist_build_cap_worksheet)

    fields = ['SHAPE@Length', "oCC_EX"]
    none = 0.0
    rare = 0.0
    occasional = 0.0
    frequent = 0.0
    pervasive = 0.0
    total_length = 0.0

    search_cursor(fields, none, rare, occasional, frequent, pervasive, total_length, stream_network, is_complex, exist_build_cap_worksheet, workbook)


def write_hist_complex_worksheet(hist_complex_worksheet, stream_network, watershed_name, workbook):
    is_complex = True
    write_header(hist_complex_worksheet, watershed_name)
    write_categories_complex(hist_complex_worksheet)

    fields = ['SHAPE@Length', "mCC_HPE_CT"]
    no_dams_length = 0.0
    one_dam_length = 0.0
    some_dams_length = 0.0
    more_dams_length = 0.0
    many_dams_length = 0.0
    total_length = 0.0

    #TODO: FINISH HISTORIC COMPLEX

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
    ai_folder = make_folder(summary_prods_folder, "AI")
    png_folder = make_folder(summary_prods_folder, "PNG")
    pdf_folder = make_folder(summary_prods_folder, "PDF")
    kmz_folder = make_folder(summary_prods_folder, "KMZ")

    ai_files = []
    png_files = []
    pdf_files = []
    kmz_files = []
    for root, dirs, files in os.walk(project_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if "\\Summary_Products\\" in root:
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

    copy_all_files(ai_folder, ai_files)
    copy_all_files(kmz_folder, kmz_files)
    copy_to_input_output_structure(png_folder, png_files)
    copy_to_input_output_structure(pdf_folder, pdf_files)


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


def copy_all_files(folder, files):
    for file in files:
        shutil.copy(file, folder)