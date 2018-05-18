# -------------------------------------------------------------------------------
# Name:        Comb_FIS
# Purpose:     Runs the combined FIS for the BRAT input table
#
# Author:      Jordan Gilbert
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import arcpy
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import os
import sys
import projectxml
import uuid
import xml.etree.ElementTree as ET


def main(
    projPath,
    in_network,
    max_DA_thresh,
    out_name):

    scratch = 'in_memory'

    output_folder = os.path.dirname(os.path.dirname(in_network))
    analyses_folder = makeFolder(output_folder, "02_Analyses")
    if out_name.endswith('.shp'):
        out_network = os.path.join(analyses_folder, out_name)
    else:
        out_network = os.path.join(analyses_folder, out_name + ".shp")

    if os.path.exists(out_network):
        arcpy.Delete_management(out_network)
    arcpy.CopyFeatures_management(in_network, out_network)

    # run the combined fis function for both potential and existing
    combFIS(out_network, 'pt', scratch, max_DA_thresh)
    combFIS(out_network, 'ex', scratch, max_DA_thresh)

    makeLayers(out_network, out_name)

    addxmloutput(projPath, in_network, out_network)


# combined fis function
def combFIS(in_network, model_run, scratch, max_DA_thresh):
    arcpy.env.overwriteOutput = True

    # get list of all fields in the flowline network
    fields = [f.name for f in arcpy.ListFields(in_network)]

    # set the carrying capacity and vegetation field depending on whether potential or existing run
    if model_run == 'pt':
        out_field = "oCC_PT"
        veg_field = "oVC_PT"
    else:
        out_field = "oCC_EX"
        veg_field = "oVC_EX"

    # check for oCC_* field in the network attribute table and delete if exists
    if out_field in fields:
        arcpy.DeleteField_management(in_network, out_field)

    # get arrays for fields of interest
    segid_np = arcpy.da.FeatureClassToNumPyArray(in_network, "ReachID")
    ovc_np = arcpy.da.FeatureClassToNumPyArray(in_network, veg_field)
    ihydsp2_np = arcpy.da.FeatureClassToNumPyArray(in_network, "iHyd_SP2")
    ihydsplow_np = arcpy.da.FeatureClassToNumPyArray(in_network, "iHyd_SPLow")
    igeoslope_np = arcpy.da.FeatureClassToNumPyArray(in_network, "iGeo_Slope")

    segid_array = np.asarray(segid_np, np.int64)
    ovc_array = np.asarray(ovc_np, np.float64)
    ihydsp2_array = np.asarray(ihydsp2_np, np.float64)
    ihydsplow_array = np.asarray(ihydsplow_np, np.float64)
    igeoslope_array = np.asarray(igeoslope_np, np.float64)

    # check that inputs are within range of fis
    # if not, re-assign the value to just within range
    ovc_array[ovc_array < 0] = 0
    ovc_array[ovc_array > 45] = 45
    ihydsp2_array[ihydsp2_array < 0] = 0.0001
    ihydsp2_array[ihydsp2_array > 10000] = 10000
    ihydsplow_array[ihydsplow_array < 0] = 0.0001
    ihydsplow_array[ihydsplow_array > 10000] = 10000
    igeoslope_array[igeoslope_array > 1] = 1

    # delete temp arrays
    items = [segid_np, ovc_np, ihydsp2_np, ihydsplow_np, igeoslope_np]
    for item in items:
        del item

    # create antecedent (input) and consequent (output) objects to hold universe variables and membership functions
    ovc = ctrl.Antecedent(np.arange(0, 45, 0.01), 'input1')
    sp2 = ctrl.Antecedent(np.arange(0, 10000, 1), 'input2')
    splow = ctrl.Antecedent(np.arange(0, 10000, 1), 'input3')
    slope = ctrl.Antecedent(np.arange(0, 1, 0.0001), 'input4')
    density = ctrl.Consequent(np.arange(0, 45, 0.01), 'result')

    # build membership functions for each antecedent and consequent object
    ovc['none'] = fuzz.trimf(ovc.universe, [0, 0, 0.1])
    ovc['rare'] = fuzz.trapmf(ovc.universe, [0, 0.1, 0.5, 1.5])
    ovc['occasional'] = fuzz.trapmf(ovc.universe, [0.5, 1.5, 4, 8])
    ovc['frequent'] = fuzz.trapmf(ovc.universe, [4, 8, 12, 25])
    ovc['pervasive'] = fuzz.trapmf(ovc.universe, [12, 25, 45, 45])

    sp2['persists'] = fuzz.trapmf(sp2.universe, [0, 0, 1000, 1200])
    sp2['breach'] = fuzz.trimf(sp2.universe, [1000, 1200, 1600])
    sp2['oblowout'] = fuzz.trimf(sp2.universe, [1200, 1600, 2400])
    sp2['blowout'] = fuzz.trapmf(sp2.universe, [1600, 2400, 10000, 10000])

    splow['can'] = fuzz.trapmf(splow.universe, [0, 0, 150, 175])
    splow['probably'] = fuzz.trapmf(splow.universe, [150, 175, 180, 190])
    splow['cannot'] = fuzz.trapmf(splow.universe, [180, 190, 10000, 10000])

    slope['flat'] = fuzz.trapmf(slope.universe, [0, 0, 0.0002, 0.005])
    slope['can'] = fuzz.trapmf(slope.universe, [0.0002, 0.005, 0.12, 0.15])
    slope['probably'] = fuzz.trapmf(slope.universe, [0.12, 0.15, 0.17, 0.23])
    slope['cannot'] = fuzz.trapmf(slope.universe, [0.17, 0.23, 1, 1])

    density['none'] = fuzz.trimf(density.universe, [0, 0, 0.1])
    density['rare'] = fuzz.trapmf(density.universe, [0, 0.1, 0.5, 1.5])
    density['occasional'] = fuzz.trapmf(density.universe, [0.5, 1.5, 4, 8])
    density['frequent'] = fuzz.trapmf(density.universe, [4, 8, 12, 25])
    density['pervasive'] = fuzz.trapmf(density.universe, [12, 25, 45, 45])

    # build fis rule table
    rule1 = ctrl.Rule(ovc['none'], density['none'])
    rule2 = ctrl.Rule(splow['cannot'], density['none'])
    rule3 = ctrl.Rule(slope['cannot'], density['none'])
    rule4 = ctrl.Rule(ovc['rare'] & sp2['persists'] & splow['can'] & ~slope['cannot'], density['rare'])
    rule5 = ctrl.Rule(ovc['occasional'] & sp2['persists'] & splow['can'] & ~slope['cannot'], density['occasional'])
    rule6 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['can'] & slope['can'], density['frequent'])
    rule7 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['can'] & slope['probably'], density['occasional'])
    rule8 = ctrl.Rule(ovc['pervasive'] & sp2['persists'] & splow['can'] & slope['flat'], density['pervasive'])
    rule9 = ctrl.Rule(ovc['pervasive'] & sp2['persists'] & splow['can'] & slope['can'], density['pervasive'])
    rule10 = ctrl.Rule(ovc['pervasive'] & sp2['persists'] & splow['can'] & slope['probably'], density['occasional'])
    rule11 = ctrl.Rule(ovc['rare'] & sp2['breach'] & splow['can'] & ~slope['cannot'], density['rare'])
    rule12 = ctrl.Rule(ovc['occasional'] & sp2['breach'] & splow['can'] & ~slope['cannot'], density['occasional'])
    rule13 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['can'] & slope['can'], density['frequent'])
    rule14 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['can'] & slope['probably'], density['occasional'])
    rule15 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['can'] & slope['flat'], density['occasional'])
    rule16 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['can'] & slope['can'], density['frequent'])
    rule17 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['can'] & slope['probably'], density['occasional'])
    rule18 = ctrl.Rule(ovc['rare'] & sp2['oblowout'] & splow['can'] & ~slope['cannot'], density['rare'])
    rule19 = ctrl.Rule(ovc['occasional'] & sp2['oblowout'] & splow['can'] & ~slope['cannot'], density['occasional'])
    rule20 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['can'] & slope['can'], density['frequent'])
    rule21 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['can'] & slope['probably'], density['occasional'])
    rule22 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['can'] & slope['flat'], density['occasional'])
    rule23 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['can'] & slope['can'], density['frequent'])
    rule24 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['can'] & slope['probably'], density['occasional'])
    rule25 = ctrl.Rule(ovc['rare'] & sp2['blowout'] & splow['can'] & ~slope['cannot'], density['none'])
    rule26 = ctrl.Rule(ovc['occasional'] & sp2['blowout'] & splow['can'] & ~slope['cannot'], density['rare'])
    rule27 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['can'] & slope['can'], density['rare'])
    rule28 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['can'] & slope['probably'], density['none'])
    rule29 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['can'] & slope['flat'], density['rare'])
    rule30 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['can'] & slope['can'], density['occasional'])
    rule31 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['can'] & slope['probably'], density['rare'])
    rule32 = ctrl.Rule(ovc['rare'] & sp2['breach'] & splow['probably'] & ~slope['cannot'], density['rare'])
    rule33 = ctrl.Rule(ovc['occasional'] & sp2['breach'] & splow['probably'] & ~slope['cannot'], density['occasional'])
    rule34 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['probably'] & slope['can'], density['frequent'])
    rule35 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['probably'] & slope['probably'], density['occasional'])
    rule36 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['probably'] & slope['flat'], density['occasional'])
    rule37 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['probably'] & slope['can'], density['frequent'])
    rule38 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['probably'] & slope['probably'], density['occasional'])
    rule39 = ctrl.Rule(ovc['rare'] & sp2['oblowout'] & splow['probably'] & ~slope['cannot'], density['rare'])
    rule40 = ctrl.Rule(ovc['occasional'] & sp2['oblowout'] & splow['probably'] & ~slope['cannot'], density['occasional'])
    rule41 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['probably'] & slope['can'], density['occasional'])
    rule42 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['probably'] & slope['probably'], density['rare'])
    rule43 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['probably'] & slope['flat'], density['occasional'])
    rule44 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['probably'] & slope['can'], density['frequent'])
    rule45 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['probably'] & slope['probably'], density['occasional'])
    rule46 = ctrl.Rule(ovc['rare'] & sp2['blowout'] & splow['probably'] & ~slope['cannot'], density['none'])
    rule47 = ctrl.Rule(ovc['occasional'] & sp2['blowout'] & splow['probably'] & ~slope['cannot'], density['rare'])
    rule48 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['probably'] & slope['can'], density['rare'])
    rule49 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['probably'] & slope['probably'], density['none'])
    rule50 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['probably'] & slope['flat'], density['rare'])
    rule51 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['probably'] & slope['can'], density['occasional'])
    rule52 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['probably'] & slope['probably'], density['rare'])
    rule53 = ctrl.Rule(ovc['rare'] & sp2['persists'] & splow['probably'] & ~slope['cannot'], density['rare'])
    rule54 = ctrl.Rule(ovc['occasional'] & sp2['persists'] & splow['probably'] & ~slope['cannot'], density['rare'])
    rule55 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['probably'] & slope['flat'], density['occasional'])
    rule56 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['probably'] & slope['can'], density['frequent'])
    rule57 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['probably'] & slope['probably'], density['occasional'])
    rule58 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['can'] & slope['flat'], density['frequent'])
    rule59 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['probably'] & slope['flat'], density['occasional'])
    rule60 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['can'] & slope['flat'], density['occasional'])
    rule61 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['probably'] & slope['flat'], density['occasional'])
    rule62 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['can'] & slope['flat'], density['rare'])
    rule63 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['probably'] & slope['flat'], density['rare'])
    rule64 = ctrl.Rule(ovc['pervasive'] & sp2['persists'] & splow['probably'] & ~slope['cannot'], density['frequent'])
    rule65 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['can'] & slope['flat'], density['occasional'])

    comb_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27, rule28, rule29, rule30,
                                    rule31, rule32, rule33, rule34, rule35, rule36, rule37, rule38, rule39, rule40, rule41, rule42, rule43, rule44, rule45, rule46, rule47, rule48, rule49, rule50, rule51, rule52, rule53, rule54, rule55, rule56, rule57,
                                    rule58, rule59, rule60, rule61, rule62, rule63, rule64, rule65])
    comb_fis = ctrl.ControlSystemSimulation(comb_ctrl)

    # run fuzzy inference system on inputs and defuzzify output
    out = np.zeros(len(ovc_array)) # todo: test this using nas instead of zeros
    for i in range(len(out)):
        comb_fis.input['input1'] = ovc_array[i]
        comb_fis.input['input2'] = ihydsp2_array[i]
        comb_fis.input['input3'] = ihydsplow_array[i]
        comb_fis.input['input4'] = igeoslope_array[i]
        comb_fis.compute()
        out[i] = comb_fis.output['result']

    # save fuzzy inference system output as table
    columns = np.column_stack((segid_array, out))
    out_table = os.path.dirname(in_network) + "/" + out_field + "_Table.txt"  # todo: see if possible to skip this step
    np.savetxt(out_table, columns, delimiter = ",", header = "ReachID, " + out_field, comments = "")
    occ_table = scratch + "/" + out_field + "Tbl"
    arcpy.CopyRows_management(out_table, occ_table)

    # join the fuzzy inference system output to the flowline network
    # create empty dictionary to hold input table field values
    tblDict = {}
    # add values to dictionary
    with arcpy.da.SearchCursor(occ_table, ['ReachID', out_field]) as cursor:
        for row in cursor:
            tblDict[row[0]] = row[1]
    # populate flowline network out field
    arcpy.AddField_management(in_network, out_field, 'DOUBLE')
    with arcpy.da.UpdateCursor(in_network, ['ReachID', out_field]) as cursor:
        for row in cursor:
            try:
                aKey = row[0]
                row[1] = tblDict[aKey]
                cursor.updateRow(row)
            except:
                pass
    tblDict.clear()

    # calculate defuzzified centroid value for density 'none' MF group
    # this will be used to re-classify output values that fall in this group
    # important: will need to update the array (x) and MF values (mfx) if the
    #            density 'none' values are changed in the model
    x = np.arange(0, 45, 0.01)
    mfx = fuzz.trimf(x, [0, 0, 0.1])
    defuzz_centroid = round(fuzz.defuzz(x, mfx, 'centroid'), 6)

    # update combined capacity (occ_*) values in stream network
    # correct for occ_* greater than ovc_* as vegetation is most limiting factor in model
    # (i.e., combined fis value should not be greater than the vegetation capacity)
    # set occ_* to 0 if the drainage area is greater than the user defined threshold
    # this enforces a stream size threshold above which beaver dams won't persist and/or won't be built
    # set occ_* to 0 if output falls fully in 'none' category

    with arcpy.da.UpdateCursor(in_network, [out_field, veg_field, 'iGeo_DA', 'iGeo_Slope']) as cursor:
        for row in cursor:
            if row[0] > row[1]:
                row[0] = row[1]
            if row[2] >= float(max_DA_thresh):
                row[0] = 0.0
            if round(row[0], 6) == defuzz_centroid:
                row[0] = 0.0
            cursor.updateRow(row)

    # delete temporary tables and arrays
    arcpy.Delete_management(out_table)
    arcpy.Delete_management(occ_table)
    items = [columns, out, x, mfx, defuzz_centroid]
    for item in items:
        del item

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

    exxml.addOutput("BRAT Analysis", "Vector", "BRAT Capacity Output", out_network[out_network.find("02_Analyses"):],
                    outrz, guid=getUUID())

    exxml.write()


