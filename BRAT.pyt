import os
import arcpy
import BRATProject
import BRAT_table
import iHyd
import Veg_FIS
import Comb_FIS
import Constraints_Opportunities
import BRAT_Braid_Handler
import Data_Capture_Validation
import Drainage_Area_Check
import StreamObjects
import Layer_Package_Generator
import Collect_Summary_Products

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "BRAT Toolbox"
        self.alias = "BRAT Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [BRAT_project_tool, BRAT_table_tool, BRAT_braid_handler, iHyd_tool, Veg_FIS_tool, Comb_FIS_tool,
                        Constraints_Opportunities_tool, Data_Capture_Validation_tool, Drainage_Area_Check_tool,
                        Layer_Package_Generator_tool, Collect_Summary_Products_tool]

class BRAT_project_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 1. BRAT Project Builder"
        self.description = "Gathers inputs and creates folder structure for a BRAT project"
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
            displayName="Project name",
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
            displayName = "Watershed name",
            name="hucName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Select existing vegetation datasets",
            name="ex_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param5 = arcpy.Parameter(
            displayName="Select historic vegetation datasets",
            name="hist_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param6 = arcpy.Parameter(
            displayName="Select drainage network datasets",
            name="network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param7 = arcpy.Parameter(
            displayName="Select DEM inputs",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param8 = arcpy.Parameter(
            displayName="Select land use rasters",
            name="landuse",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param9 = arcpy.Parameter(
            displayName="Select valley bottom datasets",
            name="valley",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param10 = arcpy.Parameter(
            displayName="Select roads datasets",
            name="road",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param11 = arcpy.Parameter(
            displayName="Select railroads datasets",
            name="rr",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param12 = arcpy.Parameter(
            displayName="Select canals datasets",
            name="canal",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param13 = arcpy.Parameter(
            displayName="Select land ownership datasets",
            name="ownership",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param14 = arcpy.Parameter(
            displayName="Beaver Dam Survey Data",
            name="beaver_dams",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        param15 = arcpy.Parameter(
            displayName="Perennial Stream",
            name="perennial_stream",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11,
                param12, param13, param14, param15]

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
                        p[9].valueAsText,
                        p[10].valueAsText,
                        p[11].valueAsText,
                        p[12].valueAsText,
                        p[13].valueAsText,
                        p[14].valueAsText,
                        p[15].valueAsText)
        return


class BRAT_table_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 2. BRAT Table"
        self.description = "Calculates, for each stream network segment, the attributes needed to run the BRAT tools"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select project folder",
            name="proj_path",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Input segmented network",
            name="seg_network",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Input DEM",
            name="in_DEM",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Input drainage area raster",
            name="flow_acc",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Input coded existing vegetation raster",
            name="coded_veg",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Input coded historic vegetation raster",
            name="coded_hist",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Input valley bottom polygon",
            name="valley_bottom",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param6.filter.list = ["Polygon"]

        param7 = arcpy.Parameter(
            displayName="Input roads feature class",
            name="road",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param7.filter.list = ["Polyline"]

        param8 = arcpy.Parameter(
            displayName="Input railroads feature class",
            name="railroad",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param8.filter.list = ["Polyline"]

        param9 = arcpy.Parameter(
            displayName="Input canal feature class",
            name="canal",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param9.filter.list = ["Polyline"]

        param10 = arcpy.Parameter(
            displayName="Input landuse raster",
            name="landuse",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input")

        param11 = arcpy.Parameter(
			displayName="Input land ownership feature class",
            name="ownership",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")

        param12 = arcpy.Parameter(
            displayName="Perennial stream network",
            name="perennial_network",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")

        param13 = arcpy.Parameter(
            displayName="Name BRAT table output feature class",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
			
        param13.value = "BRAT_Table"
			
        param14 = arcpy.Parameter(
            displayName="Short description for run - less than 100 characters",
            name="description",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
 
        param15 = arcpy.Parameter(
            displayName="Find Clusters",
            name="find_clusters",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        param16 = arcpy.Parameter(
            displayName="Segment Network by Roads",
            name="should_segment_network",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
			
        param17 = arcpy.Parameter(
            displayName="Segment Network by Land Ownership",
            name="segment_by_ownership",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        param18 = arcpy.Parameter(
            displayName="Run Verbose",
            name="is_verbose",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
       
        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11, param12, param13, param14, param15, param16, param17, param18]

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
                        p[14].valueAsText,
                        p[15].valueAsText,
                        p[16].valueAsText,
						p[17].valueAsText,
						p[18].valueAsText)
        return


class BRAT_braid_handler(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 2.2 Braid Handler (Optional)"
        self.description = "In development and currently non-operational. Gives braided streams the appropriate values, once mainstems have been identified in the stream network."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT network",
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
        reload(BRAT_Braid_Handler)
        reload(StreamObjects)
        BRAT_Braid_Handler.main(p[0].valueAsText)
        return


class iHyd_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 3. iHyd Streamflow Attributes"
        self.description = "Calculates, for each stream network segment, discharge (in cubic meters per second) and stream power for both baseflow and annual peak streamflows"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="Select hydrologic region",
            name="region",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param2 = arcpy.Parameter(
			displayName="Baseflow equation",
			name="Qlow_eqtn",
			datatype="GPString",
			parameterType="Optional",
			direction="Input")

        param3 = arcpy.Parameter(
			displayName="Highflow equation",
			name="Q2_eqtn",
			datatype="GPString",
			parameterType="Optional",
			direction="Input")
		
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
        reload(iHyd)
        iHyd.main(p[0].valueAsText,
                  p[1].valueAsText,
				  p[2].valueAsText,
				  p[3].valueAsText)
        return

class Veg_FIS_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 4. BRAT Vegetation Dam Capacity Model"
        self.description = "Calculates dam capacity, for each stream network segment, based solely on vegetation.  Capacity is calculated separately for existing and historic vegetation type."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input BRAT network",
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
        self.label = "Step 5. BRAT Combined Dam Capacity Model"
        self.description = "Calculates dam capacity, for each stream network segment, based on vegetation dam capacity estimates, baseflow stream power, annual peak stream power, and slope.  Capacity is calculated separetly for existing and history vegetation."
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
            displayName="Input BRAT network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Maximum DA threshold (in square kilometers)",
            name = "max_DA_thresh",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName = "Name combined capacity model output feature class",
            name = "out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
			
        param3.value = "Combined_Capacity_Model"
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


class Constraints_Opportunities_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 6. BRAT Constraints and Opportunities Model"
        self.description = "For each stream segment, assigns a constraints and opportunities class based on existing dam capacity, historic dam capacity, and human-beaver conflict potential score"
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
            displayName="Select combined dam capacity output network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="Name the constraints and opportunities output",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param2.value = "Constraints_Opportunities_Model"

        param3 = arcpy.Parameter(
            displayName="Surveyed beaver dams",
            name="surveyed_dams",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Conservation areas shapefile",
            name="conservation_areas",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param4.filter.list = ["Polygon"]

        param5 = arcpy.Parameter(
            displayName="Conservation easements shapefile",
            name="conservation_easements",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param5.filter.list = ["Polygon"]

        return [param0, param1, param2, param3, param4, param5]

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
        reload(Constraints_Opportunities)
        Constraints_Opportunities.main(p[0].valueAsText,
                                      p[1].valueAsText,
                                      p[2].valueAsText,
                                      p[3].valueAsText,
                                      p[4].valueAsText,
                                      p[5].valueAsText)
        return

class Data_Capture_Validation_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 7. Data Capture Validation (Optional)"
        self.description = "Tests the results of BRAT against data on beaver dam sites"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Select constraints and opportunities model output network",
            name="in_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="Name the data validation output",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param1.value = "Data_Capture_Validation"

        param2 = arcpy.Parameter(
            displayName="Select beaver dam shape file",
            name="dams",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Maximum DA threshold (in square kilometers)",
            name="DA_threshold",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

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
        reload(Data_Capture_Validation)
        Data_Capture_Validation.main(p[0].valueAsText,
                                     p[1].valueAsText,
                                     p[2].valueAsText,
									 p[3].valueAsText)


class Drainage_Area_Check_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 2.1 Drainage Area Check (Optional)"
        self.description = "Looks for drainage area values that are less than an upstream value, and then modifies them"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Select BRAT Table output network",
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
        reload(StreamObjects)
        reload(Drainage_Area_Check)
        Drainage_Area_Check.main(p[0].valueAsText)
        return


class Layer_Package_Generator_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Layer Package Generator"
        self.description = "Creates a layer package based on the completed BRAT run"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Select output folder",
            name="in_network",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Name the layer package output",
            name="layer_package_name",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Give a stream network to clip the layer package networks to",
            name="clipping_network",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        param2.filter.list = ["Polyline"]

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
        reload(Layer_Package_Generator)
        Layer_Package_Generator.main(p[0].valueAsText, p[1].valueAsText, p[2].valueAsText)
        return


class Collect_Summary_Products_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Collect Summary Products"
        self.description = "Creates a folder structure for the summary products, divided into AI, PDF, and PNG files"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Select project folder",
            name="in_network",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Stream Network(s)",
            name="clipping_network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param2 = arcpy.Parameter(
            displayName="Watershed/Area Name",
            name="watershed_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Name the output Excel file",
            name="excel_file_name",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Dams Shapefile(s)",
            name="dams_shapefile",
            datatype="DEFeatureClass",
            parameterType="Optional",
			multiValue=True,
            direction="Input")
		
        param5 = arcpy.Parameter(
            displayName="Output folder",
            name="output_folder",
            datatype="DEFolder",
            parameterType="Optional",
			multiValue=False,
            direction="Input")
			
        return [param0, param1, param2, param3, param4, param5]

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
        reload(Collect_Summary_Products)
        Collect_Summary_Products.main(p[0].valueAsText,
                                       p[1].valueAsText,
                                       p[2].valueAsText,
                                       p[3].valueAsText,
                                       p[4].valueAsText,
                                       p[5].valueAsText)
        return
