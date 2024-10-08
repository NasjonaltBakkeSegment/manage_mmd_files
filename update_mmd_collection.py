import os
from lib.utils import MMD, find_xml_files
import argparse

def process_files(directory, product_type):
    """
    Process XML files and update the collection to be NBS.
    """
    xml_files = find_xml_files(directory, product_type)

    for xml_file in xml_files:
        print(xml_file)
        mmd = MMD(xml_file)
        mmd.read()
        mmd.get_geospatial_extents()
        within_sios = mmd.check_if_within_sios()
        mmd.remove_element('.//mmd:collection')
        mmd.add_collection('NBS')
        if within_sios:
            mmd.add_collection('SIOS')
        mmd.write()

def main():
    """
    Main function to parse arguments and initiate the process.
    """
    parser = argparse.ArgumentParser(description='Process XML files to update the collection to be equal to NBS in all files.')
    parser.add_argument('directory', type=str, help='Top level directory to search')
    parser.add_argument('product_type', type=str, help='Product type to search for (e.g., S2A, S1A)')

    args = parser.parse_args()
    process_files(args.directory, args.product_type)

if __name__ == "__main__":
    main()
