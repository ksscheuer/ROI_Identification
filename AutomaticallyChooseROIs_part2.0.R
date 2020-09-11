### This is a another test to see if I can use sourcetree.

########################## Set initial values###############################
############################################################################

k <- 3 #number of clusters chosen by hand based on silhouette plot
SNRcutoff <- 4

myslice <- "04-01"
mydate <- "07-11-2020"
dateSlice <- paste(mydate,myslice,sep=" ")

saveclusterplot <- 1 #1 = save, 0 = don't save
  clusterplotheight <- 5
  clusterplotwidth <- 6.5
saveallpotentialroisplot <- 1 #1 = save, 0 = don't save
  allroiplotheight <- 5
  allroiplotwidth <- 6.5
savepotentialroiscorrectsizeplot <- 1 #1 = save, 0 = don't save
  nonoverlaproiplotheight <- 5
  nonoverlaproiplotwidth <- 8
saveroisgoodsnrplot <- 1 #1 = save, 0 = don't save
  roiplotheight <- 5
  roiplotwidth <- 6.5
savefinalroisplot <- 1 #1 = save, 0 = don't save
  finalroiplotheight <- 5
  finalroiplotwidth <- 6.5

#################### Read in data and load libraries #######################
############################################################################

library(ggplot2)
library(dendextend)
library(plyr)
library(dplyr)
library(reshape2)
library(tidyr)

myclusterdata <- read.csv("EachPixel_Cluster.csv",check.names = FALSE)
myclustAvgGps_df_sc <- as.data.frame(myclusterdata$AvgGps)

myfiles <- read.csv("EachPixel_Data.csv",check.names = FALSE)

electrodepixels <- read.csv("electrodepixels.csv",header=FALSE)
electrodepixels <- electrodepixels+1 #photoZ starts counting with 0

############## Hierarchical clustering using chosen k ######################
############################################################################

dist_mat <- dist(myclustAvgGps_df_sc,method="euclidean")
hclust_avg <- hclust(dist_mat,method="average")
cut_avg <- cutree(hclust_avg,k=k)

avg_dend_obj <- as.dendrogram(hclust_avg)
avg_col_dend <- color_branches(avg_dend_obj,h=k)

myclusterdata_df_cl <- mutate(myclusterdata, cluster = cut_avg)

myfiles_df_cl <- data.frame(matrix(ncol=ncol(myfiles)+1,
                                   nrow=nrow(myfiles)))
colnames(myfiles_df_cl) <- c(colnames(myfiles),"Cluster")
myfiles_df_cl[,1:ncol(myfiles)] <- myfiles[,1:ncol(myfiles)]
for (i in 1:nrow(myclusterdata_df_cl)) {
  myclusterpixelid <- which(myfiles_df_cl$PixelID==myclusterdata_df_cl$PixelID[i])
  myfiles_df_cl$Cluster[myclusterpixelid] <- myclusterdata_df_cl$cluster[i]
}

clusteraverages_all <- data.frame(matrix(nrow=k,ncol=2))
colnames(clusteraverages_all) <- c("Avg","SD")
rownames(clusteraverages_all) <- paste(rep("Clust"),1:k,sep="")

clusteraverages <- data.frame(matrix(ncol=2,nrow=k))
colnames(clusteraverages) <- c("k","StN_Avg")
clusteraverages$k <- seq(1:k)
for (i in 1:k) {
  allcolmeans <- colMeans(myfiles_df_cl[which(myfiles_df_cl$Cluster==i),])
  myclustersd <- sd(as.matrix(myfiles_df_cl[which(myfiles_df_cl$Cluster==i),4:6]))
  clusteraverages$StN_Avg[i] <- allcolmeans[which(colnames(myfiles_df_cl)=="AvgGps")]
  clusteraverages_all$Avg[i] <- clusteraverages$StN_Avg[i]
  clusteraverages_all$SD[i] <- myclustersd
}

if (((min(which(clusteraverages$StN_Avg>SNRcutoff)))-1)>0) {
  clustercutoff <- (which(clusteraverages$StN_Avg>SNRcutoff))-1
} else {
  clustercutoff <- 0
}

######################### Plot clusters ####################################
############################################################################

ggplot(myfiles_df_cl,aes(x=X,y=Y)) +
  geom_tile(aes(fill=myfiles_df_cl$Cluster)) +
  labs(title=paste(dateSlice,"Clusters"), fill="SNR Avg +/- SD") +
  theme(
    axis.title.y = element_blank(),
    axis.title.x = element_blank(),
    # axis.ticks = element_blank(),
    # axis.text = element_blank(),
    panel.background = element_blank(),
    plot.title = element_text(hjust=0.5),
    legend.position = "none"
  ) +
  guides(fill = guide_legend(keyheight = 0.9)) +
  scale_y_reverse() +
  scale_fill_gradientn(breaks=seq(1:k),
                       labels=c(paste(round(clusteraverages_all$Avg,3),"+/-",round(clusteraverages_all$SD,3))),
                       colors=rev(c("red1","yellow1","green1","dodgerblue1","navy"))
  )

# if (saveclusterplot==1) {
#   ggsave("Step2_Clusters.jpg",height=plotheight,width=plotwidth)
# }

matrixplot <- function(matrix_to_plot, ptitle) {
  longData<-melt(matrix_to_plot)
  longData<-longData[!is.na(longData$value),]
  ggplot(longData, aes(x = Var2, y = Var1)) + 
    geom_tile(aes(fill=value)) + 
    scale_fill_gradient(low="blue", high="red") +
    labs(x="x", y="y", title=ptitle) +
    scale_y_reverse() +
    theme_bw() + theme(axis.text.x=element_text(size=9, angle=0, vjust=0.3),
                       axis.text.y=element_text(size=9),
                       plot.title=element_text(size=11))
}

