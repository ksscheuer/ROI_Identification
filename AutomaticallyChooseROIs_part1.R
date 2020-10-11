
########################## Set initial values###############################
############################################################################

maxkclust <- 10 #maximum number of potential clusters
# pixelcutoff <- 0.5 #before clustering, eliminate pixels with lowest SNR
myslice <- "03-01"
# myslice_plot_name <- "01-01"
mydate <- "06-26-2019"
dateSlice <- paste(mydate,myslice,sep=" ")

# saveoriginalplot <- 1 #1 = save, 0 = don't save
# saveelbowplot <- 1 #1 = save, 0 = don't save
# savesilhouetteplot <- 1 #1 = save, 0 = don't save
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
suppressMessages(suppressWarnings(library(stringr)))

clusteraverages_all <- data.frame(matrix(nrow=maxkclust,ncol=maxkclust))
colnames(clusteraverages_all) <- paste(rep("TotalClust"),1:maxkclust,sep="")
rownames(clusteraverages_all) <- paste(rep("AvgCluster"),1:maxkclust,sep="")

myfilenames <- list.files(pattern=".txt")
nostimfilenames <- myfilenames[str_detect(myfilenames,"_noStim")]
myfilenames <- myfilenames[!str_detect(myfilenames,"_noStim")]
nostimfilelist <- lapply(nostimfilenames,read.table)
myfilelist <- lapply(myfilenames,read.table)

################ Find SNR cutoff based on no stim file #####################
############################################################################

nostimfiles <- as.data.frame(matrix(ncol=length(nostimfilelist)+1,
                                nrow=nrow(myfilelist[[1]])))
colnames(nostimfiles) <- c(gsub(".txt","",nostimfilenames),"Average")
for (i in 1:length(nostimfilelist)) {
  nostimfiles[,i] <- nostimfilelist[[i]][,2]
}

if (length(nostimfilelist) > 1) {
  nostimfiles$Average <- rowMeans(nostimfiles[,1:(length(nostimfiles)-1)])
} else {
  nostimfiles$Average <- nostimfiles[,1]
}

SNRcutoff <- qnorm(0.95,mean=mean(nostimfiles$Average),sd=sd(nostimfiles$Average))

################ Plot SNR cutoff based on no stim file #####################
############################################################################

ggplot(nostimfiles,aes(x=nostimfiles$Average)) +
  geom_density() +
  labs(x="SNR",title=paste("No Stim SNR, 95th %ile Cutoff = ",round(SNRcutoff,3))) +
  geom_vline(xintercept=SNRcutoff) +
  theme_bw() +
  theme(plot.title = element_text(hjust = 0.5))

ggsave("Step0a_SNRcutoff.jpg")

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

myfiles_SNRcutoff <- myfiles[,c(1:(ncol(myfiles)-2))]
for (i in 1:length(myfilenames)) {
  for (j in 1:nrow(myfiles_SNRcutoff)) {
    if (myfiles_SNRcutoff[j,3+i] <= SNRcutoff) {
      myfiles_SNRcutoff[j,3+i] <- NA
    }
  }
}


myfiles$Avg <- rowMeans(myfiles[,4:(ncol(myfiles)-2)])
myfiles$AvgGps <- myfiles$Avg
for (i in 1:nrow(myfiles)) {
  if (myfiles$Avg[i] <= SNRcutoff) {
    myfiles$AvgGps[i] <- NA
  }
}

############################# Plot data ####################################
############################################################################

for (i in 1:(ncol(myfiles_SNRcutoff)-3)) {
  ggplot(myfiles_SNRcutoff,aes(x=X,y=Y)) +
    geom_tile(aes(fill=myfiles_SNRcutoff[,3+i])) +
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
  ggsave(paste("Step0b_IndivHeatmap_",colnames(myfiles_SNRcutoff)[i+3],".jpg",sep=""))
}

ggplot(myfiles,aes(x=X,y=Y)) +
  geom_tile(aes(fill=myfiles$AvgGps)) +
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
ggsave("Step0c_AvgHeatmap.jpg",height=plotheight,width=plotwidth)

######### hierarchical clustering: find optimal number of clusters  ########
############################################################################

idAvgNotNa <- which(!is.na(myfiles$AvgGps))
mycolids <- c(which(colnames(myfiles)=="PixelID"),which(colnames(myfiles)=="X"),
              which(colnames(myfiles)=="Y"),which(colnames(myfiles)=="AvgGps"))
myclusterdata <- myfiles[idAvgNotNa,mycolids]

myclustAvgGps_df_sc <- as.data.frame(myclusterdata$AvgGps)

elbowplot <- fviz_nbclust(myclustAvgGps_df_sc, hcut, method = "wss")  #hcut based on hclust which is agglomerative
elbowplot
ggsave("Step1a_elbowplot.jpeg",height=plotheight,width=plotwidth)


silhouetteplot <- fviz_nbclust(myclustAvgGps_df_sc, hcut, method = "silhouette")
silhouetteplot
ggsave("Step1b_silhouetteplot.jpeg",height=plotheight,width=plotwidth)
# gap plot takes too long to make and usually says only one cluster

####################### Save cluster data as csv ###########################
############################################################################

write.csv(myclusterdata,"EachPixel_Cluster.csv",row.names = FALSE)
write.csv(myfiles,"EachPixel_Data.csv",row.names = FALSE)
