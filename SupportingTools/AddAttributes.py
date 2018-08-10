import arcpy
import os
import argparse


input_stream = None


def main(given_stream):
    addIDs(given_stream)
    addReachDist(given_stream)


def addIDs(given_stream):
    """
    Gives the stream network the StreamID and ReachID attributes
    :param given_stream: The stream network given to the program
    :return:
    """
    pass


def addReachDist(given_stream):
    """
    Calculates the ReachDist attribute using StreamID
    :param given_stream:
    :return:
    """
    print "Adding Reach Distance Attribute..."
    fields = [f.name for f in arcpy.ListFields(given_stream)]
    if 'ReachID' not in fields:
        arcpy.AddField_management(given_stream, "ReachID", "LONG")
    with arcpy.da.UpdateCursor(given_stream, ['FID', 'ReachID']) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)

    # get distance along route (LineID) for segment midpoints
    midpoints = arcpy.FeatureVerticesToPoints_management(given_stream, 'in_memory/midpoints', "MID")

    seg_network_dissolve = arcpy.Dissolve_management(given_stream, 'in_memory/seg_network_dissolve', 'StreamID', '',
                                                     'SINGLE_PART', 'UNSPLIT_LINES')

    arcpy.AddField_management(seg_network_dissolve, 'From_', 'DOUBLE')
    arcpy.AddField_management(seg_network_dissolve, 'To_', 'DOUBLE')
    with arcpy.da.UpdateCursor(seg_network_dissolve, ['SHAPE@Length', 'From_', 'To_']) as cursor:
        for row in cursor:
            row[1] = 0.0
            row[2] = row[0]
            cursor.updateRow(row)

    arcpy.CreateRoutes_lr(seg_network_dissolve, 'StreamID', 'in_memory/flowline_route', 'TWO_FIELDS', 'From_', 'To_')
    routeTbl = arcpy.LocateFeaturesAlongRoutes_lr(midpoints, 'in_memory/flowline_route', 'StreamID',
                                                  1.0,
                                                  os.path.join(os.path.dirname(given_stream), 'tbl_Routes.dbf'),
                                                  'RID POINT MEAS')

    distDict = {}
    # add reach id distance values to dictionary
    with arcpy.da.SearchCursor(routeTbl, ['ReachID', 'MEAS']) as cursor:
        for row in cursor:
            distDict[row[0]] = row[1]

    # populate dictionary value to output field by ReachID
    arcpy.AddField_management(given_stream, 'ReachDist', 'DOUBLE')
    with arcpy.da.UpdateCursor(given_stream, ['ReachID', 'ReachDist']) as cursor:
        for row in cursor:
            aKey = row[0]
            row[1] = distDict[aKey]
            cursor.updateRow(row)

    arcpy.Delete_management('in_memory')


if __name__ == '__main__':
    if input_stream is not None:
        main(input_stream)
    else:
        parser = argparse.ArgumentParser(description="Adds the ReachDist attribute")
        parser.add_argument('input_stream', help="The shape file given as input to the program")
        args = parser.parse_args()

        main(args.input_stream)