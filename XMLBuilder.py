import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import arcpy
import re


class XMLBuilder:
    """
    Builds an XML file
    """

    def __init__(self, xml_file, root_name='', tags=[]):
        """
        Initializes the class by setting up the root based on the given name and tags
        :param xml_file: The path to where the new XML file will be made on the hard drive
        :param root_name: The name of the root element of the XML file
        :param tags: An array of tuples. tag[0] is the name of the tag, tag[1] is the value
        """
        self.xml_file = xml_file
        if os.path.exists(xml_file):
            self.tree = ET.parse(xml_file)
        else:
            self.tree = ET.ElementTree(ET.Element(root_name))
        self.root = self.tree.getroot()

        self.set_parent_map()

        for tag in tags:
            self.root.set(tag[0], tag[1])

    def set_parent_map(self):
        self.parent_map = dict((c, p) for p in self.tree.iter() for c in p)


    def add_sub_element(self, base_element, name='', text='', tags=[]):
        """
        Creates a new element below an existing element
        :param base_element: an XML Element that we will attach our new sub element to
        :param name: The name of the new sub element
        :param text: The text that is meant to go within the element
        :param tags: A list of tuples. The first element contains the name of the tag, the second contains the value
        :return: The subelement created. Useful if the user wants to append additional subelements to it
        """
        if base_element is None:
            arcpy.AddWarning("Warning: NoneType was passed to add_sub_element as base element. Possible bug, further investigation may be required")
            return None
        new_element = ET.SubElement(base_element, name)
        new_element.text = text

        for tag in tags:
            new_element.set(tag[0], tag[1])

        self.set_parent_map() # Redoes the parent child mapping, to account for the new element
        return new_element


    def find(self, element_name):
        return self.root.find(element_name)


    def find_by_text(self, text):
        for element in self.tree.iter():
            if element.text == text:
                return element
        return None


    def find_by_id(self, given_id):
        for element in self.tree.iter():
            try:
                if element.attrib['id'] == given_id:
                    return element
            except KeyError:
                pass
        return None


    def find_element_parent(self, element):
        if element is None:
            arcpy.AddWarning("None type passed to find_element_parent. Possible bug, please report to the pyBRAT GitHub page")
            return None
        if element not in self.parent_map:
            self.set_parent_map()
            if element not in self.parent_map:
                arcpy.AddWarning("Could not find parent of an XML element. Possible bug, please report to the pyBRAT GitHub page")
                return None
        return self.parent_map[element]


    def write(self):
        """
        Creates a pretty-printed XML string for the Element,
        then write it out to the expected file
        """
        if os.path.exists(self.xml_file):
            os.remove(self.xml_file)

        xml = minidom.parseString(ET.tostring(self.root))
        temp_string = xml.toprettyxml()
        temp_string = remove_extra_newlines(temp_string)
        # arcpy.AddMessage(temp_string)
        with open(self.xml_file, 'w') as f:
            f.write(temp_string)


def remove_extra_newlines(given_string):
    """
    Removes any case of multiple newlines in a row from a given string
    :param given_string: The string we want to strip newlines from
    :return: The string, sans extra newlines
    """
    ret_string = given_string[0]

    for i in range(1, len(given_string)):
        if given_string[i] != '\n' and given_string[i] != '\t':
            i_is_bad_char = False
        elif given_string[i] == '\n' and given_string[i-1] == '\t':
            i_is_bad_char = True
        elif given_string[i] == '\n' and given_string[i-1] == '\n':
            i_is_bad_char = True
        elif given_string[i] == '\n':
            i_is_bad_char = False
        else:
            j = find_next_non_tab_index(i, given_string)
            if given_string[j] == '\n':
                i_is_bad_char = True
            else:
                i_is_bad_char = False

        if not i_is_bad_char:
            ret_string += given_string[i]

    return ret_string


def find_next_non_tab_index(i, given_string):
    """
    Finds the next value in the string that isn't \t
    """
    while given_string[i] == '\t':
        i += 1
    return i