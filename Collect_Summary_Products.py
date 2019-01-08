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

def main(project_folder):
    summary_prods_folder = make_folder(project_folder, "Summary_Products")
    ai_folder = make_folder(summary_prods_folder, "AI")
    png_folder = make_folder(summary_prods_folder, "PNG")
    pdf_folder = make_folder(summary_prods_folder, "PDF")
    kmz_folder = make_folder(summary_prods_folder, "KMZ")

    png_output_folder = make_folder(png_folder, "Outputs")
    png_inputs_folder = make_folder(png_folder, "Inputs")
    png_intermediates_folder = make_folder(png_folder, "Intermediates")

    pdf_output_folder = make_folder(pdf_folder, "Outputs")
    pdf_inputs_folder = make_folder(pdf_folder, "Inputs")
    pdf_intermediates_folder = make_folder(pdf_folder, "Intermediates")

    ai_files = []
    png_files = []
    pdf_files = []
    kmz_files = []
    for root, dirs, files in os.walk(project_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if "\\Summary_Products\\" in root:
                #We don't want to add anything that's already in our summary product area
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
    copy_to_input_output_structure(png_folder, png_output_folder, png_inputs_folder, png_intermediates_folder, png_files)
    copy_to_input_output_structure(pdf_folder, pdf_output_folder, pdf_inputs_folder, pdf_intermediates_folder, pdf_files)


def copy_to_input_output_structure(folder_base, output_folder, input_folder, intermed_folder, files):
    for file in files:
        if "\\Inputs\\" in file:
            shutil.copy(file, input_folder)
        elif "\\01_Intermediates\\" in file:
            shutil.copy(file, intermed_folder)
        elif "\\02_Analyses\\" in file:
            shutil.copy(file, output_folder)
        else:
            shutil.copy(file, folder_base)


def copy_all_files(folder, files):
    for file in files:
        shutil.copy(file, folder)