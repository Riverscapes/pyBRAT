import arcpy

import bdwsRun

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "BDWS Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [BDWS_Run]


class BDWS_Run(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "BDWS"
        self.description = "Beaver Dam Water Storage (BDWS) is a collection of Python classes for estimating surface water and groundwater stored by beaver dams."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select project folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Select BRAT output",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Select DEM inputs",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Input drainage area raster",
            name="FlowAcc",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Input flow direction raster",
            name="FlowDir",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Input Horizontal KFN",
            name="horizontalKFN",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Input Vertical KFN",
            name="verticalKFN",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Input Field Capacity Raster",
            name="fieldCapacity",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param8 = arcpy.Parameter(
            displayName="Modflow .exe file",
            name="modflowexe",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(bdwsRun)
        bdwsRun.main(p[0].valueAsText,
                      p[1].valueAsText,
                      p[2].valueAsText,
                      p[3].valueAsText,
                      p[4].valueAsText,
                      p[5].valueAsText,
                      p[6].valueAsText,
                      p[7].valueAsText,
                      p[8].valueAsText)
        return