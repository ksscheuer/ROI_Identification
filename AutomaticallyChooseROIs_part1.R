############### Load libraries and set initial values ######################
############################################################################

library(stringr)
library(ggplot2)
library(Ckmeans.1d.dp)
library(factoextra)

xdim <- 80 #pixels in X direction
ydim <- 80 #pixels in Y direction
SNRcutoff_choice <- "pre-stim max" #add RMS noise (sqrt(mean(prestim_data$Avg^2)))
  #can be pre-set value eg 4, "pre-stim mean" for the mean of the SNR values 
  #before stimulus, "pre-stim 95%ile" for 95th percentile of SNR values 
  #before stimulus, or "pre-stim max" for the maximum value of SNR values 
  #before stimulus, or "RMS" for root mean square noise calculated as
  #squareroot fo the mean of squared(average pre-stimulus SNR values)
k_choice <- "automatic"
  #can be pre-set value or automatically determined based on BIC (see 
  #Ckmeans.1d.dp package for details)


########################### Load files #####################################
############################################################################

prestim_filenames <- list.files(pattern=".txt")[str_detect(list.files(pattern=".txt"),"_preStim")]
  #list of file names for files containing SNR values before stimulus
amp_filenames <- list.files(pattern=".txt")[str_detect(list.files(pattern=".txt"),"_amp")]
  #list of file names for files containing amplitude values
snr_filenames <- list.files(pattern=".txt")[str_detect(list.files(pattern=".txt"),"_snr")]
  #list of file names for files containing SNR values
  
########################## Average data ####################################
############################################################################

prestim_data <- data.frame(matrix(nrow=xdim*ydim,ncol=length(prestim_filenames)+1))
colnames(prestim_data) <- c(gsub("_preStim.txt","",prestim_filenames),"Avg")
if (length(prestim_filenames) > 1) {
  for (i in 1:length(prestim_filenames)) {
    prestim_data[,i] <- read.table(prestim_filenames[i])[,2]
  }
  prestim_data[,ncol(prestim_data)] <- rowMeans(prestim_data[,1:ncol(prestim_data)-1])
} else if (length(prestim_filenames) == 1) {
  warning("Only one file with pre-stimulus SNR values.")
  prestim_data[,1] <- read.table(prestim_filenames[1])[,2]
  prestim_data[,2] <- read.table(prestim_filenames[1])[,2]
}
  #create, name, and fill matrix where each column contains SNR values 
  #before stimulus for one prestim file and last column contains average
  #SNR value before stimulus across all trials

amp_data <- data.frame(matrix(nrow=xdim*ydim,ncol=length(amp_filenames)+1))
colnames(amp_data) <- c(gsub("_amp.txt","",amp_filenames),"Avg")
if (length(amp_filenames) > 1) {
  for (i in 1:length(amp_filenames)) {
    amp_data[,i] <- read.table(amp_filenames[i])[,2]
  }
  amp_data[,ncol(amp_data)] <- rowMeans(amp_data[,1:ncol(amp_data)-1])
} else if (length(amp_filenames) == 1) {
  warning("Only one file with amplitude values.")
  amp_data[,1] <- read.table(amp_filenames[1])[,2]
  amp_data[,2] <- read.table(amp_filenames[1])[,2]
}
  #create, name, and fill matrix where each column contains amplitude
  #values before stimulus for one amp file and last column contains 
  #amplitude value before stimulus across all trials

snr_data <- data.frame(matrix(nrow=xdim*ydim,ncol=length(snr_filenames)+1))
colnames(snr_data) <- c(gsub("_snr.txt","",snr_filenames),"Avg")
if (length(snr_filenames) > 1) {
  for (i in 1:length(snr_filenames)) {
    snr_data[,i] <- read.table(snr_filenames[i])[,2]
  }
  snr_data[,ncol(snr_data)] <- rowMeans(snr_data[,1:ncol(snr_data)-1])
} else if (length(snr_filenames) == 1) {
  warning("Only one file with SNR values.")
  snr_data[,1] <- read.table(snr_filenames[1])[,2]
  snr_data[,2] <- read.table(snr_filenames[1])[,2]
}
  #create, name, and fill matrix where each column contains SNR values 
  #for one SNR file and last column contains average SNR value across
  #all trials

############################ SNR cutoff ####################################
############################################################################

