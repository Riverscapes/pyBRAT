import os
import arcpy
import BRATProject
import BRAT_table
import iHyd
import Veg_FIS
import Comb_FIS
import Conflict_Potential
import Conservation_Restoration
import BRAT_Braid_Handler


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "BRAT Toolbox"
        self.alias = "BRAT Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [BRAT_project_tool, BRAT_table_tool, BRAT_braid_handler, iHyd_tool, Veg_FIS_tool, Comb_FIS_tool, Conflict_Potential_tool, Conservation_Restoration_tool]


class BRAT_project_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 1. BRAT Project Builder"
        self.description = "Gathers and structures the inputs for a BRAT project"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select Project Folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Select existing vegetation datasets",
            name="ex_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param2 = arcpy.Parameter(
            displayName="Select historic vegetation datasets",
            name="hist_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param3 = arcpy.Parameter(
            displayName="Select drainage network datasets",
            name="network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param4 = arcpy.Parameter(
            displayName="Select DEM inputs",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param5 = arcpy.Parameter(
            displayName="Select land use rasters",
            name="landuse",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param6 = arcpy.Parameter(
            displayName="Select valley bottom datasets",
            name="valley",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param7 = arcpy.Parameter(
            displayName="Select roads datasets",
            name="road",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param8 = arcpy.Parameter(
            displayName="Select railroads datasets",
            name="rr",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param9 = arcpy.Parameter(
            displayName="Select canals datasets",
            name="canal",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
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
        reload(BRATProject)
        BRATProject.main(p[0].valueAsText,
                        p[1].valueAsText,
                        p[2].valueAsText,
                        p[3].valueAsText,
                        p[4].valueAsText,
                        p[5].valueAsText,
                        p[6].valueAsText,
                        p[7].valueAsText,
                        p[8].valueAsText,
                        p[9].valueAsText)
        return


class BRAT_table_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 2. BRAT Table"
        self.description = "Prepares the input table to be used in the BRAT tools"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select Project Folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Project Name",
            name="projName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Watershed HUC ID",
            name="hucID",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName = "Watershed Name",
            name="hucName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Input Segmented Network",
            name="seg_network",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        param4.filter.list = ["Polyline"]

        param5 = arcpy.Parameter(
            displayName="Input DEM",
            name="DEM",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Input Drainage Area Raster",
            name="FlowAcc",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Input Coded Existing Vegetation Raster",
            name="coded_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param8 = arcpy.Parameter(
            displayName="Input Coded Historic Vegetation Raster",
            name="coded_hist",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param9 = arcpy.Parameter(
            displayName="Input Valley Bottom Polygon",
            name="valley_bottom",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param9.filter.list = ["Polygon"]

        param10 = arcpy.Parameter(
            displayName="Input Road Layer Feature Class",
            name="road",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param10.filter.list = ["Polyline"]

        param11 = arcpy.Parameter(
            displayName="Input Railroad Feature Class",
            name="railroad",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param11.filter.list = ["Polyline"]

        param12 = arcpy.Parameter(
            displayName="Input Canal Feature Class",
            name="canal",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param12.filter.list = ["Polyline"]

        param13 = arcpy.Parameter(
            displayName="Input Landuse Raster",
            name="landuse",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param14 = arcpy.Parameter(
            displayName="Name BRAT Table Output",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11, param12, param13, param14]

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
        reload(BRAT_table)
        BRAT_table.main(p[0].valueAsText,
                        p[1].valueAsText,
                        p[2].valueAsText,
                        p[3].valueAsText,
                        p[4].valueAsText,
                        p[5].valueAsText,
                        p[6].valueAsText,
                        p[7].valueAsText,
                        p[8].valueAsText,
                        p[9].valueAsText,
                        p[10].valueAsText,
                        p[11].valueAsText,
                        p[12].valueAsText,
                        p[13].valueAsText,
                        p[14].valueAsText)
        return


class BRAT_braid_handler(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 3. BRAT Braid Handler"
        self.description = "Gives braided streams the appropriate values, once mainstems have been identified in the stream network."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT Network",
            name="inputNetwork",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        return [param0]

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
        BRAT_Braid_Handler.main(p[0].valueAsText)
        return


class iHyd_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 4. iHyd Attributes"
        self.description = "Adds the hydrology attributes to the BRAT input table"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT Network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="Select Hydrologic Region",
            name="region",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        return [param0, param1]

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
        reload(iHyd)
        iHyd.main(p[0].valueAsText,
                  p[1].valueAsText)
        return

class Veg_FIS_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 5. BRAT Vegetation FIS"
        self.description = "Runs the vegetation FIS on the BRAT input table"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT Network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        return [param0]

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
        reload(Veg_FIS)
        Veg_FIS.main(p[0].valueAsText)
        return

class Comb_FIS_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 6. BRAT Combined FIS"
        self.description = "Runs the combined FIS on the BRAT input table"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select Project Folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Input BRAT Network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Maximum DA Threshold (Square KM)",
            name = "max_DA_thresh",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName = "Name Output Network",
            name = "out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        # param3.symbology = os.path.join(os.path.dirname(__file__), "Capacity.lyr")

        return [param0, param1, param2, param3]

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
        reload(Comb_FIS)
        Comb_FIS.main(p[0].valueAsText,
                      p[1].valueAsText,
                      p[2].valueAsText,
                      p[3].valueAsText)
        return

class Conflict_Potential_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 7. BRAT Conflict Potential"
        self.description = "Runs the Conflict Potential model on the BRAT output"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select Project Folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Select Combined FIS Output Network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName = "Name Output Network",
            name = "out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        # param2.symbology = os.path.join(os.path.dirname(__file__), "oPC.lyr")

        param3 = arcpy.Parameter(
            displayName="Set Scratch Workspace",
            name="scratch",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        param3.filter.list = ['Local Database']
        param3.value = arcpy.env.scratchWorkspace

        return [param0, param1, param2, param3]

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
        reload(Conflict_Potential)
        Conflict_Potential.main(p[0].valueAsText,
                                p[1].valueAsText,
                                p[2].valueAsText,
                                p[3].valueAsText)
        return

class Conservation_Restoration_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 8. BRAT Conservation Restoration"
        self.description = "Runs the Conservation and Restoration model on the BRAT output"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select Project Folder",
            name="projPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Select Conflict Output Network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Name Output Network",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        # param2.symbology = os.path.join(os.path.dirname(__file__), "oPBRC.lyr")

        return [param0, param1, param2]

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
        reload(Conservation_Restoration)
        Conservation_Restoration.main(p[0].valueAsText,
                                      p[1].valueAsText,
                                      p[2].valueAsText)
        return