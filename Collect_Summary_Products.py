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

def main(project_folder, stream_network, excel_file_name=None):
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

    create_excel_file(excel_file_name, stream_network, summary_prods_folder)


def create_excel_file(excel_file_name, stream_network, summary_prods_folder):
    workbook = xlsxwriter.Workbook(os.path.join(summary_prods_folder, excel_file_name))
    worksheet = workbook.add_worksheet("My Worksheet")
    worksheet.write(0, 0, "sup")
    workbook.close()
    arcpy.AddMessage(excel_file_name)


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