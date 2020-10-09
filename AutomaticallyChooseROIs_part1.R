






# TODO: MAKE INITIAL CUTOFF BASED ON 95TH PERCENTILE SNR FOR NO STIM CONTROL OR FOR 40 FRAMES AT FRAME 200

# TODO: KEEP ONLY TOP 10? 15? 5? ROIS; PLOT FINAL ROIS WITH SNR AND ELECTRODE 



















########################## Set initial values###############################
############################################################################

maxkclust <- 10 #maximum number of potential clusters
# pixelcutoff <- 0.5 #before clustering, eliminate pixels with lowest SNR
myslice <- "02-01"
mydate <- "07-11-2020"
dateSlice <- paste(mydate,myslice,sep=" ")

saveoriginalplot <- 1 #1 = save, 0 = don't save
saveelbowplot <- 1 #1 = save, 0 = don't save
savesilhouetteplot <- 1 #1 = save, 0 = don't save
saveclusterplot <- 0 #1 = save, 0 = don't save
plotheight <- 5
plotwidth <- 5.75

############# Load libraries, load data, and make df to fill ###############
############################################################################

suppressMessages(suppressWarnings(library(dendextend)))
suppressMessages(suppressWarnings(library(ggplot2)))
suppressMessages(suppressWarnings(library(colorRamps)))
suppressMessages(suppressWarnings(library(dplyr)))
suppressMessages(suppressWarnings(library(factoextra)))
suppressMessages(suppressWarnings(library(reshape2)))
suppressMessages(suppressWarnings(library(stringr)))
suppressMessages(suppressWarnings(library(tibble)))
suppressMessages(suppressWarnings(library(RColorBrewer)))


clusteraverages_all <- data.frame(matrix(nrow=maxkclust,ncol=maxkclust))
colnames(clusteraverages_all) <- paste(rep("TotalClust"),1:maxkclust,sep="")
rownames(clusteraverages_all) <- paste(rep("AvgCluster"),1:maxkclust,sep="")

myfilenames <- list.files(pattern=".txt")
myfilenames <- myfilenames[which(str_detect(myfilenames,myslice)==TRUE)]
myfilelist <- lapply(myfilenames,read.table)

######################### Average data #####################################
############################################################################

myfiles <- as.data.frame(matrix(ncol=length(myfilelist)+5,
                                nrow=nrow(myfilelist[[1]])))
colnames(myfiles) <- c("PixelID","X","Y",
                       gsub(".txt","",myfilenames),
                       "Avg","AvgGps")
myfiles$PixelID <- myfilelist[[1]][,1]
# myfiles$X <- rep(1:80,80)
myfiles$X <- rep(1:80,80)
# myfiles$Y <- rep(rev(1:80),each=80)
myfiles$Y <- rep(1:80,each=80)

for (i in 1:length(myfilelist)) {
  myfiles[,i+3] <- myfilelist[[i]][,2]
}

myfiles$Avg <- rowMeans(myfiles[,4:(ncol(myfiles)-2)])


pixelcutoff <- 2.902257/max(myfiles$Avg)


fromlargesttosmalleststn <- myfiles$PixelID[order(myfiles$Avg,decreasing = TRUE)]
tokeepid <- fromlargesttosmalleststn[1:length(fromlargesttosmalleststn)*pixelcutoff]
for (i in 1:nrow(myfiles)) {
  if (myfiles$PixelID[i] %in% tokeepid) {
    myfiles$AvgGps[i] <- myfiles$Avg[i]
  }
}

############################# Plot data ####################################
############################################################################

ggplot(myfiles,aes(x=X,y=Y)) +
  geom_tile(aes(fill=myfiles$AvgGps)) +
  # geom_tile(aes(fill=myfiles$`04-01-08`)) +
  labs(title=paste(dateSlice)) +
  theme(
    axis.title.y = element_blank(),
    axis.title.x = element_blank(),
    axis.ticks = element_blank(),
    axis.text = element_blank(),
    panel.background = element_blank(),
    legend.title = element_blank(),
    plot.title = element_text(hjust=0.5)
  ) +
  scale_y_reverse() +
  scale_fill_gradientn(colors=rev(c(
  "red1","yellow1","green1","dodgerblue1","navy"))
)

if (saveoriginalplot==1) {
  ggsave("Step0_AvgHeatmap.jpg",height=plotheight,width=plotwidth)
}

######### hierarchical clustering: find optimal number of clusters  ########
############################################################################

idAvgNotNa <- which(!is.na(myfiles$AvgGps))
mycolids <- c(which(colnames(myfiles)=="PixelID"),which(colnames(myfiles)=="X"),
              which(colnames(myfiles)=="Y"),which(colnames(myfiles)=="AvgGps"))
myclusterdata <- myfiles[idAvgNotNa,mycolids]

myclustAvgGps_df_sc <- as.data.frame(myclusterdata$AvgGps)

elbowplot <- fviz_nbclust(myclustAvgGps_df_sc, hcut, method = "wss")  #hcut based on hclust which is agglomerative
elbowplot
if (saveelbowplot==1) {
  ggsave("Step1a_elbowplot.jpeg",height=plotheight,width=plotwidth)
}

silhouetteplot <- fviz_nbclust(myclustAvgGps_df_sc, hcut, method = "silhouette")
silhouetteplot
if (savesilhouetteplot==1) {
  ggsave("Step1b_silhouetteplot.jpeg",height=plotheight,width=plotwidth)
}
# gap plot takes too long to make and usually says only one cluster

################# hierarchical clustering: loop through all k ###################
############################################################################

for (k in 2:maxkclust) {
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

########## Loop through all clusters and plot each cluster #################

  clusteraverages <- data.frame(matrix(ncol=2,nrow=k))
  colnames(clusteraverages) <- c("k","StN_Avg")
  clusteraverages$k <- seq(1:k)
  for (i in 1:k) {
    allcolmeans <- colMeans(myfiles_df_cl[which(myfiles_df_cl$Cluster==i),])
    clusteraverages$StN_Avg[i] <- allcolmeans[which(colnames(myfiles_df_cl)=="AvgGps")]
    clusteraverages_all[i,k] <- clusteraverages$StN_Avg[i]
  }
  
  ggplot(myfiles_df_cl,aes(x=X,y=Y)) +
    geom_tile(aes(fill=myfiles_df_cl$Cluster)) +
    labs(title=dateSlice) +
    theme(
      axis.title.y = element_blank(),
      axis.title.x = element_blank(),
      axis.ticks = element_blank(),
      axis.text = element_blank(),
      panel.background = element_blank(),
      legend.title = element_blank(),
      plot.title = element_text(hjust=0.5)
    ) +
    guides(fill = guide_legend(keyheight = 0.9)) +
    scale_y_reverse() +
    scale_fill_gradientn(breaks=seq(1:k),
                         labels=round(clusteraverages$StN_Avg,3),
                         colors=rev(c("red1","yellow1","green1","dodgerblue1","navy"))
    )
  
  clusterplotname <- paste(k,"_ClusteredAvgHeatmap.jpeg",sep="")
  if (saveclusterplot==1) {
    ggsave(clusterplotname,height=plotheight,width=plotwidth)
  }
}  

####################### Save cluster data as csv ###########################
############################################################################

write.csv(myclusterdata,"EachPixel_Cluster.csv",row.names = FALSE)
write.csv(myfiles,"EachPixel_Data.csv",row.names = FALSE)
