<!--
SPDX-FileCopyrightText: 2024 © Idiap Research Institute <contact@idiap.ch>
SPDX-FileContributor: Olena Hrynenko <olena.hrynenko@idiap.ch>

SPDX-License-Identifier: GPL-3.0-only
-->

# Artifact Appendix

Paper title: **Identifying Privacy Personas**

Artifacts HotCRP Id: **#10**

Requested Badge: **Available**.

## Description

- This is the code accompanying the following paper O. Hrynenko, A. Cavallaro, "Identifying Privacy Personas" paper, accepted at Proceeding on Privacy Enhancement Technologies, 2025.
- This code computes the dissimilarity matrix and constructs a dendrogram (without pruning) as part of a processing pipeline described in the paper.
- We provide randomly generated dummy data for demonstration purposes `feature_vector_generation_set_p_dummy.csv` and `feature_vector_generation_set_p_dummy_prime.csv`.
- The paper includes both qualitative and quantitative analyses. The code builds on the previously conducted qualitative analysis (coding, trait formation, annotation). The output of this code can be used for the subsequent quantitative analysis, namely [Boschloo's test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.boschloo_exact.html).
  
### Security/Privacy Issues and Ethical Concerns

The provided code does not pose security/privacy issues, since the code can be run locally. In the case of questionnaire data collection, ethical approval must be obtained. Note that we did not conduct questionnaire data collection in our study. 

## Environment 

### Accessibility

To access the artifacts, please follow the [link](https://github.com/idiap/identifying-privacy-personas). 

#### Installation

Install R:

```bash
sudo apt install r-base-core
```

Clone the project and install it:

```bash
git clone git@github.com/idiap/identifying-privacy-personas.git
cd ipp 
pip install .
```

#### Setup

Open the `constants.py` file to provide the following essential information:

- `path_to_data` – the path to your data folder.
- `feature_vector_generation_set_p` – the name of the participants' feature vectors, $p_i$,
- `feature_vector_generation_set_p_prime` – the name of the participants' feature vectors, $p_i’$,
- `max_likert_distance` – the maximum possible distance between the participants in the Likert space,
- `number_of_likert_variables` – the number of the Likert explanatory variables,
- `num_of_participants_generation_set` – the number of the participants in the generation set.

#### Command-Line usage

Run `./scripts/run.sh`

#### Detailed steps in Python and R

##### Computing the dissimilarity matrix (see Section 5.1 from the paper for details)

The input to this step is a `feature_vector_generation_set_p_prime` file that contains $\bm{p_i}'$ representation of participant $i$, a feature vector of Likert and binary explanatory variables.

```python
compute_dissimilarity_matrix(path_to_data = path_to_data, 
                              input_file_name = feature_vector_generation_set_p_prime,
                              outfile_name = dissimilarity_matrix_generation_set
                              )
```

This function is called in the `run.sh` file:

```bash
python ipp/steps/step_1.py
```

#### Dendrogram construction (see Section 5.2 from the paper for details)

For dendrogram construction, use the corresponding R script `step_2.R`. The default name of the output folder is "Converted_R_output_generation_set". The output folder contains $n$ (where $n$ is a number of participants) .csv files with participants' IDs and their corresponding cluster labels. The naming convention for the files in the output folder is cluster_labels_level_i, where $i$ is the level of the dendrogram. The dendrogram is built by running the following function:

```R
cluster_in_r()
```

The path to the output folder and to the input file and the function call is completed in the `run.sh` file:

```bash
Rscript "ipp/steps/step_2.R" $path_to_data/$dissimilarity_matrix_generation_set $path_to_data/$path_to_r_results
```

#### Unparsing dendrogram construction for Python

For consequent analysis we recommend using Python, hence we unparse the output from R into Python. The function below saves each of the clusters’ information into a separate file (for each cluster, for each level of the dendrogram). The output of this call is a set of files "u.v.csv", where $u$ is the dendrogram level, and $v$ is a cluster ID.

```python
unparsing_for_python(path_to_data = path_to_data, 
                    file_name_binary_descriptor = feature_vector_generation_set_p, 
                    path_to_r_results = path_to_r_results,
                    path_to_parsed_results = path_to_parsed_results
                    )
```

#### Saving clusters’ descriptors, cluster sizes, and cluster splits

In the paper, we represent a descriptor as the frequency of appearance of the traits in a cluster. For further use of the pipeline described in the paper, namely for  Boschloo's test, we recommend storing the count of how many times a trait appeared and the number of people in a cluster separately.

```python
save_descriptors_to_table(path_to_data = path_to_data, 
                          path_to_parsed_results = path_to_parsed_results, 
                          number_of_participants = num_of_participants_generation_set
                          )

save_number_of_ppl_to_dictionary(path_to_data = path_to_data, 
                                  path_to_parsed_results = path_to_parsed_results, 
                                  number_of_participants = num_of_participants_generation_set
                                  )
```

Additionally, we save how a parent cluster u.v is split into clusters u+1.j and u+1.k into a table.

```python
save_cluster_splits(path_to_data = path_to_data, 
                    path_to_r_results = path_to_r_results, 
                    number_of_participants = num_of_participants_generation_set, 
                    outfile_name = dendrogram_cluster_splits_generation_set
                    )
```

These functions are called in the `run.sh` file:

```bash
python ipp/steps/step_3.py
```
