Python Whole Slide Image (WSI) Deidentification Library
===============
This library allows python applications to deidentify WSI

Installing
============


pip install pywsidi

Usage
=====
* iSyntax: deident_isyntax_file(ident_file_path, deident_file_path)
* SVS: deident_svs_file(ident_file_path, deident_file_path)


Demo
=====
python3 main.py --identified_slides_path='ident_dir' --deidentified_slides_path='deident_dir'