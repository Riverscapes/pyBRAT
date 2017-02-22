# -------------------------------------------------------------------------------
# Name:        BRAT Project Builder
# Purpose:     Gathers and structures the inputs for a BRAT project
#
# Author:      Jordan Gilbert
#
# Created:     09/25/2015
# Latest Update: 02/08/2017
# Copyright:   (c) Jordan Gilbert 2017
# Licence:     This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
#              License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/.
# -------------------------------------------------------------------------------

# import modules
import os
import arcpy
import shutil
import sys
import string


def main(projPath, ex_veg, hist_veg, network, DEM, landuse, valley, road, rr, canal):
    """Create a BRAT project and populate the inputs"""

    arcpy.env.overwriteOutput = True

    if not os.path.exists(projPath):
        os.mkdir(projPath)

    if os.getcwd() is not projPath:
        os.chdir(projPath)

    set_structure(projPath)

    # add the existing veg inputs to project
    inex_veg = ex_veg.split(";")
    os.chdir(projPath + "/01_Inputs/01_Ex_Veg/")
    i = 1
    for x in range(len(inex_veg)):
        if not os.path.exists("Ex_Veg_" + str(i)):
            os.mkdir("Ex_Veg_" + str(i))
        if not os.path.exists("Ex_Veg_" + str(i) + "/" + os.path.basename(inex_veg[x])):
            src = string.replace(inex_veg[x], "'", "")
            shutil.copytree(src, "Ex_Veg_" + str(i) + "/" + os.path.basename(inex_veg[x]))
        i += 1

    # add the historic veg inputs to project
    inhist_veg = hist_veg.split(";")
    os.chdir(projPath + "/01_Inputs/02_Hist_Veg/")
    i = 1
    for x in range(len(inhist_veg)):
        if not os.path.exists("Hist_Veg_" + str(i)):
            os.mkdir("Hist_Veg_" + str(i))
        if not os.path.exists("Hist_Veg_" + str(i) + "/" + os.path.basename(inhist_veg[x])):
            src = string.replace(inhist_veg[x], "'", "")
            shutil.copytree(src, "Hist_Veg_" + str(i) + "/" + os.path.basename(inhist_veg[x]))
        i += 1

    # add the network inputs to project
    innetwork = network.split(";")
    os.chdir(projPath + "/01_Inputs/03_Network/")
    i = 1
    for x in range(len(innetwork)):
        if not os.path.exists("Network_" + str(i)):
            os.mkdir("Network_" + str(i))
        arcpy.Copy_management(innetwork[x], "Network_" + str(i) + "/" + os.path.basename(innetwork[x]))
        i += 1

    # add the DEM inputs to the project
    inDEM = DEM.split(";")
    os.chdir(projPath + "/01_Inputs/04_Topo/")
    i = 1
    for x in range(len(inDEM)):
        if not os.path.exists("DEM_" + str(i)):
            os.mkdir("DEM_" + str(i))
        arcpy.CopyRaster_management(inDEM[x], "DEM_" + str(i) + "/" + os.path.basename(inDEM[x]))
        i += 1

    # add landuse raster to the project
    if landuse is not None:
        inlanduse = landuse.split(";")
        os.chdir(projPath + "/01_Inputs/05_Conflict/05_Land_Use/")
        i = 1
        for x in range(len(inlanduse)):
            if not os.path.exists("Land_Use_" + str(i)):
                os.mkdir("Land_Use_" + str(i))
            if os.path.basename(inlanduse[x]).endswith("evt"):
                if not os.path.exists("Land_Use_" + str(i) + "/" + os.path.basename(inlanduse[x])):
                    src = string.replace(inlanduse[x], "'", "")
                    shutil.copytree(src, "Land_Use_" + str(i) + "/" + os.path.basename(inlanduse[x]))
            else:
                arcpy.CopyRaster_management(inlanduse[x], "Land_Use_" + str(i) + "/" + os.path.basename(inlanduse[x]))

    # add the conflict inputs to the project
    if valley is not None:
        invalley = valley.split(";")
        os.chdir(projPath + "/01_Inputs/05_Conflict/01_Valley/")
        i = 1
        for x in range(len(invalley)):
            if not os.path.exists("Valley_" + str(i)):
                os.mkdir("Valley_" + str(i))
            arcpy.Copy_management(invalley[x], "Valley_" + str(i) + "/" + os.path.basename(invalley[x]))
            i += 1

    # add road layers to the project
    if road is not None:
        inroad = road.split(";")
        os.chdir(projPath + "/01_Inputs/05_Conflict/02_Roads/")
        i = 1
        for x in range(len(inroad)):
            if not os.path.exists("Roads_" + str(i)):
                os.mkdir("Roads_" + str(i))
            arcpy.Copy_management(inroad[x], "Roads_" + str(i) + "/" + os.path.basename(inroad[x]))
            i += 1

    # add railroad layers to the project
    if rr is not None:
        inrr = rr.split(";")
        os.chdir(projPath + "/01_Inputs/05_Conflict/03_Railroads/")
        i = 1
        for x in range(len(inrr)):
            if not os.path.exists("Railroads_" + str(i)):
                os.mkdir("Railroads_" + str(i))
            arcpy.Copy_management(inrr[x], "Railroads_" + str(i) + "/" + os.path.basename(inrr[x]))

    # add canal layers to the project
    if canal is not None:
        incanal = canal.split(";")
        os.chdir(projPath + "/01_Inputs/05_Conflict/04_Canals/")
        i = 1
        for x in range(len(incanal)):
            if not os.path.exists("Canals_" + str(i)):
                os.mkdir("Canals_" + str(i))
            arcpy.Copy_management(incanal[x], "Canals_" + str(i) + "/" + os.path.basename(incanal[x]))

    else:
        pass


def set_structure(projPath):
    """Sets up the folder structure for an RVD project"""

    if not os.path.exists(projPath):
        os.mkdir(projPath)

    if os.getcwd() is not projPath:
        os.chdir(projPath)

    if not os.path.exists("01_Inputs"):
        os.mkdir("01_Inputs")
    if not os.path.exists("02_Analyses"):
        os.mkdir("02_Analyses")
    os.chdir("01_Inputs")
    if not os.path.exists("01_Ex_Veg"):
        os.mkdir("01_Ex_Veg")
    if not os.path.exists("02_Hist_Veg"):
        os.mkdir("02_Hist_Veg")
    if not os.path.exists("03_Network"):
        os.mkdir("03_Network")
    if not os.path.exists("04_Topo"):
        os.mkdir("04_Topo")
    if not os.path.exists("05_Conflict"):
        os.mkdir("05_Conflict")
    os.chdir("05_Conflict")
    if not os.path.exists("01_Valley"):
        os.mkdir("01_Valley")
    if not os.path.exists("02_Roads"):
        os.mkdir("02_Roads")
    if not os.path.exists("03_Railroads"):
        os.mkdir("03_Railroads")
    if not os.path.exists("04_Canals"):
        os.mkdir("04_Canals")
    if not os.path.exists("05_Land_Use"):
        os.mkdir("05_Land_Use")
    os.chdir(projPath)

if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
        sys.argv[8],
        sys.argv[9],
        sys.argv[10])
