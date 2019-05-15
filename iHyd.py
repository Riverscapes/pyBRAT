# -------------------------------------------------------------------------------
# Name:        iHYD
# Purpose:     Adds the hydrologic attributes to the BRAT input table
#
# Author:      Jordan
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
import numpy as np
import os
import sys
from SupportingFunctions import make_layer, make_folder, find_available_num_prefix, find_relative_path
import XMLBuilder
reload(XMLBuilder)
XMLBuilder = XMLBuilder.XMLBuilder

def main(
    in_network,
    region,
    in_elev,
    in_slope,
    in_precip,
    Qlow_eqtn = None,
    Q2_eqtn = None):

    scratch = 'in_memory'

    arcpy.env.overwriteOutput = True

    # set basin specific variables
    ELEV_FT = float(in_elev)
    SLOPE_PCT = float(in_slope)
    PRECIP_IN = float(in_precip)

    # create segid array for joining output to input network
    segid_np = arcpy.da.FeatureClassToNumPyArray(in_network, "ReachID")
    segid = np.asarray(segid_np, np.int64)

    # create array for input network drainage area ("iGeo_DA")
    DA_array = arcpy.da.FeatureClassToNumPyArray(in_network, "iGeo_DA")
    DA = np.asarray(DA_array, np.float32)

    # # create array for input network elevation
    # EL_array = arcpy.da.FeatureClassToNumPyArray(in_network, "iGeo_ElMin")
    # EL = np.asarray(EL_array, np.float32)

    # convert drainage area (in square kilometers) to square miles
    # note: this assumes that streamflow equations are in US customary units (e.g., inches, feet)
    DA_SQM = np.zeros_like(DA)
    DA_SQM = DA * 0.3861021585424458

    # create Qlow and Q2
    Qlow = np.zeros_like(DA)
    Q2 = np.zeros_like(DA)

    arcpy.AddMessage("Adding Qlow and Q2 to network...")

    if region is None:
        region = 0

    # --regional curve equations for Qlow (baseflow) and Q2 (annual peak streamflow)--
    # # # Add in regional curve equations here # # #
    if Qlow_eqtn is not None:
        Qlow = eval(Qlow_eqtn)
    elif float(region) == 1:  # North Coast
        Qlow = (10**-2.8397) * (DA_SQM**1.2021) * (SLOPE_PCT**1.1394)
    elif float(region) == 2:  # Lahontan
        Qlow = (10**-12.6104) * (DA_SQM**1.0762) * (ELEV_FT**2.3032) * (PRECIP_IN**2.1072)
    elif float(region) == 3:  # Sierra Nevada
        Qlow = (10**-7.2182) * (DA_SQM**1.013) * (ELEV_FT**01.1236) * (PRECIP_IN**1.4483)
    elif float(region) == 4:  # Central Coast
        Qlow = (10**-9.0231) * (DA_SQM**1.9398) * (SLOPE_PCT**3.9156)
    elif float(region) == 6: # Desert
        Qlow = (10**0.4406) * (DA_SQM**0.7301)
    else:
        arcpy.AddMessage("WARNING: Region is not part of project area.  Quitting iHyd script")
        return

    if Q2_eqtn is not None:
        Q2 = eval(Q2_eqtn)
    elif float(region) == 1:  # North Coast
        Q2 = 1.82 * (DA_SQM**0.904) * (PRECIP_IN**0.983)
    elif float(region) == 2:  # Lahontan
        Q2 = 0.0865 * (DA_SQM**0.736)*(PRECIP_IN**1.59)
    elif float(region) == 3:  # Sierra Nevada
        Q2 = 2.43 * (DA_SQM**0.924)*(ELEV_FT**-0.646)*(PRECIP_IN**2.06)
    elif float(region) == 4: # Central Coast
        Q2 = 0.00459 * (DA_SQM ** 0.856) * (PRECIP_IN**2.58)
    elif float(region) == 6: # Desert
        Q2 = 10.3 * (DA_SQM ** 0.506)
    else:
        arcpy.AddMessage("WARNING: Region is not part of project area.  Quitting iHyd script")
        return

    # save segid, Qlow, Q2 as single table
    columns = np.column_stack((segid, Qlow, Q2))
    tmp_table = os.path.dirname(in_network) + "/ihyd_Q_Table.txt"
    np.savetxt(tmp_table, columns, delimiter = ",", header = "ReachID, iHyd_QLow, iHyd_Q2", comments = "")
    ihyd_table = scratch + "/ihyd_table"
    arcpy.CopyRows_management(tmp_table, ihyd_table)

    # join Qlow and Q2 output to the flowline network
    # create empty dictionary to hold input table field values
    tblDict = {}
    # add values to dictionary
    with arcpy.da.SearchCursor(ihyd_table, ['ReachID', "iHyd_QLow", "iHyd_Q2"]) as cursor:
        for row in cursor:
            tblDict[row[0]] = [row[1], row[2]]
    # check for and delete if output fields already included in flowline network
    remove_existing_output(in_network)
    # populate flowline network out field
    arcpy.AddField_management(in_network, "iHyd_QLow", 'DOUBLE')
    arcpy.AddField_management(in_network, "iHyd_Q2", 'DOUBLE')
    with arcpy.da.UpdateCursor(in_network, ['ReachID', "iHyd_QLow", "iHyd_Q2"]) as cursor:
        for row in cursor:
            try:
                aKey = row[0]
                row[1] = tblDict[aKey][0]
                row[2] = tblDict[aKey][1]
                cursor.updateRow(row)
            except:
                pass
    tblDict.clear()

    # delete temporary table
    arcpy.Delete_management(tmp_table)

    # check that Q2 is greater than Qlow
    # if not, re-calculate Q2 as Qlow + 0.001
    with arcpy.da.UpdateCursor(in_network, ["iHyd_QLow", "iHyd_Q2"]) as cursor:
        for row in cursor:
            if row[1] < row[0]:
                row[1] = row[0] + 0.001
            else:
                pass
            cursor.updateRow(row)

    arcpy.AddMessage("Adding stream power to network...")

    # calculate Qlow and Q2 stream power
    # where stream power = density of water (1000 kg/m3) * acceleration due to gravity (9.80665 m/s2) * discharge (m3/s) * channel slope
    # note: we assume that discharge ("iHyd_QLow", "iHyd_Q2") was calculated in cubic feet per second and handle conversion to cubic
    #       meters per second (e.g., "iHyd_QLow" * 0.028316846592
    arcpy.AddField_management(in_network, "iHyd_SPLow", "DOUBLE")
    arcpy.AddField_management(in_network, "iHyd_SP2", "DOUBLE")
    with arcpy.da.UpdateCursor(in_network, ["iGeo_Slope", "iHyd_QLow", "iHyd_SPLow", "iHyd_Q2", "iHyd_SP2"]) as cursor:
        for row in cursor:
            if row[0] < 0.001:
                slope = 0.001
            else:
                slope = row[0]
            row[2] = (1000 * 9.80665) * slope * (row[1] * 0.028316846592)
            row[4] = (1000 * 9.80665) * slope * (row[3] * 0.028316846592)
            cursor.updateRow(row)

    makeLayers(in_network)

    # add equations to XML
    #if Qlow_eqtn is not None and Q2_eqtn is not None and region is not None:
    #    xml_add_equations(in_network, region, Qlow_eqtn, Q2_eqtn)



