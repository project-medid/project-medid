#!/usr/bin/python3
#
# SPDX-FileCopyrightText: Copyright (c) 2022 Project MEDID
# SPDX-License-Identifier: MIT
#


import random
from enum import Enum

import numpy as np
import pandas as pd
import pydicom
from faker import Faker
from PIL import Image, ImageDraw, ImageFont


class Gender(Enum):
    FEMALE = "F"
    MALE = "M"


class Patient:
    """Class to record patient data"""

    def __init__(self):
        self.name = None
        self.ssn = None
        self.dob = None
        self.gender = None

    def get_new_fake_patient_info(self, gender=None):
        """
        create fake patient
        :param gender:
        :return: name, ssn, dob
        """

        fake = Faker()
        fake.name()

        if gender == Gender.FEMALE:
            self.name = fake.first_name_female() + " " + fake.last_name()
        elif gender == Gender.MALE:
            self.name = fake.first_name_male() + " " + fake.last_name()
        else:
            self.name = fake.first_name() + " " + fake.last_name()

        self.ssn = fake.ssn()
        self.dob = fake.date_of_birth()
        self.gender = gender.value


def get_ground_truth():
    """
    randomly vary where PHI text is placed
    :return: coordinates for begining of PHI text
    """
    return np.random.randint(0, 180), np.random.randint(0, 20)


def rename_dir(directory, name):
    new_dir = directory.strip("0123456789")
    name = name.replace(" ", "_")
    rand_pos = random.choice([0, 1])
    if rand_pos == 0:
        new_dir = name + "_" + new_dir
    else:
        new_dir = new_dir + "_" + name
    return new_dir


def write_txt_img(image, patient, gnd_truth):
    """
    Write burned in annotation to image with random location
    :param image: numpy image array (converted from DICOM)
    :param patient: fake patient info
    :return: image with burned in annotations
    """
    WHITE_COLOR_VALUE_8BIT = 255
    x_var, y_var = gnd_truth

    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 20)
    img_edit = ImageDraw.Draw(image)

    img_edit.text(
        (x_var, y_var),
        patient.name,
        (WHITE_COLOR_VALUE_8BIT, WHITE_COLOR_VALUE_8BIT, WHITE_COLOR_VALUE_8BIT),
        font,
    )
    img_edit.text(
        (x_var, y_var + 20),
        "SSN: " + patient.ssn,
        (WHITE_COLOR_VALUE_8BIT, WHITE_COLOR_VALUE_8BIT, WHITE_COLOR_VALUE_8BIT),
        font,
    )
    img_edit.text(
        (x_var, y_var + 40),
        "DOB: " + str(patient.dob),
        (WHITE_COLOR_VALUE_8BIT, WHITE_COLOR_VALUE_8BIT, WHITE_COLOR_VALUE_8BIT),
        font,
    )

    return image


def inject_phi(input_dicom, output_dicom, patient):
    """
    input:  de-identified image or video dicom file
    output: image or video dicom file w/ fake PHI in meta & pixel data
    """
    ds = pydicom.dcmread(input_dicom)
    img = ds.pixel_array.astype(float)

    if len(img.shape) == 4:
        # video
        im = np.zeros(shape=img.shape)

        gnd_truth = get_ground_truth()

        for i in range(img.shape[0]):
            img_temp = img[i, :, :, :]
            img_temp = Image.fromarray((img_temp).astype(np.uint8))
            img_temp = write_txt_img(img_temp, patient, gnd_truth)
            im[i, :, :, :] = img_temp
        im = im.astype(np.uint8)
    elif len(img.shape) == 3:
        # image
        gnd_truth = get_ground_truth()
        im = Image.fromarray((img).astype(np.uint8))
        im = write_txt_img(im, patient, gnd_truth)
    else:
        print("DICOM img dimensions not 3 or 4. Skipping...")
        return

    ds.PatientName = patient.name
    ds.PatientBirthDate = patient.dob
    ds.PatientSex = patient.gender

    ds.PixelData = im.tobytes()
    ds.save_as(output_dicom)
    return gnd_truth


def write_to_csv(gnd_truth):
    df = pd.DataFrame(data={"ground_truth": gnd_truth})
    df.to_csv("ground_truth.csv", sep=",", index=False)
