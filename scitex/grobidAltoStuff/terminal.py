import argparse
import sys, os


import main


def scitex():
    '''
    Main entry point, makes all options available
    '''

    # Setup the command line arguments to the program
    command = argparse.ArgumentParser(description='Utility function to read and translate Common Logic Interchange Format (.clif) files and print to stdout.')

    requiredArguments = command.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path or folder for PDF file(s) to parse', required=True)

    # Parse the command line arguments
    args = command.parse_args()

    main(args)


def main(args):
    '''
    :param args: arguments passed from customized entry points
    :return:
    '''

    # TODO need to substitute base path
    full_path = args.file

    if os.path.isfile(full_path):
        scitexFile(full_path, args=args)

    elif os.path.isdir(full_path):
        scitexFolder(full_path, args=args)
    else:
        print("Error: Location doesn't exist")


def scitexFile(file):
    print("uhhh")


def scitexFolder(folder):
    for directory, subdirs, files in os.walk(folder):
        for single_file in files:
            if single_file.endswith(".pdf"):
                file = os.path.join(directory, single_file)
                scitexFile(file)


if __name__ == '__main__':
    sys.exit(main())