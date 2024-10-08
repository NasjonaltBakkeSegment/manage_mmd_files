import os
from lxml import etree
from shapely.geometry import Polygon, box
from datetime import datetime, timezone

sios = Polygon([
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

def get_current_time():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

class MMD:

    def __init__(self, filepath):
        self.filepath = str(filepath)
        self.filename = os.path.basename(self.filepath)

    def read(self):
        self.tree = etree.parse(self.filepath)
        self.root = self.tree.getroot()
        self.ns = self.root.nsmap

    def write(self):
        self.tree.write(
            self.filepath,
            pretty_print=True
        )

    def update_element(self, element_name, element_value, language=None):
        xml_element = self.root.find(
            element_name,
            namespaces=self.ns
        )
        if xml_element is not None:
            xml_element.text = element_value
        else:
            pass

    def remove_element(self, element):
        # Find all instances of element
        xml_element_list = self.root.findall(
            element,
            namespaces=self.ns
        )
        for xml_element in xml_element_list[:]:
            if xml_element is not None:
                xml_element.getparent().remove(xml_element)

    def check_element_exists(self, element_name):
        xml_element = self.root.find(
            element_name,
            namespaces=self.ns
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

    def add_collection(self, collection):

        # Find the index of dataset_production_status
        dps_element = self.root.xpath(".//mmd:dataset_production_status", namespaces=self.ns)[0]
        dps_index = list(self.root).index(
            dps_element
            )

        # Add new collection elements after dataset_production_status
        new_element = etree.Element("{http://www.met.no/schema/mmd}collection")
        new_element.text = collection
        self.root.insert(dps_index + 1, new_element)
        new_element.tail = "\n  "  # Proper indentation

    def update_odata_access_url(self):
        '''
        The ODATA access url should point to colhub-archive.met.no
        However, for some products it is pointing to colhub.met.no
        The products don't exist there, so we need to switch the URLs
        But only if the product is in the AOI. Otherwise the product
        should be set to inactive.
        '''

        self.get_geospatial_extents()
        within_aoi = self.check_if_within_polygon()
        if within_aoi:
            # Find the data_access element with type ODATA
            data_access = self.root.find('.//mmd:data_access[mmd:type="ODATA"]', self.ns)

            if data_access is not None:
                resource = data_access.find('mmd:resource', self.ns)

                if resource is not None:
                    original_url = resource.text
                    updated_url = original_url.replace('colhub.met.no', 'colhub-archive.met.no')

                    if original_url != updated_url:
                        resource.text = updated_url
                        print(f"Updated resource URL: {updated_url}")
                    else:
                        print("No update needed for the resource URL.")
                else:
                    print("No resource element found in data_access.")
        else:
            self.update_element('.//mmd:metadata_status', 'Inactive')

    # def update_xml_version(self, transform):
    #     result = transform(self.tree)
    #     self.tree = result
    # The XSLT file is deleting everything from the platform and instrumentation elements.

    def update_last_metadata_update(self):

        # Find the last_metadata_update element
        last_metadata_update = self.root.find('.//mmd:last_metadata_update', self.ns)

        if last_metadata_update is not None:
            # Check if it contains a direct datetime text
            datetime_text = last_metadata_update.text.strip() if last_metadata_update.text else None
            if datetime_text and last_metadata_update.find('.//mmd:update', self.ns) is None:
                # Create the new structure
                update_elem = etree.Element('{http://www.met.no/schema/mmd}update')

                datetime_elem = etree.SubElement(update_elem, '{http://www.met.no/schema/mmd}datetime')
                datetime_elem.text = datetime_text

                type_elem = etree.SubElement(update_elem, '{http://www.met.no/schema/mmd}type')
                type_elem.text = 'Created'

                note_elem = etree.SubElement(update_elem, '{http://www.met.no/schema/mmd}note')

                # Clear the original element and append the new structure
                last_metadata_update.clear()
                last_metadata_update.append(update_elem)

                # Ensure proper indentation
                update_elem.text = '\n      '
                datetime_elem.tail = '\n      '
                type_elem.tail = '\n      '
                note_elem.tail = '\n    '
                last_metadata_update.text = '\n    '
                last_metadata_update[-1].tail = '\n  '
                last_metadata_update.tail = '\n  '


    def set_to_inactive(self):
        '''
        Set product to inactive
        '''
        self.update_element('.//mmd:metadata_status', 'Inactive')
        self.log_change('Major modification', 'Product has been deleted')

    def set_to_active(self):
        '''
        Set to inactive based on certain criteria.
        All S2 L1C and only up to and including 2020.
        '''
        self.get_geospatial_extents()
        within_aoi = self.check_if_within_polygon()
        if within_aoi:
            self.update_element('.//mmd:metadata_status', 'Active')
        else:
            self.update_element('.//mmd:metadata_status', 'Inactive')

    def log_change(self, updatetype, note):
        '''
        Add a new entry to the last_metadata_update element
        To log changes made to the file
        '''

        # Find the last_metadata_update element
        last_metadata_update = self.root.find("mmd:last_metadata_update", namespaces=self.ns)

        update = {
            'datetime': get_current_time(),
            'type': updatetype,
            'note': note
        }

        update_element = etree.Element("{http://www.met.no/schema/mmd}update")

        datetime_element = etree.SubElement(update_element, "{http://www.met.no/schema/mmd}datetime")
        datetime_element.text = update["datetime"]

        type_element = etree.SubElement(update_element, "{http://www.met.no/schema/mmd}type")
        type_element.text = update["type"]

        note_element = etree.SubElement(update_element, "{http://www.met.no/schema/mmd}note")
        note_element.text = update["note"]

        update_element.text = '\n      '
        update_element.tail = '\n  '
        datetime_element.tail = '\n      '
        type_element.tail = '\n      '
        note_element.tail = '\n    '

        last_metadata_update.append(update_element)
        last_metadata_update[-2].tail = '\n    '


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
