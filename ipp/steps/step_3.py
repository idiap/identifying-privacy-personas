# SPDX-FileCopyrightText: 2024 © Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olena Hrynenko <olena.hrynenko@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-only

import pandas as pd
import numpy as np
import pickle
from pathlib import Path

from ipp.constants import (
    path_to_data, 
    path_to_r_results, 
    path_to_parsed_results, 
    feature_vector_generation_set_p, 
    num_of_participants_generation_set, 
    dendrogram_cluster_splits_generation_set
    )

def unparsing_for_python(path_to_data, file_name_binary_descriptor, path_to_r_results, path_to_parsed_results):  
    path_binary_descriptor = Path(path_to_data) / Path(file_name_binary_descriptor)
    all_participants = pd.read_csv(path_binary_descriptor, index_col = 0)
    all_participants = all_participants.transpose()
    n_pariticipants = all_participants.shape[0]
    
    path_to_assignments = Path(path_to_data) / Path(path_to_r_results)
    path_to_save_assignments = Path(path_to_data) / Path(path_to_parsed_results)
    
    files = [Path(f"cluster_labels_level_{i}.csv") for i in range(1, n_pariticipants + 1)]

    for level_file_name in files:
        #reading the cluster level
        level = str(level_file_name).split("_")[-1].split(".")[0]

        #reading the level assignements
        level_assignments = pd.read_csv(path_to_assignments / level_file_name, index_col = 0)

        result = pd.concat([level_assignments, all_participants], axis=1)
        result['assignment'] = result['assignment'].apply(lambda x: f"{level}.{x}")

        for lvl in range(1, int(level) + 1):  
            cluster = f"{level}.{lvl}"
            result_tmp = result[result["assignment"] == cluster]
            file_name_to_save = path_to_save_assignments / Path(cluster +".csv")
            result_tmp.to_csv(file_name_to_save, index = True)
            print(f"Saved {cluster} to a file.")

def read_absolute_indices_of_cluster_elements(path_to_saved_assignments, number_of_participants):
    absolute_indicies = []

    for i in range(1, number_of_participants + 1): #iterating over number of clusters in a split
      path = Path(path_to_saved_assignments) / Path(f"cluster_labels_level_{i}.csv")
      tmp = pd.read_csv(path)
      lab = np.array(list(tmp['assignment']))
      lab = lab -1
      absolute_indicies_at_lvl_i = []
      for j in range(i):
        tmp = []
        for id,val in enumerate(lab):
          if val == j:
            tmp.append(id)
        absolute_indicies_at_lvl_i.append(tmp)
      absolute_indicies.append(absolute_indicies_at_lvl_i)
    
    # absolute_indicies contains the lists with absolute indices of the elements of a cluster 
    # (e.g., absolute_indicies[1] contains two lists, where absolute_indicies[1][0] indices of cluster 0 
    # and absolute_indicies[1][1] are indices of cluster 1)
    return absolute_indicies

def save_cluster_splits(path_to_data, path_to_r_results, number_of_participants, outfile_name, save_to_text = True):
    path_absolute_indices_of_cluster_elements = Path(path_to_data) / Path(path_to_r_results)
    absolute_indicies = read_absolute_indices_of_cluster_elements(path_absolute_indices_of_cluster_elements, number_of_participants)     

    if save_to_text: 
      to_save = ""

    clusters_that_are_split = pd.DataFrame(columns = ["child_1 (R_naming)", "child_2 (R_naming)"])
    clusters_that_are_split.index.name = 'parent (R_naming)'

    for i in range(1, number_of_participants):      
      parent_level = i - 1
      leaves_level = i

      if save_to_text: 
        to_save += "\n########################\n\n"
        to_save += "Level {} going into level {}.".format(parent_level + 1, leaves_level + 1)+ "\n\n"
        correct_order = []

      
      # converting the nested lists into nested sets 
      prev = [set(x) for x in absolute_indicies[parent_level]]
      curr = [set(x) for x in absolute_indicies[leaves_level]]

      child_nodes = []

      if save_to_text:
        correct_order = []
        for id, val in enumerate(prev):
          if val in curr:
            child_id = curr.index(val)
            correct_order.append((id, "Cluster {}.{} is renamed as {}.{}".format(parent_level + 1, id + 1, leaves_level + 1, child_id + 1)))
      
      # iterating over all of the elements in the child level
      for id, val in enumerate(curr):
        if val not in prev: #if the sets were not in the previous level, they are leaves
          child_nodes.append(id)

      # getting a union of the child nodes to identify the position of the parent node
      parent_val = curr[child_nodes[0]].union(curr[child_nodes[1]]) # this is a set
      parent_ind = prev.index(parent_val)#extracting the index of the parent_val (e.g., what was the label of the parent cluster)

      if save_to_text:
        correct_order.append((parent_ind, "Cluster {}.{} was split into clusters {}.{} and {}.{}".format(parent_level + 1, parent_ind + 1, leaves_level + 1, child_nodes[0] + 1, leaves_level + 1, child_nodes[1] + 1)))
        correct_order.sort(key=lambda x: x[0])
        for value in correct_order:
          to_save += value[1] + "\n"
        to_save += "\n"

      index_to_use = f"{parent_level+1}.{parent_ind+1}"
      clusters_that_are_split.loc[index_to_use] = [f"{parent_level+1 +1}.{child_nodes[0]+1}", f"{parent_level+1 +1}.{child_nodes[1]+1}"]
      print("At level " +str(parent_level+1)+", cluster number "+str(parent_ind+1)+" was split into clusters "+str(child_nodes[0]+1)+" and "+str(child_nodes[1]+1))

    path_to_save_data = Path(path_to_data) / Path(outfile_name)
    clusters_that_are_split.to_csv(path_to_save_data, index = True)
    print(f"Saved cluster splits to {outfile_name}")
          
    if save_to_text:
      text_outfile_name = outfile_name[0:-4]
      path_to_save_data_txt = Path(path_to_data) / Path(text_outfile_name+"_and_renaming_convention.txt")
      text_file = open(path_to_save_data_txt, "w")
      text_file.write(to_save)
      text_file.close()
      print(f"Saved cluster splits and renaming conventions to {text_outfile_name}_and_renaming_convention.txt")

