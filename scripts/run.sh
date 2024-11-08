#!/bin/bash

# SPDX-FileCopyrightText: 2024 © Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olena Hrynenko <olena.hrynenko@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-only

source "ipp/constants.py"

mkdir -p $path_to_data/$path_to_r_results
mkdir -p $path_to_data/$path_to_parsed_results

python ipp/steps/step_1.py
Rscript "ipp/steps/step_2.R" $path_to_data/$dissimilarity_matrix_generation_set $path_to_data/$path_to_r_results/
python ipp/steps/step_3.py