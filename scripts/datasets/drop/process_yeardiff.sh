#!/usr/bin/env bash

ROOT_DIR=./resources/data/drop

PREPROCESS_DIR=${ROOT_DIR}/preprocess

YEARDIFF_DIR=${ROOT_DIR}/date/year_diff_re


python -m datasets.drop.preprocess.year_diff.year_diff  --input_dir ${PREPROCESS_DIR} \
                                                        --output_dir ${YEARDIFF_DIR}
