import os
from lxml import etree
import argparse

def find_xml_files(directory, product_type):
    """
    Find all XML files in the metadata directories for the given product type.
    """
    xml_files = []
    for root, dirs, files in os.walk(directory):
        if product_type in root and 'metadata' in dirs:
            metadata_dir = os.path.join(root, 'metadata')
            for file in os.listdir(metadata_dir):
                if file.endswith(".xml"):
                    xml_files.append(os.path.join(metadata_dir, file))
    return xml_files

def get_corresponding_nc_file(xml_file):
    """
    Get the corresponding NC file for a given XML file.
    """
    nc_file_name = os.path.basename(xml_file).replace('.xml', '.nc')
    parent_dir = os.path.dirname(os.path.dirname(xml_file))
    nc_file_path = os.path.join(parent_dir, nc_file_name)
    return nc_file_path

def update_xml(xml_file):
    """
    Update xml
    """
    tree = etree.parse(xml_file)
    root = tree.getroot()

    # Removing data access elements apart from where type is ODATA
    xml_element_list = root.findall(
        './/mmd:data_access',
        namespaces=root.nsmap
    )

    for xml_element in xml_element_list:
        if xml_element is not None:
            type_elem = xml_element.find('mmd:type', namespaces=root.nsmap)
            if type_elem is None or type_elem.text != 'ODATA':
                xml_element.getparent().remove(xml_element)


    # Removing link to dataset landing page on THREDDs
    # Find all related_information elements
    related_info_elements = root.findall(
        './/mmd:related_information',
        namespaces=root.nsmap
    )

    # Iterate through each related_information element
    for elem in related_info_elements:
        type_elem = elem.find(
            'mmd:type',
            namespaces=root.nsmap
        )
        if type_elem is not None and type_elem.text == 'Dataset landing page':
            parent = elem.getparent()
            parent.remove(elem)

    # Find the file_format element within storage_information and change its text to 'SAFE'
    file_format_elem = root.find('.//mmd:storage_information/mmd:file_format', namespaces=root.nsmap)
    if file_format_elem is not None:
        file_format_elem.text = 'SAFE'

    tree.write(
            xml_file,
            pretty_print=True
        )

def process_files(directory, product_type):
    """
    Process XML files and remove data access elements if the corresponding NC file does not exist.
    """
    xml_files = find_xml_files(directory, product_type)
    for xml_file in xml_files:
        #print("Processing XML file", xml_file)
        nc_file_path = get_corresponding_nc_file(xml_file)
        if not os.path.exists(nc_file_path):
            print(f"Updating {xml_file}")
            update_xml(xml_file)

def main():
    """
    Main function to parse arguments and initiate the process.
    """
    parser = argparse.ArgumentParser(description='Process XML files to remove data access elements if corresponding NC file is not found.')
    parser.add_argument('directory', type=str, help='Top level directory to search')
    parser.add_argument('product_type', type=str, help='Product type to search for (e.g., S2A, S1A)')

    args = parser.parse_args()
    process_files(args.directory, args.product_type)

if __name__ == "__main__":
    main()