# SPDX-FileCopyrightText: 2024 © Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olena Hrynenko <olena.hrynenko@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-only

args <- commandArgs(trailingOnly = TRUE)

path_to_file <- args[1]
path_to_folder <- args[2]

library(cluster)

read_data <- function(path_to_file) {
  myData = read.csv(path_to_file, header = TRUE)
  index <- myData$X
  myData <- subset(myData, select = -X)
  rownames(myData) <- index
  return(myData)
}

build_dendrogram <- function(dissimilarity_matrix, visualise = FALSE){
  cluster_diana <- diana(dissimilarity_matrix, diss = TRUE, stand = FALSE)
  if (visualise){
    par(lty = 1)
    par(mfrow = c(1,1))
    pltree(cluster_diana, 
           cex = 0.5, hang = -1, 
           main = "Dendogram of the hierarchical clustering of particiapnts",
           xlab = "Participants' ID")
  }
  return(cluster_diana)
}

parse_dendrogram <- function(dendrogram, dissimilarity_data, path_to_folder){
  number_of_participants = length(dendrogram$order)
  #saving the assignment to files
  for (i in 1:number_of_participants) {
    sub_grp <- cutree(dendrogram, k = i)
    file_name = paste0("cluster_labels_level_", i, ".csv")
    df <- data.frame(index = rownames(dissimilarity_data), assignment = sub_grp)
    write.csv(df, file = paste0(path_to_folder, file_name), row.names = FALSE)
    print(paste0("Saved ", file_name, ""))
  }
}

cluster_in_r <- function(visualise = FALSE){
  myData = read_data(path_to_file)
  cluster_diana = build_dendrogram(myData, visualise = visualise)
  parse_dendrogram(cluster_diana, myData, path_to_folder)
}

cluster_in_r()