#set and plot SNR cutoff based on choice made at top of file
if (SNRcutoff_choice == "pre-stim mean") {
  SNRcutoff <- mean(prestim_data$Avg)
  ggplot(prestim_data,aes(x=Avg)) +
    geom_density() +
    labs(x="SNR",title=paste("Mean Pre-Stimulus SNR = ",round(SNRcutoff,3))) +
    geom_vline(xintercept=SNRcutoff) +
    theme_bw() +
    theme(plot.title = element_text(hjust = 0.5))
  ggsave("Step1_SNR_Cutoff.jpg")
} else if (SNRcutoff_choice == "pre-stim 95%ile") {
  SNRcutoff <- qnorm(0.95,mean=mean(prestim_data$Avg),sd=sd(prestim_data$Avg))
  ggplot(prestim_data,aes(x=Avg)) +
    geom_density() +
    labs(x="SNR",title=paste("95th Percentile Pre-Stimulus SNR = ",round(SNRcutoff,3))) +
    geom_vline(xintercept=SNRcutoff) +
    theme_bw() +
    theme(plot.title = element_text(hjust = 0.5))
  ggsave("Step1_SNR_Cutoff.jpg")
} else if (SNRcutoff_choice == "pre-stim max") {
  SNRcutoff <- max(prestim_data$Avg)
  ggplot(prestim_data,aes(x=Avg)) +
    geom_density() +
    labs(x="SNR",title=paste("Max Pre-Stimulus SNR = ",round(SNRcutoff,3))) +
    geom_vline(xintercept=SNRcutoff) +
    theme_bw() +
    theme(plot.title = element_text(hjust = 0.5))
  ggsave("Step1_SNR_Cutoff.jpg")
} else if (SNRcutoff_choice == "RMS") {
  SNRcutoff <- sqrt(mean(prestim_data$Avg^2))
  ggplot(prestim_data,aes(x=Avg)) +
    geom_density() +
    labs(x="SNR",title=paste("RMS Noise for SNR = ",round(SNRcutoff,3))) +
    geom_vline(xintercept=SNRcutoff) +
    theme_bw() +
    theme(plot.title = element_text(hjust = 0.5))
  ggsave("Step1_SNR_Cutoff.jpg")
} else {
  SNRcutoff <- SNRcutoff_choice
  ggplot(prestim_data,aes(x=Avg)) +
    geom_density() +
    labs(x="SNR",title=paste("SNR Cutoff = ",SNRcutoff)) +
    geom_vline(xintercept=SNRcutoff) +
    theme_bw() +
    theme(plot.title = element_text(hjust = 0.5))
  ggsave("Step1_SNR_Cutoff.jpg")
}

############################## Plot SNR ####################################
############################################################################

#plot SNR values for each file and the overall average
snr_coords_data <- data.frame(rep(1:ydim,xdim),rep(1:ydim,each=xdim),snr_data)
colnames(snr_coords_data) <- c("X","Y",colnames(snr_data))
for (i in 3:ncol(snr_data)+2) {
  ggplot(snr_coords_data,aes(x=X,y=Y)) +
    geom_tile(aes(fill=snr_coords_data[,i])) +
    labs(title=paste(colnames(snr_coords_data)[i]," SNR")) +
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
  ggsave(paste("Step1_SNR_",colnames(snr_coords_data)[i],".jpg",sep=""),width=6.5,height=6)
}

snr_coords_data["Avg_cutoff"] <- snr_coords_data$Avg
for (i in 1:nrow(snr_coords_data)) {
  if (snr_coords_data$Avg_cutoff[i]<SNRcutoff) {
    snr_coords_data$Avg_cutoff[i] <- NA
  }
}

#plot SNR values for average, excluding pixels where SNR < cutoff
ggplot(snr_coords_data,aes(x=X,y=Y)) +
  geom_tile(aes(fill=Avg_cutoff)) +
  labs(title=paste("SNR > Cutoff of ",round(SNRcutoff,3))) +
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
ggsave(paste("Step1_SNR_Over_Cutoff.jpg"),width=6.5,height=6)

################# One-dimensional K-means clustering #######################
############################################################################

# snr_vals_to_cluster <- intersect(which(snr_data$Avg>SNRcutoff),which(!is.na(snr_data$Avg)))
clustering_results <- Ckmeans.1d.dp(snr_coords_data$Avg_cutoff[which(!is.na(snr_coords_data$Avg_cutoff))],
                                    k=c(1,20))
  #using only SNR values > cutoff, perform K-means clustering optimized for 
  #one-dimensional data (see Ckmeans.1d.dp package and "Ckmeans.1d.dp: 
  #Optimal k-means Clustering in One dimension by Dynamic Programming" by 
  #Wang, H. and Song, M. published in The R Journal Vol 3/2 Dec 2011)

#automatically choose number of clusters based on BIC value or manually 
#determine number of clusters
if (k_choice == "automatic") { 
  k <- max(clustering_results$cluster)
} else {
  k <- k_choice
}

