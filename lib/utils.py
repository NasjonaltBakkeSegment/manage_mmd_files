import os
from lxml import etree
from shapely.geometry import Polygon, box

sios = Polyon([
    (-20, 70),
    (-20, 90),
    (40, 90),
    (40, 70),
    (-20, 70)
    ])

polygon = Polygon([
    (-20.263238824222373, 84.8852877777822),
    (-36.25445787748578, 67.02581594412311),
    (11.148084316116405, 52.31593720759386),
    (45.98609725358305, 63.94940066151824),
    (89.96194965005743, 84.8341192704811),
    (-20.263238824222373, 84.8852877777822),
    (-20.263238824222373, 84.8852877777822)
    ])

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

    def get_geospatial_extents(self):
        # Extract the geographic extent coordinates
        self.north = float(self.root.xpath('.//mmd:north', namespaces=self.ns)[0].text)
        self.south = float(self.root.xpath('.//mmd:south', namespaces=self.ns)[0].text)
        self.west = float(self.root.xpath('.//mmd:west', namespaces=self.ns)[0].text)
        self.east = float(self.root.xpath('.//mmd:east', namespaces=self.ns)[0].text)

    def check_if_within_polygon(self):

        # Create a shapely box (rectangle) from the geographic extent
        extent_box = box(self.west, self.south, self.east, self.north)

        # Check if the extent box overlaps with the given polygon
        return extent_box.intersects(polygon) # Returns True or False

    def check_if_within_sios(self):

        # Create a shapely box (rectangle) from the geographic extent
        extent_box = box(self.west, self.south, self.east, self.north)

        # Check if the extent box overlaps with the given polygon
        return extent_box.intersects(sios) # Returns True or False

def find_xml_files(directory, product_type):
    """
    Find all XML files in the metadata directories for the given product type.
    Scans all subdirectories of the given directory
    Returns a list of filepaths to the XML files
    """
    xml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".xml") and file.startswith("S"):
                xml_files.append(os.path.join(root, file))
    return xml_files