####################### Find all potential ROIs ############################
############################################################################
height = 80
width = 80
pixel_cluster_data <- t(matrix(myfiles_df_cl$Cluster, ncol=width, nrow=height))
#pixel_cluster_data[is.na(pixel_cluster_data)] <- 0
# Cluster results is a map of continuous regions in pixel_cluster_data
# Each region is marked by a monotonically increasing integer
cluster_results <- matrix(ncol=width, nrow=height)

check_cell <- function(x, y, group_index, color=0) {
  cell_value <- pixel_cluster_data[y,x]
  #print (c(x, y))
  if(!is.na(cell_value) && is.na(cluster_results[y,x]) && (color == 0 || cell_value==color)) {
    cluster_results[y,x] <<- group_index
    my_bounds = c(x,x,y,y)
    if(y-1 >= 1) {
      child_bounds = check_cell(x, (y-1), group_index, cell_value)
      if(!is.na(child_bounds[1])) {
        my_bounds = c(min(my_bounds[1], child_bounds[1]), max(my_bounds[2], child_bounds[2]),min(my_bounds[3], child_bounds[3]), max(my_bounds[4], child_bounds[4]))
      }
    }
    if(y+1 <= height) {
      child_bounds = check_cell(x, (y+1), group_index, cell_value)
      if(!is.na(child_bounds[1])) {
        my_bounds = c(min(my_bounds[1], child_bounds[1]), max(my_bounds[2], child_bounds[2]),min(my_bounds[3], child_bounds[3]), max(my_bounds[4], child_bounds[4]))
      }    }
    if(x-1 >= 1) {
      child_bounds = check_cell((x-1), y, group_index, cell_value)
      if(!is.na(child_bounds[1])) {
        my_bounds = c(min(my_bounds[1], child_bounds[1]), max(my_bounds[2], child_bounds[2]),min(my_bounds[3], child_bounds[3]), max(my_bounds[4], child_bounds[4]))
      }    }
    if(x+1 <= width) {
      child_bounds = check_cell((x+1), y, group_index, cell_value)
      if(!is.na(child_bounds[1])) {
        my_bounds = c(min(my_bounds[1], child_bounds[1]), max(my_bounds[2], child_bounds[2]),min(my_bounds[3], child_bounds[3]), max(my_bounds[4], child_bounds[4]))
      }    }
    return(my_bounds)
  }
  return(NA)
}

found_groups = 1
group_bounds = list()

for (i in 1:width) {
  for (j in 1:height) {
    result <- check_cell(i,j, found_groups, 0)
    if(!is.na(result[1])) {
      group_bounds[[found_groups]] = result
      found_groups <- found_groups+1
    }
  }
}

matrixplot(cluster_results, "Before Bounds Check")

bound_limit = 3

# Remove clusters that do not fit into our bounds
for (i in 1:length(group_bounds)) {
  group = group_bounds[[i]]
  x_big = ((group[2] - group[1]) > bound_limit-1)
  y_big = ((group[4] - group[3]) > bound_limit-1)
  if (x_big || y_big) {
    # This group does not fit in the rectangular bounds we defined
    cluster_results[cluster_results == i] <- NA 
  }
}

#par(mar=c(0, 0, 0, 0))
#image(t(apply(cluster_results, 2, rev)), col = grey(seq(0, 1, length = 256)), axes=FALSE)

matrixplot(cluster_results, "After Bounds Check")

clipped_cluster_results = cluster_results
clipped_cluster_results[!is.na(clipped_cluster_results)] <- 1
pixel_cluster_data <- pixel_cluster_data * clipped_cluster_results

matrixplot(pixel_cluster_data, "Cleaned Up Clusters")

################## Start trimming / combining regions that touch ###############
visited_cells = matrix(nrow=height, ncol=width)
check_collisions <- function(x, y, group_index=0) {
  cell_value <- cluster_results[y,x]
  # We are looking for collisions with cells that have a differentgroup index 
  # from the set of indexes that we built in the previous step
  if(!is.na(cell_value) && is.na(visited_cells[y,x])) {
    visited_cells[y,x] <<- TRUE
    if(group_index == 0 || cell_value==group_index) {
      xleft = max(1, x-1)
      xright = min(width, x+1)
      yup = max(1, y-1)
      ydown = min(height, y+1)
      check_collisions(x,yup,cell_value)
      check_collisions(xleft,yup,cell_value)
      check_collisions(xleft,y,cell_value)
      check_collisions(xleft,ydown,cell_value)
      check_collisions(x,ydown,cell_value)
      check_collisions(xright,ydown,cell_value)
      check_collisions(xright,y,cell_value)
      check_collisions(xright,yup,cell_value)
    } else {
      # We found a collision (this group_index does not match the parent)
      # Remove both items from cluster_results
      cluster_results[cluster_results == group_index] <<- NA 
      cluster_results[cluster_results == cell_value] <<- NA 
    } 
    
  }
}

# Now that we've trimmed pixel cluster data down, visit each cell again
for (i in 1:width) {
  for (j in 1:height) {
    result <- check_collisions(i,j, 0)
  }
}

matrixplot(cluster_results, "Step 2 Groups")

# Use the trimmed cluster results to remove items from the pixel_cluster_data
clipped_cluster_results = cluster_results
clipped_cluster_results[!is.na(clipped_cluster_results)] <- 1
pixel_cluster_data <- pixel_cluster_data * clipped_cluster_results

matrixplot(pixel_cluster_data, "Step 2 Clusters")

