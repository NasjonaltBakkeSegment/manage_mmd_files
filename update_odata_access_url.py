import os
from lib.utils import MMD, find_xml_files
import argparse

def process_files(directory, product_type):
    """
    Process XML files
    """
    xml_files = find_xml_files(directory, product_type)

    for xml_file in xml_files:
        print(xml_file)
        mmd = MMD(xml_file)
        mmd.read()
        mmd.update_odata_access_url()
        mmd.write()

def main():
    """
    Main function to parse arguments and initiate the process.
    """
    parser = argparse.ArgumentParser(description='Process XML files to update the odata access url to be at colhub-archive instead of colhub.')
    parser.add_argument('directory', type=str, help='Top level directory to search')
    parser.add_argument('product_type', type=str, help='Product type to search for (e.g., S2A, S1A)')

    args = parser.parse_args()
    process_files(args.directory, args.product_type)

if __name__ == "__main__":
    main()
