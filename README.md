# Project MEDID (MEdical Data De-IDentification) Consortium

## Purpose

A consortium of academic, clinical and industry partners for the development of open source healthcare imaging de-identification tooling to better enable the democratization of data.

## Goals

* Create SOTA de-id tools across modalities (NLP, radiology, diagnostic & surgical video, pathology) in a Python 3.10.x framework - the de facto language of machine learning.
* Create synthetic PHI datasets to serve as benchmarks for de-id tooling performance.
* Make data released by tools easy to access & use


# De-Identification Tools

Descriptions of de-id tools to go here

# Benchmarking

Leaderboards for benchmark datasets per modality to go here.

# synthetic_phi

Tool(s) to create DICOM datasets with synthetic PHI from previously de-identified DICOM data. 

To install the requirements

	pip install -r requirements.txt

To use the tool

	python generate_synth_phi.py -i input_dir -o output_dir -m num_synth_dicoms


# License

This tool is under the MIT license.


