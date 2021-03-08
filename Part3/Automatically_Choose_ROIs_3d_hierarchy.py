
# MAKE SURE THAT ENABLE SO CAN DO WITHOUT NEEDING ELECTRODE TO BE IN VIEW
# AT THE END OF EVERY STEP MAKE SURE THERE'S A PLOT COMING OUT AND A SET OF
# .DAT FILES SO CAN FEED INTO PHOTOZ TO SEE OPTIONS

# SEE IF CAN MAKE PLOTS OF 3D HIERARCHICAL CLUSTERING

####################################### Load initial values, libraries, and data ######################################

# date = "2020-12-29"
# slice = "01-01"
xdim = 80 #number of pixels in X dimension
ydim = 80 #number of pixels in Y dimension
snr_cutoff = 4 #minimum SNR value to be included in clustering
# date_slice = date + " " + slice

clusters = np.loadtxt("Clusters_for_python.txt")
clusters_w_electrode = np.loadtxt("Clusters_w_Electrode_for_python.txt")

import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
import itertools
from scipy.interpolate import griddata
# import plotly.plotly as py














######################################## Average and plot SNR and amplitude data #######################################

files = os.listdir(os.curdir)  #list all files in current directory

amp_files = [file for file in files if "_amp" in file] #list of files with amplitude value for each pixel
amp_array = np.zeros([xdim*ydim,len(amp_files)+1]) #create empty array for amplitude data
nfile = 0
for file in files: #import each amplitude file into a column of the amplitude array
    if "_amp" in file:
        amp = np.loadtxt(file)
        amp_array[:,nfile] = amp[:,1]
        nfile += 1
        amp_plot = np.reshape(amp[:,1],(xdim,ydim))
        # plt.matshow(amp_plot)
        # plt.show()
        # plt.savefig("Amp_" + str(file.replace("_amp.txt", "")) + ".jpg")
amp_mean = np.mean(amp_array[:,0:4],axis=1)
amp_array[:,nfile] = amp_mean #row mean of amplitude array placed in last column

amp_mean_plot = np.reshape(amp_mean,(xdim,ydim))
# plt.matshow(amp_mean_plot)
# plt.show()
# plt.savefig("Amp_avg.jpg")

snr_files = [file for file in files if "_snr" in file] #list of files with snr value for each pixel
snr_array = np.zeros([xdim*ydim,len(snr_files)+1]) #create empty array for amplitudesnrdata
nfile = 0
for file in files: #import each snr file into a column of the snr array
    if "_snr" in file:
        snr = np.loadtxt(file)
        snr_array[:,nfile] = snr[:,1]
        nfile += 1
        snr_plot = np.reshape(snr[:,1],(xdim,ydim))
        # plt.matshow(snr_plot)
        # plt.show()
        # plt.savefig("SNR_" + str(file.replace("_snr.txt", "")) + ".jpg")
snr_mean = np.mean(snr_array[:,0:4],axis=1)
snr_array[:,nfile] = snr_mean #row mean of snr array placed in last column

snr_mean_plot = np.reshape(snr_mean,(xdim,ydim))
# plt.matshow(snr_mean_plot)
# plt.show()
# plt.savefig("SNR_avg.jpg")

################################################ Hierarchical clustering ###############################################

# print(snr_mean)
# plt.figure(figsize=(10,7))
# plt.title("Dendrograms")
# print(len(np.array(snr_mean)))
# dend = shc.dendrogram(shc.linkage(np.array(snr_array[:,nfile])))
# hc = AgglomerativeClustering(n_clusters = 2,affinity='euclidean',linkage='ward')
# y_hc = hc.fit_predict(snr_mean)

# print(snr_plot)
snr_coords = np.zeros([(xdim*ydim),4])
snr_coords[:,2] = snr_mean
snr_coords[:,0] = np.repeat(range(ydim),xdim)
snr_coords[:,1] = list(range(ydim))*xdim

# print(snr_coords)
snr_coords_cluster = snr_coords[snr_coords[:,2] > snr_cutoff]
# print(snr_coords_cluster)

# kmeans = KMeans(n_clusters=2)
# snr_coords_cluster['label'] = kmeans.fit_predict(snr_coords_cluster[:,2])
# print(snr_coords_cluster)
# ax = snr_coords_cluster[snr_coords_cluster['label']==0].plot.scatter(x=snr_coords_cluster[:,2] y=snr_coords_cluster[:,3], s=50, color='white', edgecolor='black')
# snr_coords_cluster[snr_coords_cluster['label']==1].plot.scatter(x=snr_coords_cluster[:,2], y='label', s=50, color='white', ax=ax, edgecolor='red')
# plt.scatter(kmeans.cluster_centers_.ravel(), [0.5]*len(kmeans.cluster_centers_), s=100, color='green', marker='*')



