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

    # combined fis function
    def combFIS(model_run):

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
        segid_np = arcpy.da.FeatureClassToNumPyArray(in_network, "SegID")
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
        ovc = ctrl.Antecedent(np.arange(0, 45, 0.5), 'input1')
        sp2 = ctrl.Antecedent(np.arange(0, 10000, 1), 'input2')
        splow = ctrl.Antecedent(np.arange(0, 10000, 1), 'input3')
        slope = ctrl.Antecedent(np.arange(0, 1, 0.001), 'input4')
        density = ctrl.Consequent(np.arange(0, 45, 0.5), 'result')

        # build membership functions for each antecedent and consequent object
        ovc['none'] = fuzz.trapmf(ovc.universe, [0, 0, 0, 0.0001])
        ovc['rare'] = fuzz.trapmf(ovc.universe, [0, 0.0001, 0.5, 1])
        ovc['occasional'] = fuzz.trapmf(ovc.universe, [0.5, 1, 4, 5])
        ovc['frequent'] = fuzz.trapmf(ovc.universe, [4, 5, 12, 20])
        ovc['pervasive'] = fuzz.trapmf(ovc.universe, [12, 20, 45, 45])

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
        rule4 = ctrl.Rule(ovc['rare'] & sp2['persists'] & splow['can'], density['rare'])
        rule5 = ctrl.Rule(ovc['occasional'] & sp2['persists'] & splow['can'], density['occasional'])
        rule6 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['can'] & slope['can'], density['frequent'])
        rule7 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['can'] & slope['probably'], density['occasional'])
        rule8 = ctrl.Rule(ovc['pervasive'] & sp2['persists'] & splow['can'] & slope['flat'], density['pervasive'])
        rule9 = ctrl.Rule(ovc['pervasive'] & sp2['persists'] & splow['can'] & slope['can'], density['pervasive'])
        rule10 = ctrl.Rule(ovc['pervasive'] & sp2['persists'] & splow['can'] & slope['probably'], density['occasional'])
        rule11 = ctrl.Rule(ovc['rare'] & sp2['breach'] & splow['can'], density['rare'])
        rule12 = ctrl.Rule(ovc['occasional'] & sp2['breach'] & splow['can'], density['occasional'])
        rule13 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['can'] & slope['can'], density['frequent'])
        rule14 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['can'] & slope['probably'], density['occasional'])
        rule15 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['can'] & slope['flat'], density['occasional'])
        rule16 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['can'] & slope['can'], density['frequent'])
        rule17 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['can'] & slope['probably'], density['occasional'])
        rule18 = ctrl.Rule(ovc['rare'] & sp2['oblowout'] & splow['can'], density['rare'])
        rule19 = ctrl.Rule(ovc['occasional'] & sp2['oblowout'] & splow['can'], density['occasional'])
        rule20 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['can'] & slope['can'], density['frequent'])
        rule21 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['can'] & slope['probably'], density['occasional'])
        rule22 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['can'] & slope['flat'], density['occasional'])
        rule23 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['can'] & slope['can'], density['frequent'])
        rule24 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['can'] & slope['probably'], density['occasional'])
        rule25 = ctrl.Rule(ovc['rare'] & sp2['blowout'] & splow['can'], density['none'])
        rule26 = ctrl.Rule(ovc['occasional'] & sp2['blowout'] & splow['can'], density['rare'])
        rule27 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['can'] & slope['can'], density['rare'])
        rule28 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['can'] & slope['probably'], density['none'])
        rule29 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['can'] & slope['flat'], density['rare'])
        rule30 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['can'] & slope['can'], density['occasional'])
        rule31 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['can'] & slope['probably'], density['rare'])
        rule32 = ctrl.Rule(ovc['rare'] & sp2['breach'] & splow['probably'], density['rare'])
        rule33 = ctrl.Rule(ovc['occasional'] & sp2['breach'] & splow['probably'], density['occasional'])
        rule34 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['probably'] & slope['can'], density['frequent'])
        rule35 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['probably'] & slope['probably'], density['occasional'])
        rule36 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['probably'] & slope['flat'], density['occasional'])
        rule37 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['probably'] & slope['can'], density['frequent'])
        rule38 = ctrl.Rule(ovc['pervasive'] & sp2['breach'] & splow['probably'] & slope['probably'], density['occasional'])
        rule39 = ctrl.Rule(ovc['rare'] & sp2['oblowout'] & splow['probably'], density['rare'])
        rule40 = ctrl.Rule(ovc['occasional'] & sp2['oblowout'] & splow['probably'], density['occasional'])
        rule41 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['probably'] & slope['can'], density['occasional'])
        rule42 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['probably'] & slope['probably'], density['rare'])
        rule43 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['probably'] & slope['flat'], density['occasional'])
        rule44 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['probably'] & slope['can'], density['frequent'])
        rule45 = ctrl.Rule(ovc['pervasive'] & sp2['oblowout'] & splow['probably'] & slope['probably'], density['occasional'])
        rule46 = ctrl.Rule(ovc['rare'] & sp2['blowout'] & splow['probably'], density['none'])
        rule47 = ctrl.Rule(ovc['occasional'] & sp2['blowout'] & splow['probably'], density['rare'])
        rule48 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['probably'] & slope['can'], density['rare'])
        rule49 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['probably'] & slope['probably'], density['none'])
        rule50 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['probably'] & slope['flat'], density['rare'])
        rule51 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['probably'] & slope['can'], density['occasional'])
        rule52 = ctrl.Rule(ovc['pervasive'] & sp2['blowout'] & splow['probably'] & slope['probably'], density['rare'])
        rule53 = ctrl.Rule(ovc['rare'] & sp2['persists'] & splow['probably'], density['rare'])
        rule54 = ctrl.Rule(ovc['occasional'] & sp2['persists'] & splow['probably'], density['rare'])
        rule55 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['probably'] & slope['flat'], density['occasional'])
        rule56 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['probably'] & slope['can'], density['frequent'])
        rule57 = ctrl.Rule(ovc['frequent'] & sp2['persists'] & splow['probably'] & slope['probably'], density['occasional'])
        rule58 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['can'] & slope['flat'], density['frequent'])
        rule59 = ctrl.Rule(ovc['frequent'] & sp2['breach'] & splow['probably'] & slope['flat'], density['occasional'])
        rule60 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['can'] & slope['flat'], density['occasional'])
        rule61 = ctrl.Rule(ovc['frequent'] & sp2['oblowout'] & splow['probably'] & slope['flat'], density['occasional'])
        rule62 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['can'] & slope['flat'], density['rare'])
        rule63 = ctrl.Rule(ovc['frequent'] & sp2['blowout'] & splow['probably'] & slope['flat'], density['rare'])
        rule64 = ctrl.Rule(ovc['pervasive'] & sp2['persists'] & splow['probably'], density['frequent'])
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
        np.savetxt(out_table, columns, delimiter = ",", header = "SegID, " + out_field, comments = "")
        occ_table = scratch + "/" + out_field + "Tbl"
        arcpy.CopyRows_management(out_table, occ_table)

        # join the fuzzy inference system output to the flowline network
        # create empty dictionary to hold input table field values
        tblDict = {}
        # add values to dictionary
        with arcpy.da.SearchCursor(occ_table, ['SegID', out_field]) as cursor:
            for row in cursor:
                tblDict[row[0]] = row[1]
        # populate flowline network out field
        arcpy.AddField_management(in_network, out_field, 'DOUBLE')
        with arcpy.da.UpdateCursor(in_network, ['SegID', out_field]) as cursor:
            for row in cursor:
                try:
                    aKey = row[0]
                    row[1] = tblDict[aKey]
                    cursor.updateRow(row)
                except:
                    pass
        tblDict.clear()

        # delete temporary tables and arrays
        arcpy.Delete_management(out_table)
        arcpy.Delete_management(occ_table)
        del columns

        # update combined capacity (occ_*) values in stream network
        # correct for occ_* greater than ovc_* as vegetation is most limiting factor in model
        # (i.e., combined fis value should not be greater than the vegetation capacity)
        # set occ_* to 0 if the drainage area is greater than the user defined threshold
        # this enforces a stream size threshold above which beaver dams won't persist and/or won't be built
        with arcpy.da.UpdateCursor(in_network, [out_field, veg_field, 'iGeo_DA']) as cursor:
            for row in cursor:
                if row[0] > row[1]:
                    row[0] = row[1]
                if row[2] >= float(max_DA_thresh):
                    row[0] = 0
                cursor.updateRow(row)

    # run the combined fis function for both potential and existing
    combFIS('pt')
    combFIS('ex')

    # save results to user defined output shp
    out_network = os.path.dirname(in_network) + "/" + out_name + ".shp"
    arcpy.CopyFeatures_management(in_network, out_network)
    addxmloutput(projPath, in_network, out_network)


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


def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4])