def remove_existing_output(in_network):
    if "iHyd_QLow" in [field.name for field in arcpy.ListFields(in_network)]:    
        arcpy.DeleteField_management(in_network, "iHyd_Qlow")
    if "iHyd_Q2" in [field.name for field in arcpy.ListFields(in_network)]:
        arcpy.DeleteField_management(in_network, "iHyd_Q2")
    if "iHyd_SPLow" in [field.name for field in arcpy.ListFields(in_network)]:
        arcpy.DeleteField_management(in_network, "iHyd_SPLow")
    if "iHyd_SP2" in [field.name for fields in arcpy.ListFields(in_network)]:
        arcpy.DeleteField_management(in_network, "iHyd_SP2")



def makeLayers(inputNetwork):
    """
    Makes the layers for the modified output
    :param inputNetwork: The path to the network that we'll make a layer from
    :return:
    """
    arcpy.AddMessage("Making layers...")
    intermediates_folder = os.path.dirname(inputNetwork)
    hydrology_folder_name = find_available_num_prefix(intermediates_folder) + "_Hydrology"
    hydrology_folder = make_folder(intermediates_folder, hydrology_folder_name)

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')

    highflowSymbology = os.path.join(symbologyFolder, "Highflow_StreamPower.lyr")
    baseflowSymbology = os.path.join(symbologyFolder, "Baseflow_StreamPower.lyr")

    make_layer(hydrology_folder, inputNetwork, "Highflow Stream Power", highflowSymbology, is_raster=False)
    make_layer(hydrology_folder, inputNetwork, "Baseflow Stream Power", baseflowSymbology, is_raster=False)


def xml_add_equations(in_network, region, Qlow_eqtn, Q2_eqtn):
    # get project folder path from input network
    proj_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(in_network))))

    # open xml
    xml_file_path = os.path.join(proj_path, "project.rs.xml")
    if not os.path.exists(xml_file_path):
        raise Exception("XML file for project does not exist. Return to Step 1: BRAT table to create XML.")
    xml_file = XMLBuilder(xml_file_path)

    # find input network XML element
    in_network_rel_path = find_relative_path(in_network, proj_path)                                    
    path_element = xml_file.find_by_text(in_network_rel_path)

    # find intermediates element for input network
    intermediates_element = xml_file.find_element_parent(xml_file.find_element_parent(path_element))
    if intermediates_element is None:
        raise Exception("Equations could not be added because parent element 'Intermediates' not found in XML.")

    # add regional curves element within intermediates
    ihyd_element = xml_file.add_sub_element(intermediates_element, name = "Regional Curves", text= "Equations for estimating streamflow")   

    # add region element to XML if specified
    if region is not 0:
        xml_file.add_sub_element(ihyd_element, "Hydrological region", str(region))

    # add base flow equation to XML if specified or using generic
    if Qlow_eqtn is None and region is 0:
        xml_file.add_sub_element(ihyd_element, name = "Baseflow equation", text = "(DA_SQM ** 0.2098) + 1")
    elif Q2_eqtn is None and region is not 0:
        xml_file.add_sub_element(ihyd_element, name = "Baseflow equation", text = "Not specified - see iHyd code.")
    else:
        xml_file.add_sub_element(ihyd_element, name = "Baseflow equation", text = str(Qlow_eqtn))

    # add high flow equation to XML if specified or using generic
    if Q2_eqtn is None and region is 0:
        xml_file.add_sub_element(ihyd_element, name = "Highflow equation", text = "14.7 * (DA_SQM ** 0.815)")
    elif Q2_eqtn is None and region is not 0:
        xml_file.add_sub_element(ihyd_element, name = "Highflow equation", text = "Not specified - see iHyd code.")
    else:
        xml_file.add_sub_element(ihyd_element,name = "Highflow equation", text = str(Q2_eqtn))
    
    xml_file.write()

    
if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
    )
