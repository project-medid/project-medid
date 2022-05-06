#!/usr/bin/python3
#
# SPDX-FileCopyrightText: Copyright (c) 2022 Project MEDID
# SPDX-License-Identifier: MIT
#


import argparse
import os
import random
from os import walk

from utils import Gender, Patient, inject_phi, rename_dir


def main():

    parser = argparse.ArgumentParser(
        description="Create a synthetic PHI dataset from a de-identified dataset"
    )
    parser.add_argument(
        "-i", "--input", help="Directory path of de-identified data", required=True
    )
    parser.add_argument(
        "-o", "--output", help="Directory path for output synthetic data", required=True
    )
    parser.add_argument(
        "-m",
        "--max",
        help="Maximum number of synthetic DICOM images & videos you would like to "
        "create",
        required=False,
    )
    args = parser.parse_args()

    dir_path = args.input
    synth_path = args.output + "/"

    if args.max:
        max_num = int(args.max)

    if not os.path.exists(synth_path):
        os.makedirs(synth_path)

    gnd_truth = []
    i = 0
    for (dirpath, dirnames, filenames) in walk(dir_path, topdown=False):
        for directory in dirnames:
            if i > max_num:
                break
            # if OBGYN exam - mark gender = Female
            if directory[0] == "O":
                gender = Gender.FEMALE
            else:
                gender = random.choice([Gender.MALE, Gender.FEMALE])
            # get fake patient data
            fake_patient = Patient()
            fake_patient.get_new_fake_patient_info(gender)

            # if synth dir doesn't exist create it w/ PHI
            new_dir = rename_dir(directory, fake_patient.name)
            if not os.path.exists(synth_path + new_dir):
                os.makedirs(synth_path + new_dir)

            # for each dicom in a folder, inject synth PHI
            for fname in os.listdir(os.path.join(dirpath, directory)):
                if "dcm" in fname:
                    input_file = os.path.join(dir_path, directory, fname)
                    output_file = os.path.join(synth_path, new_dir, fname)
                    print("Input: ", input_file)
                    print("Output : ", output_file)
                    # inject PHI and return ground truth coordinates for txt location
                    coord = inject_phi(input_file, output_file, fake_patient)
                    if coord is None:
                        continue
                    gnd_truth.append((output_file, input_file, coord))
                    i += 1
                    if i > max_num:
                        print(
                            "Stopping - Number of Synthetic DICOMS created: ", max_num
                        )
                        break


if __name__ == "__main__":
    main()
