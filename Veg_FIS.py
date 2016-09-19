#-------------------------------------------------------------------------------
# Name:        Veg FIS
# Purpose:     Runs the vegetation FIS for the BRAT input table
#
# Author:      Jordan Gilbert
#
# Created:     09/2016
# Copyright:   (c) Jordan 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import os
import sys

def main(
    in_network,
    fis_type,
    scratch):

    arcpy.env.overwriteOutput = True

    # fix any values outside of fis range
    if fis_type == "PT":
        cursor = arcpy.da.UpdateCursor(in_network, ["iVeg_100PT", "iVeg_30PT"])
        for row in cursor:
            if row[0] < 0:
                row[0] = 0
            elif row[0] > 4:
                row[0] = 3.9
            elif row[1] < 0:
                row[1] = 0
            elif row[1] > 4:
                row[1] = 3.9
            else:
                pass
            cursor.updateRow(row)
        del row
        del cursor

        # get arrays for fields of interest
        riparian_area_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iVeg_100PT")
        streamside_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iVeg_30PT")

        riparian_array = np.asarray(riparian_area_a, np.float64)
        streamside_array = np.asarray(streamside_a, np.float64)

        del riparian_area_a, streamside_a

        # set up input and output ranges
        riparian = ctrl.Antecedent(np.arange(0, 4, 0.04), 'input1')
        streamside = ctrl.Antecedent(np.arange(0, 4, 0.04), 'input2')
        density = ctrl.Consequent(np.arange(0, 45, 0.5), 'result')

        # membership functions
        riparian['unsuitable'] = fuzz.trapmf(riparian.universe, [0, 0, 0.1, 1])
        riparian['barely'] = fuzz.trimf(riparian.universe, [0.1, 1, 2])
        riparian['moderately'] = fuzz.trimf(riparian.universe, [1, 2, 3])
        riparian['suitable'] = fuzz.trimf(riparian.universe, [2, 3, 4])
        riparian['preferred'] = fuzz.trimf(riparian.universe, [3, 4, 4])

        streamside['unsuitable'] = fuzz.trapmf(streamside.universe, [0, 0, 0.1, 1])
        streamside['barely'] = fuzz.trimf(streamside.universe, [0.1, 1, 2])
        streamside['moderately'] = fuzz.trimf(streamside.universe, [1, 2, 3])
        streamside['suitable'] = fuzz.trimf(streamside.universe, [2, 3, 4])
        streamside['preferred'] = fuzz.trimf(streamside.universe, [3, 4, 4])

        density['none'] = fuzz.trimf(density.universe, [0, 0, 0])
        density['rare'] = fuzz.trapmf(density.universe, [0, 0, 0.5, 1])
        density['occasional'] = fuzz.trapmf(density.universe, [0.5, 1, 4, 5])
        density['frequent'] = fuzz.trapmf(density.universe, [4, 5, 12, 20])
        density['pervasive'] = fuzz.trapmf(density.universe, [12, 20, 45, 45])

        # rules
        rule1 = ctrl.Rule(riparian['unsuitable'] & streamside['unsuitable'], density['none'])
        rule2 = ctrl.Rule(riparian['barely'] & streamside['unsuitable'], density['rare'])
        rule3 = ctrl.Rule(riparian['moderately'] & streamside['unsuitable'], density['occasional'])
        rule4 = ctrl.Rule(riparian['suitable'] & streamside['unsuitable'], density['occasional'])
        rule5 = ctrl.Rule(riparian['preferred'] & streamside['unsuitable'], density['occasional'])
        rule6 = ctrl.Rule(riparian['unsuitable'] & streamside['barely'], density['rare'])
        rule7 = ctrl.Rule(riparian['barely'] & streamside['barely'], density['rare'])
        rule8 = ctrl.Rule(riparian['moderately'] & streamside['barely'], density['occasional'])
        rule9 = ctrl.Rule(riparian['suitable'] & streamside['barely'], density['frequent'])
        rule10 = ctrl.Rule(riparian['preferred'] & streamside['barely'], density['frequent'])
        rule11 = ctrl.Rule(riparian['unsuitable'] & streamside['moderately'], density['rare'])
        rule12 = ctrl.Rule(riparian['barely'] & streamside['moderately'], density['occasional'])
        rule13 = ctrl.Rule(riparian['moderately'] & streamside['moderately'], density['occasional'])
        rule14 = ctrl.Rule(riparian['suitable'] & streamside['moderately'], density['frequent'])
        rule15 = ctrl.Rule(riparian['preferred'] & streamside['moderately'], density['pervasive'])
        rule16 = ctrl.Rule(riparian['unsuitable'] & streamside['suitable'], density['rare'])
        rule17 = ctrl.Rule(riparian['barely'] & streamside['suitable'], density['frequent'])
        rule18 = ctrl.Rule(riparian['moderately'] & streamside['suitable'], density['frequent'])
        rule19 = ctrl.Rule(riparian['suitable'] & streamside['suitable'], density['frequent'])
        rule20 = ctrl.Rule(riparian['preferred'] & streamside['suitable'], density['pervasive'])
        rule21 = ctrl.Rule(riparian['unsuitable'] & streamside['preferred'], density['occasional'])
        rule22 = ctrl.Rule(riparian['barely'] & streamside['preferred'], density['frequent'])
        rule23 = ctrl.Rule(riparian['moderately'] & streamside['preferred'], density['frequent'])
        rule24 = ctrl.Rule(riparian['suitable'] & streamside['preferred'], density['pervasive'])
        rule25 = ctrl.Rule(riparian['preferred'] & streamside['preferred'], density['pervasive'])

        # FIS
        veg_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25])
        veg_fis = ctrl.ControlSystemSimulation(veg_ctrl)

        out = np.zeros(len(riparian_array))
        for i in range(len(out)):
            veg_fis.input['input1'] = riparian_array[i]
            veg_fis.input['input2'] = streamside_array[i]
            veg_fis.compute()
            out[i] = veg_fis.output['result']

        # save the output text file then merge to shapefile
        fid = np.arange(0, len(out), 1)
        columns = np.column_stack((fid, out))
        out_table = os.path.dirname(in_network) + '/oVC_PT_Table.txt'
        np.savetxt(out_table, columns, delimiter=',', header='FID, oVC_PT', comments='')

        ovc_table = scratch + '/ovc_pt_table'
        arcpy.CopyRows_management(out_table, ovc_table)
        arcpy.JoinField_management(in_network, 'FID', ovc_table, 'FID', 'oVC_PT')
        arcpy.Delete_management(out_table)

        del out, fid, columns, out_table, ovc_table

    elif fis_type == "EX":
        cursor = arcpy.da.UpdateCursor(in_network, ["iVeg_100EX", "iVeg_30EX"])
        for row in cursor:
            if row[0] < 0:
                row[0] = 0
            elif row[0] > 4:
                row[0] = 3.9
            elif row[1] < 0:
                row[1] = 0
            elif row[1] > 4:
                row[1] = 3.9
            else:
                pass
            cursor.updateRow(row)
        del row
        del cursor

        # get arrays for fields of interest
        riparian_area_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iVeg_100EX")
        streamside_a = arcpy.da.FeatureClassToNumPyArray(in_network, "iVeg_30EX")

        riparian_array = np.asarray(riparian_area_a, np.float64)
        streamside_array = np.asarray(streamside_a, np.float64)

        del riparian_area_a, streamside_a

        # set up input and output ranges
        riparian = ctrl.Antecedent(np.arange(0, 4, 0.04), 'input1')
        streamside = ctrl.Antecedent(np.arange(0, 4, 0.04), 'input2')
        density = ctrl.Consequent(np.arange(0, 45, 0.5), 'result')

        # membership functions
        riparian['unsuitable'] = fuzz.trapmf(riparian.universe, [0, 0, 0.1, 1])
        riparian['barely'] = fuzz.trimf(riparian.universe, [0.1, 1, 2])
        riparian['moderately'] = fuzz.trimf(riparian.universe, [1, 2, 3])
        riparian['suitable'] = fuzz.trimf(riparian.universe, [2, 3, 4])
        riparian['preferred'] = fuzz.trimf(riparian.universe, [3, 4, 4])

        streamside['unsuitable'] = fuzz.trapmf(streamside.universe, [0, 0, 0.1, 1])
        streamside['barely'] = fuzz.trimf(streamside.universe, [0.1, 1, 2])
        streamside['moderately'] = fuzz.trimf(streamside.universe, [1, 2, 3])
        streamside['suitable'] = fuzz.trimf(streamside.universe, [2, 3, 4])
        streamside['preferred'] = fuzz.trimf(streamside.universe, [3, 4, 4])

        density['none'] = fuzz.trimf(density.universe, [0, 0, 0])
        density['rare'] = fuzz.trapmf(density.universe, [0, 0, 0.5, 1])
        density['occasional'] = fuzz.trapmf(density.universe, [0.5, 1, 4, 5])
        density['frequent'] = fuzz.trapmf(density.universe, [4, 5, 12, 20])
        density['pervasive'] = fuzz.trapmf(density.universe, [12, 20, 45, 45])

        # rules
        rule1 = ctrl.Rule(riparian['unsuitable'] & streamside['unsuitable'], density['none'])
        rule2 = ctrl.Rule(riparian['barely'] & streamside['unsuitable'], density['rare'])
        rule3 = ctrl.Rule(riparian['moderately'] & streamside['unsuitable'], density['occasional'])
        rule4 = ctrl.Rule(riparian['suitable'] & streamside['unsuitable'], density['occasional'])
        rule5 = ctrl.Rule(riparian['preferred'] & streamside['unsuitable'], density['occasional'])
        rule6 = ctrl.Rule(riparian['unsuitable'] & streamside['barely'], density['rare'])
        rule7 = ctrl.Rule(riparian['barely'] & streamside['barely'], density['rare'])
        rule8 = ctrl.Rule(riparian['moderately'] & streamside['barely'], density['occasional'])
        rule9 = ctrl.Rule(riparian['suitable'] & streamside['barely'], density['frequent'])
        rule10 = ctrl.Rule(riparian['preferred'] & streamside['barely'], density['frequent'])
        rule11 = ctrl.Rule(riparian['unsuitable'] & streamside['moderately'], density['rare'])
        rule12 = ctrl.Rule(riparian['barely'] & streamside['moderately'], density['occasional'])
        rule13 = ctrl.Rule(riparian['moderately'] & streamside['moderately'], density['occasional'])
        rule14 = ctrl.Rule(riparian['suitable'] & streamside['moderately'], density['frequent'])
        rule15 = ctrl.Rule(riparian['preferred'] & streamside['moderately'], density['pervasive'])
        rule16 = ctrl.Rule(riparian['unsuitable'] & streamside['suitable'], density['rare'])
        rule17 = ctrl.Rule(riparian['barely'] & streamside['suitable'], density['frequent'])
        rule18 = ctrl.Rule(riparian['moderately'] & streamside['suitable'], density['frequent'])
        rule19 = ctrl.Rule(riparian['suitable'] & streamside['suitable'], density['frequent'])
        rule20 = ctrl.Rule(riparian['preferred'] & streamside['suitable'], density['pervasive'])
        rule21 = ctrl.Rule(riparian['unsuitable'] & streamside['preferred'], density['occasional'])
        rule22 = ctrl.Rule(riparian['barely'] & streamside['preferred'], density['frequent'])
        rule23 = ctrl.Rule(riparian['moderately'] & streamside['preferred'], density['frequent'])
        rule24 = ctrl.Rule(riparian['suitable'] & streamside['preferred'], density['pervasive'])
        rule25 = ctrl.Rule(riparian['preferred'] & streamside['preferred'], density['pervasive'])

        # FIS
        veg_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25])
        veg_fis = ctrl.ControlSystemSimulation(veg_ctrl)

        out = np.zeros(len(riparian_array))
        for i in range(len(out)):
            veg_fis.input['input1'] = riparian_array[i]
            veg_fis.input['input2'] = streamside_array[i]
            veg_fis.compute()
            out[i] = veg_fis.output['result']

        # save the output text file then merge to shapefile
        fid = np.arange(0, len(out), 1)
        columns = np.column_stack((fid, out))
        out_table = os.path.dirname(in_network) + '/oVC_EX_Table.txt'
        np.savetxt(out_table, columns, delimiter=',', header='FID, oVC_EX', comments='')

        ovc_table = scratch + '/ovc_ex_table'
        arcpy.CopyRows_management(out_table, ovc_table)
        arcpy.JoinField_management(in_network, 'FID', ovc_table, 'FID', 'oVC_EX')
        arcpy.Delete_management(out_table)

        del out, fid, columns, out_table, ovc_table

    else:
        raise Exception("an fis type was specified that does not exist")


    return in_network

if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3])
