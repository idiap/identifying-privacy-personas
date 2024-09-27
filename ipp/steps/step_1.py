# SPDX-FileCopyrightText: 2024 © Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olena Hrynenko <olena.hrynenko@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-only

import pandas as pd
import numpy as np
import scipy as sc

from ipp.constants import  (
    path_to_data, 
    feature_vector_generation_set_p_prime,
    dissimilarity_matrix_generation_set
)  

from ipp.constants import (
    max_likert_distance, 
    number_of_likert_variables
)

def and_similarity(not_likert_X, not_likert_X_val = None):
  # preprocessing dataframe for convenience
  not_likert_X_np = not_likert_X.to_numpy()
  indices = not_likert_X.index #participants IDs
  columns = not_likert_X.columns #traits

  if not_likert_X_val is None:
    # this is where I will be storing information, this is a square matric of the the size of the number of participants
    and_matrix = np.zeros((len(indices),len(indices)))

    for id_i, val_i in enumerate(indices):
      x1 = not_likert_X_np[id_i,:]
      for id_j, val_j in enumerate(indices):
        # print(id_i, id_j)
        x2 = not_likert_X_np[id_j,:] #all columns, but jth row
        and_matrix[id_i, id_j] = sum(np.logical_and(x1, x2))

  else:
    not_likert_X_val_np = not_likert_X_val.to_numpy()
    indices_val = not_likert_X_val.index

    and_matrix = np.zeros((len(indices),len(indices_val)))

    for id_i, val_i in enumerate(indices):
      x1 = not_likert_X_np[id_i,:]
      for id_j, val_j in enumerate(indices_val):
        # print(id_i, id_j)
        x2 = not_likert_X_val_np[id_j,:] #all columns, but jth row
        and_matrix[id_i, id_j] = sum(np.logical_and(x1, x2))


  # the only thing left is to normalise the matrix by the total number of possible overlaps
  and_matrix = and_matrix / len(columns)

  return(and_matrix)

def likert_measure(likert_data, likert_data_val = None):
  if likert_data_val is None:
    # distances between the participants in likert space, manhattan distance
    d_c_matrix = sc.spatial.distance_matrix(likert_data, likert_data, p=1)
  else:
    d_c_matrix = sc.spatial.distance_matrix(likert_data, likert_data_val, p=1)

  # normalised distances, range from 0 to 1
  hat_d_c_matrix = d_c_matrix / max_likert_distance
  return hat_d_c_matrix

def dissim_measure(likert_data, not_likert_data, likert_data_val = None, not_likert_data_val = None):
  hat_d_c_matrix = likert_measure(likert_data, likert_data_val)
  and_sim = and_similarity(not_likert_data, not_likert_data_val)
  d = hat_d_c_matrix - and_sim
  d[d < 0] = 0
  if likert_data_val is None:
    d = pd.DataFrame(d, index = list(likert_data.index), columns = list(likert_data.index))
  else:
    d = pd.DataFrame(d, index = list(likert_data.index), columns = list(likert_data_val.index))
  return d


def compute_dissimilarity_matrix(path_to_data, input_file_name, outfile_name, save = True):
    all_data = pd.read_csv(f"{path_to_data}/{input_file_name}", index_col = 0)
    likert_X = all_data.iloc[:, 0:number_of_likert_variables]
    not_likert_X = all_data.iloc[:, number_of_likert_variables:-1]
    d = dissim_measure(likert_X, not_likert_X)
    d.to_csv(f"{path_to_data}/{outfile_name}")
    print(f"Saved the dissimilarity matrix for {input_file_name} to {outfile_name} file.")

if __name__ == "__main__":
    compute_dissimilarity_matrix(path_to_data = path_to_data, 
                                 input_file_name = feature_vector_generation_set_p_prime,
                                 outfile_name = dissimilarity_matrix_generation_set
                                 )