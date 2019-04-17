# -------------------------------------------------------------------------------
# Name:        Update Major River DA Batch
# Purpose:     Updates major river drainage area in BRAT Table using input csv
#
# Note: This expects a csv input with the following columns:
#       - HUC8Dir -- must match basin sub-directory (e.g., BigChicoCreekSacramentoRiver_18020157)
#       - StreamName -- must match BRAT table StreamName (i.e., names can't be misspelled)
#       - US_DA_sqkm
#
# Author:      Sara Bangen
#
# Created:     04/2019
# -------------------------------------------------------------------------------


#  define parent folder path and run folder name for directory search
pf_path = r'C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_CodeTest\DACheck'
run_folder = 'BatchRun_02'
da_csv_path = r"C:\etal\Shared\Projects\USA\California\SierraNevada\BRAT\wrk_Data\00_Projectwide\ModelParameters\TNC_BRAT_UpstreamDA.csv"

#  import required modules and extensions
import os
import sys
import arcpy
import csv
from collections import defaultdict

arcpy.CheckOutExtension('Spatial')
sys.path.append('C:/etal/LocalCode/pyBRAT/TNC_Changes')
from Drainage_Area_Check import main as da_check
from BRAT_Braid_Handler import main as braid_handler


def update_da(inNetwork, inDict):
    """
    Updates iGeo_DA field by adding 'US_DA_sqkm' value to existing iGeo_DA value
    Note: First checks the existing iGeo_DA minimum value for the given river to make
          sure it is less than 'US_DA_sqkm' to prevent adding values several times
    :param inNetwork: The stream network to update da values on
    :param inDict: Dictionary of stream names and major river da values
    :return: None
    """
    arcpy.MakeFeatureLayer_management(inNetwork, "network_lyr")
    # create list of all the StreamNames
    streamList = []
    for key, value in inDict.items():
        for sub_key, sub_value in value.items():
            streamList.append(sub_key)
    # for each StreamName get the associated US DA value
    # if the exisitng minimum iGeo_DA value is < the DA value in the input csv/dictionary then
    # update DA values
    for stream in streamList:
        key = inDict.keys()[0]
        daValue = inDict.get(key, {}).get(stream)
        query = """ "StreamName" = '%s'""" %stream
        arcpy.SelectLayerByAttribute_management("network_lyr", "NEW_SELECTION", query)
        # get current minimum da values and pad by 50 (to account for rounding errors)
        daValues = [row[0] for row in arcpy.da.SearchCursor("network_lyr", ["iGeo_DA"])]
        min_daValues = min(daValues) + 50.0
        if min_daValues <= daValue:
            print "Updating major river DA values for " + stream
            with arcpy.da.UpdateCursor("network_lyr", ["iGeo_DA"]) as cursor:
                for row in cursor:
                    #da = row[0]
                    row[0] = row[0] + daValue
                    cursor.updateRow(row)
        else:
            print "DA values have already been updated for: " + stream + ". If this is not the case, update manually."


def main():

    arcpy.env.overwriteOutput = True  # set to overwrite output

    # read in csv of da parameters and convert to python dictionary
    daDict = defaultdict(dict)

    with open(da_csv_path, "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            daDict[row['HUC8Dir']][row['StreamName']] = float(row['US_DA_sqkm'])

    # change directory to the parent folder path
    os.chdir(pf_path)

    # list all folders in parent folder path - note this is not recursive
    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    # remove folders in the list that start with '00_' since these aren't our huc8 folders
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # run function for each huc8 folder
    for dir in dir_list:

        # get path to brat table shp
        brat_table = os.path.join(pf_path, dir, 'BRAT', run_folder, 'Outputs/Output_01/01_Intermediates/BRAT_Table.shp')

        # if brat table exists and huc8 folder is in dictionary update the major river drainage area values
        if os.path.exists(brat_table):
            if dir in daDict:
                sub_daDict = {k: v for k, v in daDict.iteritems() if dir in k}
            else:
                sub_daDict = None
            if sub_daDict is not None:
                try:
                    update_da(brat_table, sub_daDict)
                except Exception as err:
                    print 'Updating drainage area failed for ' + dir + '. Exception thrown was:'
                    print err
        else:
            print "WARNING: Script cannot be run.  BRAT table doesn't exist for " + dir


if __name__ == "__main__":
    main()