# fig = plt.figure()
# ax = plt.axes(projection='3d')
# xi = np.linspace(min(snr_coords[:,0]),max(snr_coords[:,1]))
# yi = np.linspace(min(snr_coords[:,1]),max(snr_coords[:,0]))
# X, Y = np.meshgrid(xi,yi)
# Z = f(X,Y)
# Z = griddata(snr_coords[:,0],snr_coords[:,1],snr_coords[:,2],xi,yi)
# ax.scatter(snr_coords[:,0],snr_coords[:,1],snr_coords[:,2])
# ax.plot(snr_coords[:,0],snr_coords[:,1],snr_coords[:,2])
# ax.contour3D(snr_coords[:,0],snr_coords[:,1],snr_coords[:,2],50)
# plt.show()


# print(snr_coords_cluster)
# snr_coords_cluster[:,2] =  snr_coords_cluster[:,2]*10
# print(snr_coords_cluster)
#
# plt.figure(figsize=(17,4),dpi=280)
# plt.title("Dendrogram",fontsize=22)
# dend = shc.dendrogram(shc.linkage(snr_coords_cluster,method='ward'))
# plt.xticks(fontsize=6)
# # plt.show()
# plt.savefig("Dendrogram.jpg")

cluster = AgglomerativeClustering(n_clusters = 10,affinity='euclidean',linkage='ward')
clustered_pixel_list = cluster.fit_predict(snr_coords_cluster)
# print(clustered_pixel_list)
clustered_pixel = 0
for row in range(len(snr_coords[:,2])):
    # print(row)
    if snr_coords[row,2] < snr_cutoff:
        snr_coords[row,3] = np.nan
    else:
        snr_coords[row,3] = clustered_pixel_list[clustered_pixel]
        clustered_pixel += 1
print(snr_coords)

cluster_plot = np.reshape(snr_coords[:,3],(xdim,ydim))
plt.matshow(cluster_plot)
plt.show()

# print(snr_array)
# snr_clustered = np.zeros([xdim,ydim])
# snr_clustered[snr_clustered < snr_cutoff] = NA
# print(snr_clustered)
# for row_element in range(ydim):
#     for col_element in range(xdim):
#         print(snr_array[row_element,col_element])
        # if snr_coords[row_element] < snr_cutoff:
        #     snr_clustered[element] = numpy.nan
# print(snr_clustered)

# fig = plt.figure()
# ax = plt.axes(projection='3d')
# xi = np.linspace(min(snr_coords[:,0]),max(snr_coords[:,1]))
# yi = np.linspace(min(snr_coords[:,1]),max(snr_coords[:,0]))
# X, Y = np.meshgrid(xi,yi)
# Z = f(X,Y)
# Z = griddata(snr_coords[:,0],snr_coords[:,1],snr_coords[:,2],xi,yi)
# ax.scatter(snr_coords_cluster[:,0],snr_coords_cluster[:,1],snr_coords_cluster[:,2],c=KF)
# ax.plot(snr_coords_cluster[:,0],snr_coords_cluster[:,1],snr_coords_cluster[:,2],c=KF)
# # ax.plot(snr_coords[:,0],snr_coords[:,1],snr_coords[:,2])
# # ax.contour3D(snr_coords[:,0],snr_coords[:,1],snr_coords[:,2],50)
# plt.show()



# kmeans = KMeans(n_clusters=2)
# kmeans = kmeans.fit(snr_coords)
# labels = kmeans.predict(snr_coords)
# scatter = dict(
#     mode="markers",
#     name="y",
#     type = "scatter3d",
#     x=snr_coords[:, 0], y=snr_coords[:, 1], z=snr_coords[:, 2]
# )
# clusters = dict(
#     alphahull = 7,
#     name = "y",
#     type = "mesh3d",
#     x=snr_coords[:,0],y=snr_coords[:,1],z=snr_coords[:,2]
# )
# fig = dict(data=[scatter,clusters])
# py.iplot(fig)
# print(snr_coords)
# print(np.repeat(range(9),2))
# print([range(xdim-1)]*ydim)
# clusters = 2
# kmeans = KMeans(n_clusters = clusters)
# kmeans.fit(snr_mean.reshape(-1,1))
# print(kmeans.labels_)


################################################### Plot dendrogram ####################################################

################################ Choose and plot number of clusters based on dendrogram ################################

######################################## Remove cluster with lowest SNR and replot #####################################

################################ Identify and plot potential ROIs and bounds for each ROI ##############################

##################################### Remove ROIs with diameter outside cutoff range ###################################

############################################ Plot remaining ROIs and electrode #########################################

##################################### Remove ROIs touching each other or electrode #####################################

############################################ Plot remaining ROIs and electrode #########################################

############################################## Remove ROIs with SNR < cutoff ###########################################

############################################ Plot remaining ROIs and electrode #########################################

########################################### Remove ROIs with amplitude < cutoff ########################################

############################################ Plot remaining ROIs and electrode #########################################

################################################ Export ROIs as .dat files #############################################




