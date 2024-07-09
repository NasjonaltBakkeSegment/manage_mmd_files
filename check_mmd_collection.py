import os
from lib.utils import MMD, find_xml_files
import argparse

def process_files(directory, product_type):
    """
    Process XML files and remove data access elements if the corresponding NC file does not exist.
    """
    xml_files = find_xml_files(directory, product_type)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_directory, f"missing_collection_{product_type}.txt")

    with open(log_file_path, 'a') as log_file:
        for xml_file in xml_files:
            print(xml_file)
            mmd = MMD(xml_file)
            mmd.read()
            exists = mmd.check_element_exists(".//mmd:collection") # Returns True or False
            if not exists:
                log_file.write(f"{xml_file}\n")

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