def read_trait_list(path_to_data, path_to_parsed_results):
    path_to_assignments = Path(path_to_data) / Path(path_to_parsed_results)
    all_traits = pd.read_csv((path_to_assignments / Path("1.1.csv")), index_col = 0).columns
    count_for_all_traits = pd.DataFrame()
    count_for_all_traits.index = all_traits[1:] # need to drop the label
    return count_for_all_traits #the output is an empty df with the list of all traits as indicies

def read_descriptor(path_to_data, path_to_parsed_results, name):
  path = Path(path_to_data) / Path(path_to_parsed_results) / Path(name + ".csv")
  descriptor = pd.read_csv(path, index_col=0)
  descriptor = descriptor.drop(["assignment"], axis = 1) #removing the label assignment
  descriptor = descriptor.sum()
  descriptor.name = f"{name}"
  return descriptor

def files_to_read(number_of_participants):
  files = []
  for i in range(1,number_of_participants+1):
    j = 1
    while j<= i:
      files.append(f"{i}.{j}.csv")
      j+=1
  return files

def read_all_descriptors(path_to_data, path_to_parsed_results, files, count_for_all_traits):
    for i in files:
        name = i[0:-4]
        count_for_all_traits = pd.concat((count_for_all_traits, read_descriptor(path_to_data = path_to_data, 
                                                                                path_to_parsed_results = path_to_parsed_results,
                                                                                name = name)), axis=1)
        print(f"Have read information about {name} cluster")
    return count_for_all_traits

def save_all_descriptors(path_to_data, folder_to_parsed_results, count_for_all_traits, outfile_name = "Parsed table.csv"):
   path = Path(path_to_data) / Path(outfile_name)
   count_for_all_traits.to_csv(path, index = True)

def save_descriptors_to_table(path_to_data, path_to_parsed_results, number_of_participants):
   count_for_all_traits = read_trait_list(path_to_data, path_to_parsed_results)
   files = files_to_read(number_of_participants)
   count_for_all_traits = read_all_descriptors(path_to_data, path_to_parsed_results, files = files, count_for_all_traits = count_for_all_traits )
   save_all_descriptors(path_to_data, path_to_parsed_results, count_for_all_traits = count_for_all_traits)
   return(count_for_all_traits)

def count_members(path_to_data, path_to_parsed_results, name):
  path = Path(path_to_data) / Path(path_to_parsed_results) / Path(name + ".csv")
  descriptor = pd.read_csv(path, index_col=0)
  descriptor = descriptor.drop(["assignment"], axis = 1)
  return descriptor.shape[0] #corresponds to the number of ppl in the cluster

def save_number_of_ppl_to_dictionary(path_to_data, path_to_parsed_results, number_of_participants, outfile_name = "clusters_and_their_sizes_130"): 
  count_descriptors = {}
  files = files_to_read(number_of_participants)
  for i in files:
    name = i[0:-4]
    desc = count_members(path_to_data, path_to_parsed_results, name)
    count_descriptors[name] = desc
    print(f"Read {i}")
  path = Path(path_to_data) / Path(outfile_name + ".pkl")
  with open(path, 'wb') as f:
    pickle.dump(count_descriptors, f)
  print(f"Saved cluster sizes to {outfile_name}.pkl")
  return count_descriptors

if __name__ == "__main__":
    # formatting the r output 
    unparsing_for_python(path_to_data = path_to_data, 
                        file_name_binary_descriptor = feature_vector_generation_set_p, 
                        path_to_r_results = path_to_r_results,
                        path_to_parsed_results = path_to_parsed_results
                        )

    save_descriptors_to_table(path_to_data = path_to_data, 
                              path_to_parsed_results = path_to_parsed_results, 
                              number_of_participants = num_of_participants_generation_set
                              )

    save_number_of_ppl_to_dictionary(path_to_data = path_to_data, 
                                     path_to_parsed_results = path_to_parsed_results, 
                                     number_of_participants = num_of_participants_generation_set
                                     )
    
    save_cluster_splits(path_to_data = path_to_data, 
                        path_to_r_results = path_to_r_results, 
                        number_of_participants = num_of_participants_generation_set, 
                        outfile_name = dendrogram_cluster_splits_generation_set
                        )