#pair each pixel with SNR value > cutoff with appropriate cluster value
counter <- 1
cluster_coords_data <- data.frame(matrix(ncol=5,nrow=xdim*ydim))
colnames(cluster_coords_data) <- c("X","Y","SNR","Cluster","Cluster_w_Electrode")
cluster_coords_data[,1:3] <- snr_coords_data[,c(1,2,ncol(snr_coords_data)-1)]
for (i in 1:nrow(cluster_coords_data)) {
  if (!(is.na(cluster_coords_data$SNR[i])) & cluster_coords_data$SNR[i] >= SNRcutoff) {
    cluster_coords_data$Cluster[i] <- clustering_results$cluster[counter]
    counter <- counter + 1
  }
}

#plot clusters
ggplot(cluster_coords_data,aes(x=X,y=Y)) +
  geom_tile(aes(fill=Cluster)) +
  labs(title=paste("Clusters = ",k)) +
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
  scale_fill_gradientn(breaks=seq(1:k),labels=paste(round(clustering_results$centers,3)),
    colors=rev(c(
    "red1","yellow1","green1","dodgerblue1","navy"))
  )
ggsave("Step2_Clusters.jpg",width=6.5,height=6)

###################### Indicate electrode location #########################
############################################################################

#add column which contains electrode location such that pixel in electrode 
#= 1 and all other pixels = 0, find coordinate boundaries of electrode
cluster_coords_data["Electrode"] <- 0
if ("electrode.csv" %in% list.files()) {
  electrode_pixels <- read.csv("electrode.csv")
  electrode_pixels <- electrode_pixels + 1 #because python starts counting at 0
  for (i in 1:nrow(electrode_pixels)) {
    # cluster_coords_data$Clusters_w_Electrode[electrode_pixels[i,1]] <- k+1
    cluster_coords_data$Electrode[electrode_pixels[i,1]] <- 1
  }
  electrode_loc <- data.frame(matrix(ncol=5,nrow=1))
  colnames(electrode_loc) <- c("X_min","Y_min","Y_max","X_tip","Y_tip")
  electrode_loc$X_min <- min(cluster_coords_data$X[which(cluster_coords_data$Electrode==1)])
  electrode_loc$Y_min <- min(cluster_coords_data$Y[which(cluster_coords_data$Electrode==1)])
  electrode_loc$Y_max <- max(cluster_coords_data$Y[which(cluster_coords_data$Electrode==1)])
  electrode_loc$X_tip <- max(cluster_coords_data$X[which(cluster_coords_data$Electrode==1)])
  electrode_loc$Y_tip <- (electrode_loc$Y_min + electrode_loc$Y_max)/2
} else warning("Cannot locate file with electrode pixels.")

############################## Save values #################################
############################################################################

write.table(prestim_data,"PreStim_all.txt",row.names = FALSE)
write.table(amp_data,"Amp_all.txt",row.names = FALSE)
write.table(snr_coords_data,"SNR_all.txt",row.names = FALSE)
write.table(cluster_coords_data,"Clusters_all.txt",row.names = FALSE)
write.table(electrode_loc,"Electrode_coords.txt",row.names = FALSE,col.names = FALSE)

#save cluster values as xdim by ydim matrix ready for import to Python
clusters_for_python <- t(matrix(cluster_coords_data$Cluster, ncol=xdim, nrow=ydim))
clusters_for_python[which(is.na(clusters_for_python))] <- 0
write.table(clusters_for_python,"Clusters_for_python.txt",row.names = FALSE,col.names = FALSE)

#save average SNR values as xdim by ydim matrix ready for import to Python
snr_for_python <- t(matrix(cluster_coords_data$SNR, ncol=xdim, nrow=ydim))
snr_for_python[which(is.na(snr_for_python))] <- 0
write.table(snr_for_python,"SNR_for_python.txt",row.names = FALSE,col.names = FALSE)

#save average SNR values as xdim by ydim matrix ready for import to Python
snr_for_python <- t(matrix(cluster_coords_data$SNR, ncol=xdim, nrow=ydim))
write.table(snr_for_python,"SNR_for_python.txt",row.names = FALSE,col.names = FALSE)

#save average amplitude values as xdim by ydim matrix ready for import to Python
amp_for_python <- t(matrix(amp_data$Avg, ncol=xdim, nrow=ydim))
write.table(amp_for_python,"Amp_for_python.txt",row.names = FALSE,col.names = FALSE)

#save pixels indicating electrode location (electrode pixel = 1, other pixels
#= 0 as xdim by ydim matrix ready for import to Python
Electrode_for_python <- t(matrix(cluster_coords_data$Electrode, ncol=xdim, nrow=ydim))
Electrode_for_python[which(is.na(Electrode_for_python))] <- 0
write.table(Electrode_for_python,"Electrode_for_python.txt",row.names = FALSE,col.names = FALSE)
