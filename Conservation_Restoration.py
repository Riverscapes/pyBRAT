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
import uuid
from SupportingFunctions import make_layer, make_folder, find_available_num


def main(projPath, in_network, out_name):

    arcpy.env.overwriteOutput = True

    out_network = os.path.dirname(in_network) + "/" + out_name + ".shp"
    arcpy.CopyFeatures_management(in_network, out_network)

    # check for oPBRC field and delete if exists
    fields = [f.name for f in arcpy.ListFields(out_network)]
    if "oPBRC" in fields:
        arcpy.DeleteField_management(out_network, "oPBRC")

    arcpy.AddField_management(out_network, "oPBRC", "TEXT", "", "", 100)

    fields = ['oPBRC', 'oVC_PT', 'oVC_EX', 'oCC_PT', 'oCC_EX', 'iPC_LowLU', 'iPC_ModLU', 'iPC_HighLU', 'iPC_VLowLU']

    with arcpy.da.UpdateCursor(out_network, fields) as cursor:
        for row in cursor:
            # 'oVC_PT' Occasional, Frequent or Pervasive
            # 'oCC_PT' None or Rare
            if row[1] > 1 and row[3] <= 1:
                row[0] = 'Naturally Unsuitable: Hydrologically Limited'
            # 'OVC_PT' None or Rare
            elif row[1] <= 1:
                row[0] = 'Naturally Unsuitable: Vegetation Limited'
            # 'iPC_HighLU' (i.e., Developed) > 50 or  'iPC_LowLU' + 'iPC_ModLU' (i.e., Agriculture) > 50
            elif row[5] + row[6] > 40 or row[7] > 40:
                # 'oCC_PT' Frequent or Pervasive
                # 'oCC_EX' None, Rare or Occasional
                if row[3] >= 5 and row[4] < 5:
                    row[0] = 'Unsuitable: Anthropogenically Limited'
                # todo: ask SS and WM if this is really what we want to assign in instances where high landuse but frequent exisitng
                # 'oCC_PT' Pervasive
                # 'oCC_EX' Frequent
                elif row[3] >= 15 and row[4] >= 5 and row[4] < 15:
                    row[0] = 'Unsuitable: Anthropogenically Limited'
                # 'oCC_PT' Occasional
                # 'oCC_EX' None or Rare
                elif row[3] >= 1 and row[4] <= 1:
                    row[0] = 'Unsuitable: Anthropogenically Limited'
                else:
                    row[0] = 'Unsuitable: Anthropogenically Limited'
                    # row[0] = 'Need Categorical Definition: Highly Developed'
            # 'iPC_HighLU' (i.e., Developed) < 10 and 'iPC_VLowLU'(i.e., Natural) > 75
            elif row[8] > 75 and row[7] < 10:
                # 'oCC_PT' Frequent or Pervasive
                # 'oCC_EX' Frequent or Pervasive
                if row[3] >= 5 and row[4] >= 5:
                    row[0] = 'Immediate Returns: High Impact/Activity'
                # 'oCC_PT' Occasional
                # 'oCC_EX' Occasional
                elif row[3] > 1 and row[3] < 5 and row[4] > 1 and row[4] < 5:
                    row[0] = 'Immediate Returns: Moderate Impact/Activity'
                # 'oCC_PT' Frequent or Pervasive
                # 'oCC_EX' None, Rare, or Occasional
                elif row[3] >= 5 and row[4] < 5:
                    row[0] = 'Long-Term: High Potential, Short-Term: Moderate Impact'
                # 'oCC_PT' Occasional
                # 'oCC_EX' None or Rare
                elif row[3] > 1 and row[3] < 5 and row[4] <= 1:
                    row[0] = 'Long-Term: Moderate Potential, Short-Term: Unsuitable'
                # 'oCC_PT' Occasional
                # 'oCC_EX' Frequent or Pervasive
                elif row[3] > 1 and row[3] < 5 and row[4] >= 5:
                    row[0] = 'Immediate Returns: High Impact/Activity'
                else:
                    row[0] = 'Need Categorical Definition: Low Developed'
            else:
                # todo: this is more or less a 'best option' placeholder and should re-visit and create additional category
                row[0] = 'Long-Term: Moderate Potential, Short-Term: Unsuitable'
            cursor.updateRow(row)

    addxmloutput(projPath, in_network, out_network)

    makeLayers(out_network)

    return out_network


def addxmloutput(projPath, in_network, out_network):
    """add the capacity output to the project xml file"""

    # xml file
    xmlfile = projPath + "/project.rs.xml"

    # make sure xml file exists
    if not os.path.exists(xmlfile):
        raise Exception("xml file for project does not exist. Return to table builder tool.")

    # open xml and add output
    exxml = projectxml.ExistingXML(xmlfile)

    realizations = exxml.rz.findall("BRAT")
    for i in range(len(realizations)):
        a = realizations[i].findall(".//Path")
        for j in range(len(a)):
            if os.path.abspath(a[j].text) == os.path.abspath(in_network[in_network.find("02_Analyses"):]):
                outrz = realizations[i]

    exxml.addOutput("BRAT Analysis", "Vector", "BRAT Management Output", out_network[out_network.find("02_Analyses"):],
                    outrz, guid=getUUID())

    exxml.write()



def makeLayers(out_network):
    """
    Writes the layers
    :param out_network: The output network, which we want to make into a layer
    :return:
    """
    arcpy.AddMessage("Making layers...")
    analyses_folder = os.path.dirname(out_network)
    output_folder = make_folder(analyses_folder, find_available_num(analyses_folder) + "_Management")

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')
    managementLayer = os.path.join(symbologyFolder, "Beaver_Management_Zones_v2.lyr")
    managementLayer2 = os.path.join(symbologyFolder, "Dam_Building_Not_Likely.lyr")
    managementLayer3 = os.path.join(symbologyFolder, "Restoration_Conservation_Opportunities.lyr")

    make_layer(output_folder, out_network, "Beaver Management Zones", managementLayer, is_raster=False)
    make_layer(output_folder, out_network, "Unsuitable or Limited Opportunities", managementLayer2, is_raster=False)
    make_layer(output_folder, out_network, "Restoration or Conservation Opportunities", managementLayer3, is_raster=False)



def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])