def makeLayers(out_network, out_name):
    """
    Writes the layers
    :param out_network: The output network, which we want to make into a layer
    :param out_name: The name of the layers
    :return:
    """
    arcpy.AddMessage("Making layers...")
    output_folder = os.path.dirname(out_network)

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')
    existingCapacityLayer = os.path.join(symbologyFolder, "Existing_Capacity.lyr")
    historicCapacityLayer = os.path.join(symbologyFolder, "Historic_Capacity.lyr")

    makeLayer(output_folder, out_network, "ExistingCapacity", existingCapacityLayer, isRaster=False)
    makeLayer(output_folder, out_network, "HistoricCapacity", historicCapacityLayer, isRaster=False)


def makeLayer(output_folder, layer_base, new_layer_name, symbology_layer, isRaster, description="Made Up Description"):
    """
    Creates a layer and applies a symbology to it
    :param output_folder: Where we want to put the folder
    :param layer_base: What we should base the layer off of
    :param new_layer_name: What the layer should be called
    :param symbology_layer: The symbology that we will import
    :param isRaster: Tells us if it's a raster or not
    :param description: The discription to give to the layer file
    :return: The path to the new layer
    """
    new_layer = new_layer_name + "_lyr"
    new_layer_save = os.path.join(output_folder, new_layer_name + ".lyr")

    if isRaster:
        arcpy.MakeRasterLayer_management(layer_base, new_layer)
    else:
        arcpy.MakeFeatureLayer_management(layer_base, new_layer)

    arcpy.ApplySymbologyFromLayer_management(new_layer, symbology_layer)
    arcpy.SaveToLayerFile_management(new_layer, new_layer_save)
    new_layer_instance = arcpy.mapping.Layer(new_layer_save)
    new_layer_instance.description = description
    new_layer_instance.save()
    return new_layer_save


def makeFolder(pathToLocation, newFolderName):
    """
    Makes a folder and returns the path to it
    :param pathToLocation: Where we want to put the folder
    :param newFolderName: What the folder will be called
    :return: String
    """
    newFolder = os.path.join(pathToLocation, newFolderName)
    if not os.path.exists(newFolder):
        os.mkdir(newFolder)
    return newFolder


def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4])
