import argparse
import os
from os import listdir
from os.path import isfile, join

from isyntax import deident_isyntax_file
from svs import deident_svs_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WSI Slide Deidentifier')

    # general args
    parser.add_argument('--identified_slides_path', type=str, default='ident')
    parser.add_argument('--deidentified_slides_path', type=str, default='deident')

    args = parser.parse_args()

    slide_map = dict()
    onlyfiles = [f for f in listdir(args.identified_slides_path) if isfile(join(args.identified_slides_path, f))]

    for file in onlyfiles:
        filename, file_extension = os.path.splitext(file)
        ident_file_path = os.path.join(args.identified_slides_path, file)
        deident_file_path = os.path.join(args.deidentified_slides_path, 'deident_' + file)

        if file_extension == '.isyntax':
            if deident_isyntax_file(ident_file_path, deident_file_path):
                print('iSyntax ' + ident_file_path + ' -> deident -> ' + deident_file_path)
            else:
                print('iSyntax failed deident: ' + ident_file_path)

        elif file_extension == '.svs':
            if deident_svs_file(ident_file_path, deident_file_path):
                print('SVS ' + ident_file_path + ' -> deident -> ' + deident_file_path)
            else:
                print('SVS failed deident: ' + ident_file_path)
