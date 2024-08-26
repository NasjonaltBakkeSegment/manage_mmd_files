from lib.utils import MMD
import argparse
import os

def find_S2_L1C_xml_files(directory):
    """
    Find all XML files in the metadata directory.
    Scans all subdirectories of the given directory
    Returns a list of filepaths to the XML files
    Returns only S2 L1C products, S2A or S2B.
    """
    xml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".xml") and file.startswith("S2") and "OPER" in file:
                xml_files.append(os.path.join(root, file))
    return xml_files

def process_files(directory):
    """
    Process XML files.
    """
    xml_files = find_S2_L1C_xml_files(directory)

    for xml_file in xml_files:
        print(xml_file)
        mmd = MMD(xml_file)
        mmd.read()
        mmd.set_to_inactive()
        mmd.write()

def main():
    """
    Main function to parse arguments and initiate the process.
    """
    parser = argparse.ArgumentParser(description='Process XML files to update the collection to be equal to NBS in all files.')
    parser.add_argument('directory', type=str, help='Top level directory to search')

    args = parser.parse_args()
    process_files(args.directory)

if __name__ == "__main__":
    main()
