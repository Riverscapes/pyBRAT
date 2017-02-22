import uuid
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import string

class ProjectXML:
    """creates an instance of a project xml file"""

    def __init__(self, filepath, projType, name):
        self.logFilePath = filepath

        # Initialize the tree
        self.projectTree = ET.ElementTree(ET.Element("Project"))
        self.project = self.projectTree.getroot()

        # Set up a root Project node
        self.project.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.project.set("xsi:noNamespaceSchemaLocation", "https://raw.githubusercontent.com/Riverscapes/Program/master/Project/XSD/V1/Project.xsd")

        # Set up the <Name> and <ProjectType> tags
        self.name = ET.SubElement(self.project, "Name")
        self.name.text = name
        self.projectType = ET.SubElement(self.project, "ProjectType")
        self.projectType.text = projType

        # Add some containers we will fill out later
        self.Inputs = ET.SubElement(self.project, "Inputs")
        self.realizations = ET.SubElement(self.project, "Realizations")
        self.BRATRealizations = []

    def addMeta(self, name, value, parentNode):
        """adds metadata tags to the project xml document"""
        metaNode = parentNode.find("MetaData")
        if metaNode is None:
            metaNode = ET.SubElement(parentNode, "MetaData")

        node = ET.SubElement(metaNode, "Meta")
        node.set("name", name)
        node.text = str(value)

    def addParameter(self, name, value, parentNode):
        """adds parameter tags to the project xml document"""
        paramNode = parentNode.find("Parameters")
        if paramNode is None:
            paramNode = ET.SubElement(parentNode, "Parameters")

        node = ET.SubElement(paramNode, "Param")
        node.set("name", name)
        node.text = str(value)

    def addProjectInput(self, itype, name, path, project="", iid="", guid="", ref=""):
        typeNode = ET.SubElement(self.Inputs, itype)
        if iid is not "":
            typeNode.set("id", iid)
        if guid is not "":
            typeNode.set("guid", guid)
        if ref is not "":
            typeNode.set("ref", ref)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)
        if project is not "":
            projectNode = ET.SubElement(typeNode, "Project")
            projectNode.text = str(project)

    def addOutput(self, aname, otype, name, path, parentNode, project="", oid="", guid="", ref=""):
        """adds an output tag to an analysis tag in the project xml document"""
        analysisNode = parentNode.find("Analysis")
        if analysisNode is None:
            analysisNode = ET.SubElement(parentNode, "Analysis")
            ET.SubElement(analysisNode, "Name").text = str(aname)
        outputsNode = analysisNode.find("Outputs")
        if outputsNode is None:
            outputsNode = ET.SubElement(analysisNode, "Outputs")

        typeNode = ET.SubElement(outputsNode, otype)
        if oid is not "":
            typeNode.set("id", oid)
        if guid is not "":
            typeNode.set("guid", guid)
        if ref is not "":
            typeNode.set("ref", ref)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)

        if project is not "":
            projectNode = ET.SubElement(typeNode, "Project")
            projectNode.text = str(project)

    def addBRATRealization(self, name, rid="", promoted="", dateCreated="", productVersion="", guid=""):
        """adds a BRAT realization tag to the project xml document"""
        node = ET.SubElement(self.realizations, "BRAT")
        if rid is not "":
            node.set("id", rid)
        if promoted is not "":
            node.set("promoted", promoted)
        if dateCreated is not "":
            node.set("dateCreated", dateCreated)
        if productVersion is not "":
            node.set("productVersion", productVersion)
        if guid is not "":
            node.set("guid", guid)
        nameNode = ET.SubElement(node, "Name")
        nameNode.text = str(name)
        self.BRATRealizations.append(node)

    def addBRATInput(self, parentNode, type, name="", path="", project="", iid="", guid="", ref=""):
        """adds input tags to the project xml document"""
        inputsNode = parentNode.find("Inputs")
        if inputsNode is None:
            inputsNode = ET.SubElement(parentNode, "Inputs")
        if type == "Existing Vegetation":
            exNode = inputsNode.find("ExistingVegetation")
            if exNode is None:
                exNode = ET.SubElement(inputsNode, "ExistingVegetation")
            if name is not "":
                nameNode = ET.SubElement(exNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(exNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(exNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                exNode.set("id", iid)
            if guid is not "":
                exNode.set("guid", guid)
            if ref is not "":
                exNode.set("ref", ref)
        if type == "Historic Vegetation":
            histNode = inputsNode.find("HistoricVegetation")
            if histNode is None:
                histNode = ET.SubElement(inputsNode, "HistoricVegetation")
            if name is not "":
                nameNode = ET.SubElement(histNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(histNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(histNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                histNode.set("id", iid)
            if guid is not "":
                histNode.set("guid", guid)
            if ref is not "":
                histNode.set("ref", ref)
        if type == "Network":
            dnNode = inputsNode.find("DrainageNetworks")
            if dnNode is None:
                dnNode = ET.SubElement(inputsNode, "DrainageNetworks")
            networkNode = ET.SubElement(dnNode, "Network")
            if name is not "":
                nameNode = ET.SubElement(networkNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(networkNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(networkNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                networkNode.set("id", iid)
            if guid is not "":
                networkNode.set("guid", guid)
            if ref is not "":
                networkNode.set("ref", ref)
        if type == "Buffer":
            dnNode = inputsNode.find("DrainageNetworks")
            if dnNode is None:
                dnNode = ET.SubElement(inputsNode, "DrainageNetworks")
            networkNode = dnNode.find("Network")
            if networkNode is None:
                networkNode = ET.SubElement(dnNode, "Network")
            buffersNode = networkNode.find("Buffers")
            if buffersNode is None:
                buffersNode = ET.SubElement(networkNode, "Buffers")
            bufferNode = ET.SubElement(buffersNode, "Buffer")
            if name is not "":
                nameNode = ET.SubElement(bufferNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(bufferNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(bufferNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                bufferNode.set("id", iid)
            if guid is not "":
                bufferNode.set("guid", guid)
            if ref is not "":
                bufferNode.set("ref", ref)
        if type == "DEM":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            demNode = ET.SubElement(topoNode, "DEM")
            if name is not "":
                nameNode = ET.SubElement(demNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(demNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(demNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                demNode.set("id", iid)
            if guid is not "":
                demNode.set("guid", guid)
            if ref is not "":
                demNode.set("ref", ref)
        if type == "Flow":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            flowNode = ET.SubElement(topoNode, "Flow")
            if name is not "":
                nameNode = ET.SubElement(flowNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(flowNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(flowNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                flowNode.set("id", iid)
            if guid is not "":
                flowNode.set("guid", guid)
            if ref is not "":
                flowNode.set("ref", ref)
        if type == "Valley":
            vbNode = inputsNode.find("ValleyBottom")
            if vbNode is None:
                vbNode = ET.SubElement(inputsNode, "ValleyBottom")
            if name is not "":
                nameNode = ET.SubElement(vbNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(vbNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(vbNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                vbNode.set("id", iid)
            if guid is not "":
                vbNode.set("guid", guid)
            if ref is not "":
                vbNode.set("ref", ref)
        if type == "Roads":
            roadsNode = inputsNode.find("Roads")
            if roadsNode is None:
                roadsNode = ET.SubElement(inputsNode, "Roads")
            if name is not "":
                nameNode = ET.SubElement(roadsNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(roadsNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(roadsNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                roadsNode.set("id", iid)
            if guid is not "":
                roadsNode.set("guid", guid)
            if ref is not "":
                roadsNode.set("ref", ref)
        if type == "Railroads":
            rrNode = inputsNode.find("Railroads")
            if rrNode is None:
                rrNode = ET.SubElement(inputsNode, "Railroads")
            if name is not "":
                nameNode = ET.SubElement(rrNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rrNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rrNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rrNode.set("id", iid)
            if guid is not "":
                rrNode.set("guid", guid)
            if ref is not "":
                rrNode.set("ref", ref)
        if type == "Canals":
            canalsNode = inputsNode.find("Canals")
            if canalsNode is None:
                canalsNode = ET.SubElement(inputsNode, "Canals")
            if name is not "":
                nameNode = ET.SubElement(canalsNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(canalsNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(canalsNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                canalsNode.set("id", iid)
            if guid is not "":
                canalsNode.set("guid", guid)
            if ref is not "":
                canalsNode.set("ref", ref)
        if type == "Land Use":
            luNode = inputsNode.find("LandUse")
            if luNode is None:
                luNode = ET.SubElement(inputsNode, "LandUse")
            if name is not "":
                nameNode = ET.SubElement(luNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(luNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(luNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                luNode.set("id", iid)
            if guid is not "":
                luNode.set("guid", guid)
            if ref is not "":
                luNode.set("ref", ref)

    def write(self):
        """
        Return a pretty-printed XML string for the Element.
        then write it out to the expected file
        """
        rough_string = ET.tostring(self.project, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="\t")
        pretty = string.replace(pretty, "\\", "/")
        f = open(self.logFilePath, "wb")
        f.write(pretty)
        f.close()


class ExistingXML:
    """opens an existing project xml file to edit it"""

    def __init__(self, filepath):

        self.filepath = filepath
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        self.rz = self.root.find("Realizations")

        self.BRATRealizations = []

    def addParameter(self, name, value, parentNode):
        """adds parameter tags to the project xml document"""
        paramNode = parentNode.find("Parameters")
        if paramNode is None:
            paramNode = ET.SubElement(parentNode, "Parameters")

        node = ET.SubElement(paramNode, "Param")
        node.set("name", name)
        node.text = str(value)

    def addProjectInput(self, itype, name, path, project="", iid="", guid="", ref=""):
        Inputs = self.root.find("Inputs")
        typeNode = ET.SubElement(Inputs, itype)
        if iid is not "":
            typeNode.set("id", iid)
        if guid is not "":
            typeNode.set("guid", guid)
        if ref is not "":
            typeNode.set("ref", ref)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)
        if project is not "":
            projectNode = ET.SubElement(typeNode, "Project")
            projectNode.text = str(project)

    def addOutput(self, aname, otype, name, path, parentNode, project="", oid="", guid="", ref=""):
        """adds an output tag to an analysis tag in the project xml document"""
        analysisNode = parentNode.find("Analysis")
        if analysisNode is None:
            analysisNode = ET.SubElement(parentNode, "Analysis")
            ET.SubElement(analysisNode, "Name").text = str(aname)
        outputsNode = analysisNode.find("Outputs")
        if outputsNode is None:
            outputsNode = ET.SubElement(analysisNode, "Outputs")

        typeNode = ET.SubElement(outputsNode, otype)
        if oid is not "":
            typeNode.set("id", oid)
        if guid is not "":
            typeNode.set("guid", guid)
        if ref is not "":
            typeNode.set("ref", ref)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)

        if project is not "":
            projectNode = ET.SubElement(typeNode, "Project")
            projectNode.text = str(project)

    def addBRATRealization(self, name, rid="", promoted="", dateCreated="", productVersion="", guid=""):
        """adds a BRAT realization tag to the project xml document"""
        node = ET.SubElement(self.rz, "BRAT")
        if rid is not "":
            node.set("id", rid)
        if promoted is not "":
            node.set("promoted", promoted)
        if dateCreated is not "":
            node.set("dateCreated", dateCreated)
        if productVersion is not "":
            node.set("productVersion", productVersion)
        if guid is not "":
            node.set("guid", guid)
        nameNode = ET.SubElement(node, "Name")
        nameNode.text = str(name)
        self.BRATRealizations.append(node)

    def addBRATInput(self, parentNode, type, name="", path="", project="", iid="", guid="", ref=""):
        """adds input tags to the project xml document"""
        inputsNode = parentNode.find("Inputs")
        if inputsNode is None:
            inputsNode = ET.SubElement(parentNode, "Inputs")
        if type == "Existing Vegetation":
            exNode = inputsNode.find("ExistingVegetation")
            if exNode is None:
                exNode = ET.SubElement(inputsNode, "ExistingVegetation")
            if name is not "":
                nameNode = ET.SubElement(exNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(exNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(exNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                exNode.set("id", iid)
            if guid is not "":
                exNode.set("guid", guid)
            if ref is not "":
                exNode.set("ref", ref)
        if type == "Historic Vegetation":
            histNode = inputsNode.find("HistoricVegetation")
            if histNode is None:
                histNode = ET.SubElement(inputsNode, "HistoricVegetation")
            if name is not "":
                nameNode = ET.SubElement(histNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(histNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(histNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                histNode.set("id", iid)
            if guid is not "":
                histNode.set("guid", guid)
            if ref is not "":
                histNode.set("ref", ref)
        if type == "Network":
            dnNode = inputsNode.find("DrainageNetworks")
            if dnNode is None:
                dnNode = ET.SubElement(inputsNode, "DrainageNetworks")
            networkNode = ET.SubElement(dnNode, "Network")
            if name is not "":
                nameNode = ET.SubElement(networkNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(networkNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(networkNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                networkNode.set("id", iid)
            if guid is not "":
                networkNode.set("guid", guid)
            if ref is not "":
                networkNode.set("ref", ref)
        if type == "Buffer":
            dnNode = inputsNode.find("DrainageNetworks")
            if dnNode is None:
                dnNode = ET.SubElement(inputsNode, "DrainageNetworks")
            networkNode = dnNode.find("Network")
            if networkNode is None:
                networkNode = ET.SubElement(dnNode, "Network")
            buffersNode = networkNode.find("Buffers")
            if buffersNode is None:
                buffersNode = ET.SubElement(networkNode, "Buffers")
            bufferNode = ET.SubElement(buffersNode, "Buffer")
            if name is not "":
                nameNode = ET.SubElement(bufferNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(bufferNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(bufferNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                bufferNode.set("id", iid)
            if guid is not "":
                bufferNode.set("guid", guid)
            if ref is not "":
                bufferNode.set("ref", ref)
        if type == "DEM":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            demNode = ET.SubElement(topoNode, "DEM")
            if name is not "":
                nameNode = ET.SubElement(demNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(demNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(demNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                demNode.set("id", iid)
            if guid is not "":
                demNode.set("guid", guid)
            if ref is not "":
                demNode.set("ref", ref)
        if type == "Flow":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            flowNode = ET.SubElement(topoNode, "Flow")
            if name is not "":
                nameNode = ET.SubElement(flowNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(flowNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(flowNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                flowNode.set("id", iid)
            if guid is not "":
                flowNode.set("guid", guid)
            if ref is not "":
                flowNode.set("ref", ref)
        if type == "Valley":
            vbNode = inputsNode.find("ValleyBottom")
            if vbNode is None:
                vbNode = ET.SubElement(inputsNode, "ValleyBottom")
            if name is not "":
                nameNode = ET.SubElement(vbNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(vbNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(vbNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                vbNode.set("id", iid)
            if guid is not "":
                vbNode.set("guid", guid)
            if ref is not "":
                vbNode.set("ref", ref)
        if type == "Roads":
            roadsNode = inputsNode.find("Roads")
            if roadsNode is None:
                roadsNode = ET.SubElement(inputsNode, "Roads")
            if name is not "":
                nameNode = ET.SubElement(roadsNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(roadsNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(roadsNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                roadsNode.set("id", iid)
            if guid is not "":
                roadsNode.set("guid", guid)
            if ref is not "":
                roadsNode.set("ref", ref)
        if type == "Railroads":
            rrNode = inputsNode.find("Railroads")
            if rrNode is None:
                rrNode = ET.SubElement(inputsNode, "Railroads")
            if name is not "":
                nameNode = ET.SubElement(rrNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rrNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rrNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rrNode.set("id", iid)
            if guid is not "":
                rrNode.set("guid", guid)
            if ref is not "":
                rrNode.set("ref", ref)
        if type == "Canals":
            canalsNode = inputsNode.find("Canals")
            if canalsNode is None:
                canalsNode = ET.SubElement(inputsNode, "Canals")
            if name is not "":
                nameNode = ET.SubElement(canalsNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(canalsNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(canalsNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                canalsNode.set("id", iid)
            if guid is not "":
                canalsNode.set("guid", guid)
            if ref is not "":
                canalsNode.set("ref", ref)
        if type == "Land Use":
            luNode = inputsNode.find("LandUse")
            if luNode is None:
                luNode = ET.SubElement(inputsNode, "LandUse")
            if name is not "":
                nameNode = ET.SubElement(luNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(luNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(luNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                luNode.set("id", iid)
            if guid is not "":
                luNode.set("guid", guid)
            if ref is not "":
                luNode.set("ref", ref)

    def write(self):
        """
        Return a pretty-printed XML string for the Element.
        then write it out to the expected file
        """
        rough_string = ET.tostring(self.root, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="\t")
        while string.find(pretty, "\n\t\n") > 0:
            pretty = string.replace(pretty, "\n\t\t\t\t\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\n", "\n")
            pretty = string.replace(pretty, "\n\n", "\n")
            pretty = string.replace(pretty, "\n\n\n", "\n")
            pretty = string.replace(pretty, "\\", "/")
        f = open(self.filepath, "wb")
        f.write(pretty)
        f.close()