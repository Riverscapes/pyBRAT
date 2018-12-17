import shutil
from SupportingFunctions import make_folder
import os

def main(project_folder):
    summary_prods_folder = make_folder(project_folder, "Summary_Products")
    ai_folder = make_folder(summary_prods_folder, "AI")
    png_folder = make_folder(summary_prods_folder, "PNG")
    pdf_folder = make_folder(summary_prods_folder, "PDF")

    png_output_folder = make_folder(png_folder, "Outputs")
    png_inputs_folder = make_folder(png_folder, "Inputs")
    png_intermediates_folder = make_folder(png_folder, "Intermediates")

    pdf_output_folder = make_folder(pdf_folder, "Outputs")
    pdf_inputs_folder = make_folder(pdf_folder, "Inputs")
    pdf_intermediates_folder = make_folder(pdf_folder, "Intermediates")

    ai_files = []
    png_files = []
    pdf_files = []
    for root, dirs, files in os.walk(project_folder):
        for file in files:
            if "\\Summary_Products\\" in root:
                #We don't want to add anything that's already in our summary product area
                pass
            elif file.endswith(".ai"):
                ai_files.append(os.path.join(root, file))
            elif file.endswith(".png"):
                png_files.append(os.path.join(root, file))
            elif file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))

    copy_ai_files(ai_folder, ai_files)
    copy_to_input_output_structure(png_output_folder, png_inputs_folder, png_intermediates_folder, png_files)
    copy_to_input_output_structure(pdf_output_folder, pdf_inputs_folder, pdf_intermediates_folder, pdf_files)


def copy_to_input_output_structure(output_folder, input_folder, intermed_folder, files):
    for file in files:
        if "\\Inputs\\" in file:
            shutil.copy(file, input_folder)
        elif "\\01_Intermediates\\" in file:
            shutil.copy(file, intermed_folder)
        else:
            shutil.copy(file, output_folder)


def copy_ai_files(ai_folder, ai_files):
    for file in ai_files:
        shutil.copy(file, ai_folder)