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


def main(
    in_network,
    pt_type,
    ex_type,
    max_DA_thresh,
    out_name,
    scratch):

    arcpy.env.overwriteOutput = True

    network_fields = [f.name for f in arcpy.ListFields(in_network)]

    if pt_type == "true":

        # check for oCC_PT field and delete if exists
        if "oCC_PT" in network_fields:
            arcpy.DeleteField_management(in_network, "oCC_PT")

        # check that inputs are within range of fis (slope already taken care of)
        cursor = arcpy.da.UpdateCursor(in_network, ["oVC_PT", "iHyd_SP2", "iHyd_SPLow"])
        for row in cursor:
            if row[0] < 0:
                row[0] = 0
            elif row[0] > 45:
                row[0] = 44
            elif row[1] < 0:
                row[1] = 0.001
            elif row[1] > 10000:
                row[1] = 10000
            elif row[2] < 0:
                row[2] = 0.001
            elif row[2] > 10000:
                row[2] = 10000
            else:
                pass
            cursor.updateRow(row)
        del row
        del cursor

        # get arrays for fields of interest
        ovcex_a = arcpy.da.FeatureClassToNumPyArray(in_network, "oVC_PT")
        ihydsp2_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iHyd_SP2")
        ihydsplow_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iHyd_SPLow")
        igeoslope_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iGeo_Slope")

        ovcex_array = np.asarray(ovcex_a, np.float64)
        ihydsp2_array = np.asarray(ihydsp2_a, np.float64)
        ihydsplow_array = np.asarray(ihydsplow_a, np.float64)
        igeoslope_array = np.asarray(igeoslope_a, np.float64)

        del ovcex_a, ihydsp2_a, ihydsplow_a, igeoslope_a

        ovc = ctrl.Antecedent(np.arange(0, 45, 0.225), 'input1')
        sp2 = ctrl.Antecedent(np.arange(0, 10000, 1), 'input2')
        splow = ctrl.Antecedent(np.arange(0, 10000, 1), 'input3')
        slope = ctrl.Antecedent(np.arange(0, 1, 0.001), 'input4')
        density = ctrl.Consequent(np.arange(0, 45, 0.5), 'result')

        # membership functions
        ovc['none'] = fuzz.trimf(ovc.universe, [0, 0, 0])
        ovc['rare'] = fuzz.trapmf(ovc.universe, [0, 0, 0.5, 1])
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

        # rules
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

        comb_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27, rule28, rule29, rule30,
                                      rule31, rule32, rule33, rule34, rule35, rule36, rule37, rule38, rule39, rule40, rule41, rule42, rule43, rule44, rule45, rule46, rule47, rule48, rule49, rule50, rule51, rule52, rule53, rule54, rule55, rule56, rule57,
                                      rule58, rule59, rule60, rule61, rule62, rule63, rule64])
        comb_fis = ctrl.ControlSystemSimulation(comb_ctrl)

        # defuzzify
        out = np.zeros(len(ovcex_array))
        for i in range(len(out)):
            comb_fis.input['input1'] = ovcex_array[i]
            comb_fis.input['input2'] = ihydsp2_array[i]
            comb_fis.input['input3'] = ihydsplow_array[i]
            comb_fis.input['input4'] = igeoslope_array[i]
            comb_fis.compute()
            out[i] = comb_fis.output['result']

        # save the output text file
        fid = np.arange(0, len(out), 1)
        columns = np.column_stack((fid, out))
        out_table = os.path.dirname(in_network) + "/oCC_PT_Table.txt"
        np.savetxt(out_table, columns, delimiter=",", header="FID, oCC_PT", comments="")

        occ_table = scratch + "/occ_pt_table"
        arcpy.CopyRows_management(out_table, occ_table)
        arcpy.JoinField_management(in_network, "FID", occ_table, "FID", "oCC_PT")
        arcpy.Delete_management(out_table)

        del out, fid, columns, out_table, occ_table

    elif ex_type == "true":

        # check for oCC_EX field and delete if exists
        if "oCC_EX" in network_fields:
            arcpy.DeleteField_management(in_network, "oCC_EX")

        # check that inputs are within range of fis (slope already taken care of)
        cursor = arcpy.da.UpdateCursor(in_network, ["oVC_EX", "iHyd_SP2", "iHyd_SPLow"])
        for row in cursor:
            if row[0] < 0:
                row[0] = 0
            elif row[0] > 45:
                row[0] = 44
            elif row[1] < 0:
                row[1] = 0.001
            elif row[1] > 10000:
                row[1] = 10000
            elif row[2] < 0:
                row[2] = 0.001
            elif row[2] > 10000:
                row[2] = 10000
            else:
                pass
            cursor.updateRow(row)
        del row
        del cursor

        # correct for occ_pt greater than ovc_pt
        cursor = arcpy.da.UpdateCursor(in_network, ["oCC_PT", "oVC_PT"])
        for row in cursor:
            if row[0] > row[1]:
                row[1] = row[0]
            cursor.updateRow(row)
        del row
        del cursor

        # get arrays for fields of interest
        ovcex_a = arcpy.da.FeatureClassToNumPyArray(in_network, "oVC_EX")
        ihydsp2_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iHyd_SP2")
        ihydsplow_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iHyd_SPLow")
        igeoslope_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iGeo_Slope")

        ovcex_array = np.asarray(ovcex_a, np.float64)
        ihydsp2_array = np.asarray(ihydsp2_a, np.float64)
        ihydsplow_array = np.asarray(ihydsplow_a, np.float64)
        igeoslope_array = np.asarray(igeoslope_a, np.float64)

        del ovcex_a, ihydsp2_a, ihydsplow_a, igeoslope_a

        ovc = ctrl.Antecedent(np.arange(0, 45, 0.225), 'input1')
        sp2 = ctrl.Antecedent(np.arange(0, 10000, 1), 'input2')
        splow = ctrl.Antecedent(np.arange(0, 10000, 1), 'input3')
        slope = ctrl.Antecedent(np.arange(0, 1, 0.001), 'input4')
        density = ctrl.Consequent(np.arange(0, 45, 0.5), 'result')

        # membership functions
        ovc['none'] = fuzz.trimf(ovc.universe, [0, 0, 0])
        ovc['rare'] = fuzz.trapmf(ovc.universe, [0, 0, 0.5, 1])
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
        density['rare'] = fuzz.trapmf(density.universe, [0, 0.1, 0.5, 1])
        density['occasional'] = fuzz.trapmf(density.universe, [0.5, 1, 4, 5])
        density['frequent'] = fuzz.trapmf(density.universe, [4, 5, 12, 20])
        density['pervasive'] = fuzz.trapmf(density.universe, [12, 20, 45, 45])

        # rules
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

        comb_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27, rule28, rule29, rule30,
                                      rule31, rule32, rule33, rule34, rule35, rule36, rule37, rule38, rule39, rule40, rule41, rule42, rule43, rule44, rule45, rule46, rule47, rule48, rule49, rule50, rule51, rule52, rule53, rule54, rule55, rule56, rule57,
                                      rule58, rule59, rule60, rule61, rule62, rule63, rule64])
        comb_fis = ctrl.ControlSystemSimulation(comb_ctrl)

        # defuzzify
        out = np.zeros(len(ovcex_array))
        for i in range(len(out)):
            comb_fis.input['input1'] = ovcex_array[i]
            comb_fis.input['input2'] = ihydsp2_array[i]
            comb_fis.input['input3'] = ihydsplow_array[i]
            comb_fis.input['input4'] = igeoslope_array[i]
            comb_fis.compute()
            out[i] = comb_fis.output['result']

        # save the output text file
        fid = np.arange(0, len(out), 1)
        columns = np.column_stack((fid, out))
        out_table = os.path.dirname(in_network) + "/oCC_EX_Table.txt"
        np.savetxt(out_table, columns, delimiter=",", header="FID, oCC_EX", comments="")

        occ_table = scratch + "/occ_ex_table"
        arcpy.CopyRows_management(out_table, occ_table)
        arcpy.JoinField_management(in_network, "FID", occ_table, "FID", "oCC_EX")
        arcpy.Delete_management(out_table)

        del out, fid, columns, out_table, occ_table

        cursor = arcpy.da.UpdateCursor(in_network, ["oVC_EX", "iHyd_SPLow", "iGeo_Slope", "iGeo_DA", "oCC_EX", "oCC_PT"])
        for row in cursor:
            if row[0] == 0:
                row[4] = 0
            elif row[1] > 190:
                row[4] = 0
                row[5] = 0
            elif row[2] >= 0.23:
                row[4] = 0
                row[5] = 0
            elif row[3] >= float(max_DA_thresh):
                row[4] = 0
                row[5] = 0
            elif row[4] > row[0]:
                row[4] = row[0]
            else:
                pass
            cursor.updateRow(row)
        del row
        del cursor

        out_network = os.path.dirname(in_network) + "/" + out_name + ".shp"
        arcpy.CopyFeatures_management(in_network, out_network)

    else:
        raise Exception("either historic or existing must be selected")

    return

if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6])
