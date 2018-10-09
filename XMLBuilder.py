import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


class XMLBuilder:
    """
    Builds an XML file
    """

    def __init__(self, xml_file, root_name, tags=[]):
        """
        Initializes the class by setting up the root based on the given name and tags
        :param xml_file: The path to where the new XML file will be made on the hard drive
        :param root_name: The name of the root element of the XML file
        :param tags: An array of tuples. tag[0] is the name of the tag, tag[1] is the value
        """
        self.xml_file = xml_file
        self.tree = ET.ElementTree(ET.Element(root_name))
        self.root = self.tree.getroot()

        for tag in tags:
            self.root.set(tag[0], tag[1])

    def add_sub_element(self, base_element, name='', text='', tags=[]):
        """
        Creates a new element below an existing element
        :param base_element: an XML Element that we will attach our new sub element to
        :param name: The name of the new sub element
        :param text: The text that is meant to go within the element
        :param tags: A list of tuples. The first element contains the name of the tag, the second contains the value
        :return: The subelement created. Useful if the user wants to append additional subelements to it
        """
        new_element = ET.SubElement(base_element, name)
        new_element.text = text

        for tag in tags:
            new_element.set(tag[0], tag[1])

        return new_element

    def write(self):
        """
        Creates a pretty-printed XML string for the Element,
        then write it out to the expected file
        """
        temp_string = minidom.parseString(ET.tostring(self.root)).toprettyxml(encoding="UTF-8")
        with open(self.xml_file, 'w') as f:
            f.write(temp_string)
        # f = open(self.xml_file, "w")
        # f.write(temp_string)
        # f.close()
