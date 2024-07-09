import os
from lxml import etree

class MMD:

    def __init__(self, filepath):
        self.filepath = str(filepath)
        self.filename = os.path.basename(self.filepath)

    def read(self):
        self.tree = etree.parse(self.filepath)
        self.root = self.tree.getroot()

    def write(self):
        self.tree.write(
            self.filepath,
            pretty_print=True
        )

    def update_element(self, element_name, element_value, language=None):
        xml_element = self.root.find(
            element_name,
            namespaces=self.root.nsmap
        )
        if xml_element is not None:
            xml_element.text = element_value
        else:
            pass

    def remove_element(self, element):
        # Find all instances of element
        xml_element_list = self.root.findall(
            element,
            namespaces=self.root.nsmap
        )
        for xml_element in xml_element_list:
            if xml_element is not None:
                xml_element.getparent().remove(xml_element)

    def check_element_exists(self, element_name):
        xml_element = self.root.find(
            element_name,
            namespaces=self.root.nsmap
        )
        if xml_element is not None:
            return True
        else:
            return False

def find_xml_files(directory, product_type):
    """
    Find all XML files in the metadata directories for the given product type.
    Scans all subdirectories of the given directory
    Returns a list of filepaths to the XML files
    """
    xml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".xml"):
                xml_files.append(os.path.join(root, file))
    return xml_files