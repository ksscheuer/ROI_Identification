############################## Identify each potential ROI and bounds for each ROI #####################################
#
import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(suppress=True) #prevent np exponential notation on print
np.set_printoptions(threshold=np.inf) #print all values in numpy array
# import pandas
# import scipy
# import collections
# from collections import Counter

ROI_diameter_cutoff = 3
SNR_cutoff = 3.8
Amp_cutoff = 0.001
Dat_all_potential = True #if true, will produce .dat files for all potential ROIs
Dat_diameter = True #if true, will produce .dat files for all ROIs with diameter <= cutoff
Dat_not_touching = True #if true, will produce .dat files for all ROIs not touching
Dat_snr_cutoff = True #if true, will produce .dat files for all ROIs with SNR > cutoff
Dat_amp_cutoff = True #if true, will produce .dat files for all ROIs with amp > cutoff
Dat_snr_amp_cutoff = True #if true, will produce .dat files for all ROIs with SNR and amp > cutoff

pixel_cluster_data = np.loadtxt("Clusters_for_python.txt")
electrode_data = np.loadtxt("Electrode_for_python.txt")
electrode_coords = np.loadtxt("Electrode_coords.txt")
snr_data = np.loadtxt("SNR_for_python.txt")
amp_data = np.loadtxt("Amp_for_python.txt")
width = len(pixel_cluster_data)
height = len(pixel_cluster_data[0])

k = np.amax(pixel_cluster_data)

cluster_results = np.zeros((width, height))
rlimit = 5000

import sys

sys.setrecursionlimit(rlimit + 1)

def combine_bound(bound1, bound2):
    if bound2 is None:
        return bound1
    if bound1 is None:
        return bound2
    result = [
        min(bound1[0], bound2[0]),
        max(bound1[1], bound2[1]),
        min(bound1[2], bound2[2]),
        max(bound1[3], bound2[3])
    ]
    return result

def check_cell(x, y, group_index, color, rdepth):
    cell_value = pixel_cluster_data[y][x]
    if (cell_value != 0 and
            cluster_results[y][x] == 0 and
            (color == 0 or cell_value == color)):
        if (rdepth >= rlimit):
            print("HIT RECURSION LIMIT OF {} AT CELL {} {} RESULTS INACCURATE.".format(rlimit, x, y))
            return None
        rdepth += 1
        cluster_results[y][x] = group_index
        my_bound = [x, x, y, y]
        xleft = max(0, x - 1)  # x coordinate of pixel to L
        xright = min(width - 1, x + 1)  # x coordinate of pixel to R
        yup = max(0, y - 1)  # y coordinate of pixel down in number / up in direction"
        ydown = min(height - 1, y + 1)  # y coordinate of pixel up in number / down in direction"
        child_bound = check_cell(xright, y, group_index, cell_value, rdepth)
        my_bound = combine_bound(my_bound, child_bound)
        child_bound = check_cell(xleft, y, group_index, cell_value, rdepth)
        my_bound = combine_bound(my_bound, child_bound)
        child_bound = check_cell(x, ydown, group_index, cell_value, rdepth)
        my_bound = combine_bound(my_bound, child_bound)
        child_bound = check_cell(x, yup, group_index, cell_value, rdepth)
        my_bound = combine_bound(my_bound, child_bound)
        return my_bound
    else:
        return None

group_index = 1  # 0 = never visited, 1 = first roi, 2 = second roi, etc
group_bound = []

for i in range(0, width):
    for j in range(0, height):
        result = check_cell(i, j, group_index, 0, 0)
        # print ("RETURN!", group_index)
        if result is not None:
            group_index += 1
            group_bound.append(result)

# to better see some clusters, decrease vmin and vmax
# plt.matshow(cluster_results,vmin=0,vmax=19)
# plt.show()

plt.matshow(cluster_results)
plt.title("All Potential ROIs, Clusters: %d" % (k), fontsize=13)
# plt.show()
plt.savefig("All_Potential_ROIs.jpg")

if Dat_all_potential == True:
    dat_file_all_potential_rois_data = np.zeros((width*height,4))
    dat_file_all_potential_rois_data[:,0] = range(height*width) #list of pixel IDs from 0 to width*height-1
    dat_file_all_potential_rois_data[:,1] = np.repeat(range(height),width) #y coordinates
    dat_file_all_potential_rois_data[:,2] = list(range(height))*width #y coordinates
    dat_file_all_potential_rois_data[:,3] = cluster_results.flatten() #final ROI clusters including electrode

    roi_index = 1
    final_roi_snr_vals = np.delete(np.unique(dat_file_all_potential_rois_data[:,3]),0)
    for roi in final_roi_snr_vals: #change ROI cluster values to be indexes not SNR values
        dat_file_all_potential_rois_data[dat_file_all_potential_rois_data[:,3] == roi,3] = roi_index
        roi_index = roi_index + 1

    n_rois_per_file = 50
    all_roi_indexes_list = range(1,int(np.amax(dat_file_all_potential_rois_data[:,3]))+1)

    roi_index_groups = [all_roi_indexes_list[i*n_rois_per_file:(i + 1)*n_rois_per_file] for i in range((len(all_roi_indexes_list) + n_rois_per_file - 1) // n_rois_per_file)]
    for group in roi_index_groups:
        group_dat_file_data = np.empty([0,4])
        for roi_index in group: #get pixel ids, x and y coordinates, roi indexes and electrode indexes for given group of ROIs
            roi_index_dat_file_all_potential_rois_data = dat_file_all_potential_rois_data[dat_file_all_potential_rois_data[:,3]==roi_index,:]
            group_dat_file_data = np.vstack([group_dat_file_data,roi_index_dat_file_all_potential_rois_data])
        group_rois_dat_file = np.zeros((1+3*int(np.amax(group_dat_file_data[:,3]))+len(group_dat_file_data[group_dat_file_data[:,3] != 0]),1))
        group_rois_dat_file[0,0] = np.amax(group_dat_file_data[:,3])
        group_rois_dat_list = group
        start_row_index = 1
        for roi_index in group_rois_dat_list:
            roi_index = int(roi_index)
            roi_n_pixels = len(group_dat_file_data[group_dat_file_data[:,3]==roi_index])
            group_rois_dat_file[start_row_index,0] = roi_index-1
            group_rois_dat_file[start_row_index+2, 0] = roi_index-1
            group_rois_dat_file[start_row_index+1,0] = roi_n_pixels+1
            group_rois_dat_file[start_row_index+3:start_row_index+3+roi_n_pixels,0] = group_dat_file_data[group_dat_file_data[:,3]==roi_index,0]
            start_row_index = start_row_index+2+roi_n_pixels+1
        np.savetxt("All_Potential_ROIs_"+str(min(group))+"_to_"+str(max(group))+".dat",group_rois_dat_file,fmt="%i")

############# Remove ROIs with diameter greater than cutoff ################
############################################################################

bound_limit = ROI_diameter_cutoff

for i in range(0,len(group_bound)):
  group = group_bound[i]
  # print(group)
  x_big = (group[1] - group[0]) > (bound_limit-1)
  y_big = (group[3] - group[2]) > (bound_limit-1)
  if x_big or y_big:
    cluster_results[cluster_results == (i+1)] = 0 #0 vs 1 index mismatch ie counting from 0 here but index from 1 above

# to see all ROIs, where each ROI is its own color
# plt.matshow(cluster_results,vmin=0,vmax=19)

plt.matshow(cluster_results)
plt.title("ROIs with Diameter < %d" % (ROI_diameter_cutoff),fontsize=13)
# plt.show()
plt.savefig("ROIS_Diameter_Within_Cutoff.jpg")

if Dat_diameter == True:
    dat_file_diameter_cutoff_rois_data = np.zeros((width*height,4))
    dat_file_diameter_cutoff_rois_data[:,0] = range(height*width) #list of pixel IDs from 0 to width*height-1
    dat_file_diameter_cutoff_rois_data[:,1] = np.repeat(range(height),width) #y coordinates
    dat_file_diameter_cutoff_rois_data[:,2] = list(range(height))*width #y coordinates
    dat_file_diameter_cutoff_rois_data[:,3] = cluster_results.flatten() #final ROI clusters including electrode

    roi_index = 1
    final_roi_snr_vals = np.delete(np.unique(dat_file_diameter_cutoff_rois_data[:,3]),0)
    for roi in final_roi_snr_vals: #change ROI cluster values to be indexes not SNR values
        dat_file_diameter_cutoff_rois_data[dat_file_diameter_cutoff_rois_data[:,3] == roi,3] = roi_index
        roi_index = roi_index + 1

    n_rois_per_file = 50
    all_roi_indexes_list = range(1,int(np.amax(dat_file_diameter_cutoff_rois_data[:,3]))+1)

    roi_index_groups = [all_roi_indexes_list[i*n_rois_per_file:(i + 1)*n_rois_per_file] for i in range((len(all_roi_indexes_list) + n_rois_per_file - 1) // n_rois_per_file)]
    for group in roi_index_groups:
        group_dat_file_data = np.empty([0,4])
        for roi_index in group: #get pixel ids, x and y coordinates, roi indexes and electrode indexes for given group of ROIs
            roi_index_dat_file_diameter_cutoff_rois_data = dat_file_diameter_cutoff_rois_data[dat_file_diameter_cutoff_rois_data[:,3]==roi_index,:]
            group_dat_file_data = np.vstack([group_dat_file_data,roi_index_dat_file_diameter_cutoff_rois_data])
        group_rois_dat_file = np.zeros((1+3*int(np.amax(group_dat_file_data[:,3]))+len(group_dat_file_data[group_dat_file_data[:,3] != 0]),1))
        group_rois_dat_file[0,0] = np.amax(group_dat_file_data[:,3])
        group_rois_dat_list = group
        start_row_index = 1
        for roi_index in group_rois_dat_list:
            roi_index = int(roi_index)
            roi_n_pixels = len(group_dat_file_data[group_dat_file_data[:,3]==roi_index])
            group_rois_dat_file[start_row_index,0] = roi_index-1
            group_rois_dat_file[start_row_index+2, 0] = roi_index-1
            group_rois_dat_file[start_row_index+1,0] = roi_n_pixels+1
            group_rois_dat_file[start_row_index+3:start_row_index+3+roi_n_pixels,0] = group_dat_file_data[group_dat_file_data[:,3]==roi_index,0]
            start_row_index = start_row_index+2+roi_n_pixels+1
        np.savetxt("ROIs_Diameter_Within_Cutoff_"+str(min(group))+"_to_"+str(max(group))+".dat",group_rois_dat_file,fmt="%i")

################ Separate remaining ROIs based on cluster ##################
############################################################################

# pixel_cluster_data = pixel_cluster_data * (cluster_results > 0)
#
# plt.matshow(pixel_cluster_data)
# plt.title("Clustered ROIs with Diam <= Cutoff Diam: %d" % (ROI_diameter_cutoff),fontsize=10)
# plt.show()

############################ Add electrode #################
############################################################

# to see just electrode plotted
# plt.matshow(electrode_data)
# plt.show()

electrode_data = electrode_data * (max(np.unique(cluster_results))+1) #0 if not in electrode, 1+max group number if in cluster
electrode_cluster = max(np.unique(pixel_cluster_data))+1
pixel_cluster_data_with_electrode = pixel_cluster_data

for i in range(0,width): #add electrode as new "roi"
  for j in range(0,height):
    if electrode_data[j][i] != 0:
      cluster_results[j][i] = electrode_data[j][i]
      pixel_cluster_data_with_electrode[j][i] = electrode_cluster

# plt.matshow(pixel_cluster_data)
# plt.title("Date: %s, Slice: %s, Diameter Cutoff: %d" % (mydate,myslice,ROI_diameter_cutoff),fontsize=13)
# plt.show()
# plt.savefig("Step5_Electrode_and_ROIS_with_Diameter_Less_than_or_Equal_to_Cutoff.jpg")

# Remove ROIs touching electrode #######################
############################################################################

electrode_x_min = electrode_coords[0]-1
electrode_x_max = electrode_coords[3]-1
electrode_y_max = electrode_coords[2]-1
electrode_y_min = electrode_coords[1]-1
# print (electrode_x_min,electrode_x_max,electrode_y_min,electrode_y_max)

rois_touching_electrode = []
for i in range(0,height):
  for j in range(0,width):
    cell_value = cluster_results[j][i]
    if cell_value!=0 and i>(electrode_x_min-2) and i<(electrode_x_max+2) and j>(electrode_y_min-2) and j<(electrode_y_max+2):
      rois_touching_electrode.append(cell_value)

rois_touching_electrode = np.unique(rois_touching_electrode)
# print (rois_touching_electrode)

for i in range(0,width):
  for j in range(0,height):
    cell_value = cluster_results[j][i]
    if cell_value in rois_touching_electrode:
      cluster_results[j][i] = 0
      pixel_cluster_data[j][i] = 0

# plt.matshow(pixel_cluster_data)
# plt.title("ROIs Not Touching Electrode",fontsize=13)
# plt.show()
# plt.savefig("ROIs_not_Touching_Electrode.jpg")

##################### Remove ROIs that are touching ########################
############################################################################

visited_cells = np.zeros((width,height))
def check_collisions(x,y,group_index):
  cell_value = cluster_results[y][x]
  # print ("cell_value",cell_value)
  if cell_value != 0 and visited_cells[y][x] == 0:
    visited_cells[y][x] = True
    if group_index == 0 or cell_value==group_index:
      xleft = max(0, x-1)
      xright = min(width-1, x+1)
      yup = max(0, y-1)
      ydown = min(height-1, y+1)
      check_collisions(x,yup,cell_value)
      check_collisions(xleft,yup,cell_value)
      check_collisions(xleft,y,cell_value)
      check_collisions(xleft,ydown,cell_value)
      check_collisions(x,ydown,cell_value)
      check_collisions(xright,ydown,cell_value)
      check_collisions(xright,y,cell_value)
      check_collisions(xright,yup,cell_value)
    else:
      # print ("Found collision",group_index,cell_value)
      cluster_results[cluster_results == group_index] = 0
      cluster_results[cluster_results == cell_value] = 0

for i in range(0,width):
  for j in range(0,height):
    result = check_collisions(i,j,0)

# to better see some clusters, decrease vmin and vmax
# plt.matshow(cluster_results,vmin=0,vmax=19)
# plt.show()

plt.matshow(cluster_results)
plt.title("ROIs not Touching",fontsize=13)
# plt.show()
plt.savefig("ROIs_Not_Touching.jpg")

if Dat_not_touching == True:
    dat_file_not_touching_data = np.zeros((width*height,4))
    dat_file_not_touching_data[:,0] = range(height*width) #list of pixel IDs from 0 to width*height-1
    dat_file_not_touching_data[:,1] = np.repeat(range(height),width) #y coordinates
    dat_file_not_touching_data[:,2] = list(range(height))*width #y coordinates
    dat_file_not_touching_data[:,3] = cluster_results.flatten() #final ROI clusters including electrode

    roi_index = 1
    final_roi_snr_vals = np.delete(np.unique(dat_file_not_touching_data[:,3]),0)
    for roi in final_roi_snr_vals: #change ROI cluster values to be indexes not SNR values
        dat_file_not_touching_data[dat_file_not_touching_data[:,3] == roi,3] = roi_index
        roi_index = roi_index + 1

    n_rois_per_file = 50
    all_roi_indexes_list = range(1,int(np.amax(dat_file_not_touching_data[:,3]))+1)

    roi_index_groups = [all_roi_indexes_list[i*n_rois_per_file:(i + 1)*n_rois_per_file] for i in range((len(all_roi_indexes_list) + n_rois_per_file - 1) // n_rois_per_file)]
    for group in roi_index_groups:
        group_dat_file_data = np.empty([0,4])
        for roi_index in group: #get pixel ids, x and y coordinates, roi indexes and electrode indexes for given group of ROIs
            roi_index_dat_file_not_touching_data = dat_file_not_touching_data[dat_file_not_touching_data[:,3]==roi_index,:]
            group_dat_file_data = np.vstack([group_dat_file_data,roi_index_dat_file_not_touching_data])
        group_rois_dat_file = np.zeros((1+3*int(np.amax(group_dat_file_data[:,3]))+len(group_dat_file_data[group_dat_file_data[:,3] != 0]),1))
        group_rois_dat_file[0,0] = np.amax(group_dat_file_data[:,3])
        group_rois_dat_list = group
        start_row_index = 1
        for roi_index in group_rois_dat_list:
            roi_index = int(roi_index)
            roi_n_pixels = len(group_dat_file_data[group_dat_file_data[:,3]==roi_index])
            group_rois_dat_file[start_row_index,0] = roi_index-1
            group_rois_dat_file[start_row_index+2, 0] = roi_index-1
            group_rois_dat_file[start_row_index+1,0] = roi_n_pixels+1
            group_rois_dat_file[start_row_index+3:start_row_index+3+roi_n_pixels,0] = group_dat_file_data[group_dat_file_data[:,3]==roi_index,0]
            start_row_index = start_row_index+2+roi_n_pixels+1
        np.savetxt("ROIs_Not_Touching_"+str(min(group))+"_to_"+str(max(group))+".dat",group_rois_dat_file,fmt="%i")

################## Keep ROIS > SNR Cutoff ##################################
############################################################################

roi_averages = np.zeros((width,height))

for roi_group_index in np.unique(cluster_results):
  location_index = (cluster_results == roi_group_index)
  snr_data_for_group = snr_data * location_index
  average = snr_data_for_group[snr_data_for_group != 0].mean()
  # if average > SNR_cutoff:
  #   print (average)
  # else:
  #   print ("Below SNR threshold.")
  roi_averages += (cluster_results == roi_group_index) * average

unique, counts = np.unique(roi_averages, return_counts=True)
snr_dict= dict(zip(unique, counts)) #make dictionary of snr/count pairs
background_snr = max(snr_dict, key=snr_dict.get) #find snr that occurs most often ie background
roi_averages[roi_averages == background_snr] = 0 #set background to 0

roi_averages[roi_averages < SNR_cutoff] = 0

plt.matshow(roi_averages)
# # plt.suptitle("Step 7a. ROIs with SNR > Cutoff",fontsize=15)
plt.title("ROIs with SNR > Cutoff",fontsize=13)
# plt.show()
plt.savefig("ROIs_With_SNR_Greater_Than_Cutoff.jpg")

if Dat_snr_cutoff == True:
    dat_file_greater_than_snr_cutoff_data = np.zeros((width*height,4))
    dat_file_greater_than_snr_cutoff_data[:,0] = range(height*width) #list of pixel IDs from 0 to width*height-1
    dat_file_greater_than_snr_cutoff_data[:,1] = np.repeat(range(height),width) #y coordinates
    dat_file_greater_than_snr_cutoff_data[:,2] = list(range(height))*width #y coordinates
    dat_file_greater_than_snr_cutoff_data[:,3] = cluster_results.flatten() #final ROI clusters including electrode

    roi_index = 1
    final_roi_snr_vals = np.delete(np.unique(dat_file_greater_than_snr_cutoff_data[:,3]),0)
    for roi in final_roi_snr_vals: #change ROI cluster values to be indexes not SNR values
        dat_file_greater_than_snr_cutoff_data[dat_file_greater_than_snr_cutoff_data[:,3] == roi,3] = roi_index
        roi_index = roi_index + 1

    n_rois_per_file = 50
    all_roi_indexes_list = range(1,int(np.amax(dat_file_greater_than_snr_cutoff_data[:,3]))+1)

    roi_index_groups = [all_roi_indexes_list[i*n_rois_per_file:(i + 1)*n_rois_per_file] for i in range((len(all_roi_indexes_list) + n_rois_per_file - 1) // n_rois_per_file)]
    for group in roi_index_groups:
        group_dat_file_data = np.empty([0,4])
        for roi_index in group: #get pixel ids, x and y coordinates, roi indexes and electrode indexes for given group of ROIs
            roi_index_dat_file_greater_than_snr_cutoff_data = dat_file_greater_than_snr_cutoff_data[dat_file_greater_than_snr_cutoff_data[:,3]==roi_index,:]
            group_dat_file_data = np.vstack([group_dat_file_data,roi_index_dat_file_greater_than_snr_cutoff_data])
        group_rois_dat_file = np.zeros((1+3*int(np.amax(group_dat_file_data[:,3]))+len(group_dat_file_data[group_dat_file_data[:,3] != 0]),1))
        group_rois_dat_file[0,0] = np.amax(group_dat_file_data[:,3])
        group_rois_dat_list = group
        start_row_index = 1
        for roi_index in group_rois_dat_list:
            roi_index = int(roi_index)
            roi_n_pixels = len(group_dat_file_data[group_dat_file_data[:,3]==roi_index])
            group_rois_dat_file[start_row_index,0] = roi_index-1
            group_rois_dat_file[start_row_index+2, 0] = roi_index-1
            group_rois_dat_file[start_row_index+1,0] = roi_n_pixels+1
            group_rois_dat_file[start_row_index+3:start_row_index+3+roi_n_pixels,0] = group_dat_file_data[group_dat_file_data[:,3]==roi_index,0]
            start_row_index = start_row_index+2+roi_n_pixels+1
        np.savetxt("ROIs_With_SNR_Greater_Than_Cutoff_"+str(min(group))+"_to_"+str(max(group))+".dat",group_rois_dat_file,fmt="%i")

################## Keep ROIS > Amp Cutoff ##################################
############################################################################

roi_amp_averages = np.zeros((width,height))

for roi_group_index in np.unique(cluster_results):
  location_index = (cluster_results == roi_group_index)
  amp_data_for_group = amp_data * location_index
  average = amp_data_for_group[amp_data_for_group != 0].mean()
  # if average > Amp_cutoff:
  #   print (average)
  # else:
  #   print ("Below Amp threshold.")
  roi_amp_averages += (cluster_results == roi_group_index) * average

unique, counts = np.unique(roi_amp_averages, return_counts=True)
amp_dict= dict(zip(unique, counts)) #make dictionary of snr/count pairs
background_amp = max(amp_dict, key=amp_dict.get) #find snr that occurs most often ie background
roi_amp_averages[roi_amp_averages == background_amp] = 0 #set background to 0

roi_amp_averages[roi_amp_averages < Amp_cutoff] = 0

plt.matshow(roi_amp_averages)
plt.title("ROIs with Amplitude > Cutoff",fontsize=13)
# plt.show()
plt.savefig("ROIs_With_Amp_Greater_Than_Cutoff.jpg")

if Dat_amp_cutoff == True:
    dat_file_greater_than_amp_cutoff_data = np.zeros((width*height,4))
    dat_file_greater_than_amp_cutoff_data[:,0] = range(height*width) #list of pixel IDs from 0 to width*height-1
    dat_file_greater_than_amp_cutoff_data[:,1] = np.repeat(range(height),width) #y coordinates
    dat_file_greater_than_amp_cutoff_data[:,2] = list(range(height))*width #y coordinates
    dat_file_greater_than_amp_cutoff_data[:,3] = cluster_results.flatten() #final ROI clusters including electrode

    roi_index = 1
    final_roi_snr_vals = np.delete(np.unique(dat_file_greater_than_amp_cutoff_data[:,3]),0)
    for roi in final_roi_snr_vals: #change ROI cluster values to be indexes not SNR values
        dat_file_greater_than_amp_cutoff_data[dat_file_greater_than_amp_cutoff_data[:,3] == roi,3] = roi_index
        roi_index = roi_index + 1

    n_rois_per_file = 50
    all_roi_indexes_list = range(1,int(np.amax(dat_file_greater_than_amp_cutoff_data[:,3]))+1)

    roi_index_groups = [all_roi_indexes_list[i*n_rois_per_file:(i + 1)*n_rois_per_file] for i in range((len(all_roi_indexes_list) + n_rois_per_file - 1) // n_rois_per_file)]
    for group in roi_index_groups:
        group_dat_file_data = np.empty([0,4])
        for roi_index in group: #get pixel ids, x and y coordinates, roi indexes and electrode indexes for given group of ROIs
            roi_index_dat_file_greater_than_amp_cutoff_data = dat_file_greater_than_amp_cutoff_data[dat_file_greater_than_amp_cutoff_data[:,3]==roi_index,:]
            group_dat_file_data = np.vstack([group_dat_file_data,roi_index_dat_file_greater_than_amp_cutoff_data])
        group_rois_dat_file = np.zeros((1+3*int(np.amax(group_dat_file_data[:,3]))+len(group_dat_file_data[group_dat_file_data[:,3] != 0]),1))
        group_rois_dat_file[0,0] = np.amax(group_dat_file_data[:,3])
        group_rois_dat_list = group
        start_row_index = 1
        for roi_index in group_rois_dat_list:
            roi_index = int(roi_index)
            roi_n_pixels = len(group_dat_file_data[group_dat_file_data[:,3]==roi_index])
            group_rois_dat_file[start_row_index,0] = roi_index-1
            group_rois_dat_file[start_row_index+2, 0] = roi_index-1
            group_rois_dat_file[start_row_index+1,0] = roi_n_pixels+1
            group_rois_dat_file[start_row_index+3:start_row_index+3+roi_n_pixels,0] = group_dat_file_data[group_dat_file_data[:,3]==roi_index,0]
            start_row_index = start_row_index+2+roi_n_pixels+1
        np.savetxt("ROIs_With_Amp_Greater_Than_Cutoff_"+str(min(group))+"_to_"+str(max(group))+".dat",group_rois_dat_file,fmt="%i")

############## Keep ROIS > Amp Cutoff and > SNR Cutoff #####################
############################################################################

roi_keep = np.zeros((width,height))
for i in range(0,width):
  for j in range(0,height):
    if roi_amp_averages[j][i] != 0:
      roi_keep[j][i] = roi_averages[j][i]

roi_keep_no_electrode = roi_keep
# roi_keep = numpy.multiply(roi_amp_keep,roi_averages)

plt.matshow(roi_keep)
plt.title("ROIs with SNR and Amplitude > Cutoff",fontsize=13)
# plt.show()
plt.savefig("ROIs_With_SNR_Amp_Greater_Than_Cutoff.jpg")

if Dat_snr_amp_cutoff == True:
    dat_file_greater_than_snr_amp_cutoff_data = np.zeros((width*height,4))
    dat_file_greater_than_snr_amp_cutoff_data[:,0] = range(height*width) #list of pixel IDs from 0 to width*height-1
    dat_file_greater_than_snr_amp_cutoff_data[:,1] = np.repeat(range(height),width) #y coordinates
    dat_file_greater_than_snr_amp_cutoff_data[:,2] = list(range(height))*width #y coordinates
    dat_file_greater_than_snr_amp_cutoff_data[:,3] = cluster_results.flatten() #final ROI clusters including electrode

    roi_index = 1
    final_roi_snr_vals = np.delete(np.unique(dat_file_greater_than_snr_amp_cutoff_data[:,3]),0)
    for roi in final_roi_snr_vals: #change ROI cluster values to be indexes not SNR values
        dat_file_greater_than_snr_amp_cutoff_data[dat_file_greater_than_snr_amp_cutoff_data[:,3] == roi,3] = roi_index
        roi_index = roi_index + 1

    n_rois_per_file = 50
    all_roi_indexes_list = range(1,int(np.amax(dat_file_greater_than_snr_amp_cutoff_data[:,3]))+1)

    roi_index_groups = [all_roi_indexes_list[i*n_rois_per_file:(i + 1)*n_rois_per_file] for i in range((len(all_roi_indexes_list) + n_rois_per_file - 1) // n_rois_per_file)]
    for group in roi_index_groups:
        group_dat_file_data = np.empty([0,4])
        for roi_index in group: #get pixel ids, x and y coordinates, roi indexes and electrode indexes for given group of ROIs
            roi_index_dat_file_greater_than_snr_amp_cutoff_data = dat_file_greater_than_snr_amp_cutoff_data[dat_file_greater_than_snr_amp_cutoff_data[:,3]==roi_index,:]
            group_dat_file_data = np.vstack([group_dat_file_data,roi_index_dat_file_greater_than_snr_amp_cutoff_data])
        group_rois_dat_file = np.zeros((1+3*int(np.amax(group_dat_file_data[:,3]))+len(group_dat_file_data[group_dat_file_data[:,3] != 0]),1))
        group_rois_dat_file[0,0] = np.amax(group_dat_file_data[:,3])
        group_rois_dat_list = group
        start_row_index = 1
        for roi_index in group_rois_dat_list:
            roi_index = int(roi_index)
            roi_n_pixels = len(group_dat_file_data[group_dat_file_data[:,3]==roi_index])
            group_rois_dat_file[start_row_index,0] = roi_index-1
            group_rois_dat_file[start_row_index+2, 0] = roi_index-1
            group_rois_dat_file[start_row_index+1,0] = roi_n_pixels+1
            group_rois_dat_file[start_row_index+3:start_row_index+3+roi_n_pixels,0] = group_dat_file_data[group_dat_file_data[:,3]==roi_index,0]
            start_row_index = start_row_index+2+roi_n_pixels+1
        np.savetxt("ROIs_With_SNR_And_Amp_Greater_Than_Cutoff_"+str(min(group))+"_to_"+str(max(group))+".dat",group_rois_dat_file,fmt="%i")

######################### Replot electrode #################################
############################################################################

for i in range(0,width): #add electrode as new "roi"
  for j in range(0,height):
    if electrode_data[j][i] != 0:
      roi_keep[j][i] = electrode_cluster

plt.matshow(roi_keep)
plt.title("Final ROIs with Electrode",fontsize=13)
# plt.show()
plt.savefig("Final ROIs.jpg")

########### Save pixel coordinates of final ROIs and electrode #############
############################################################################

dat_file_data = np.zeros((width*height,5))
dat_file_data[:,0] = range(height*width) #list of pixel IDs from 0 to width*height-1
dat_file_data[:,1] = np.repeat(range(height),width) #y coordinates
dat_file_data[:,2] = list(range(height))*width #y coordinates
dat_file_data[:,3] = roi_keep_no_electrode.flatten() #final ROI clusters including electrode
dat_file_data[:,4] = electrode_data.flatten() #pixels in electrode

dat_file_data[dat_file_data[:,3] == electrode_cluster,3] = 0 #remove electrode as cluster in column of final ROIs
dat_file_data[dat_file_data[:,4] == np.amax(electrode_data),4] = 1 #set pixel value to 1 if in electrode

roi_index = 1
final_roi_snr_vals = np.delete(np.unique(dat_file_data[:,3]),0)
for roi in final_roi_snr_vals: #change ROI cluster values to be indexes not SNR values
    dat_file_data[dat_file_data[:,3] == roi,3] = roi_index
    roi_index = roi_index + 1

electrode_pixel_ids = dat_file_data[dat_file_data[:,4] == 1,0] #list of pixel ids where pixel is in electrode
electrode_dat_file = np.zeros((4+len(electrode_pixel_ids),1))
electrode_dat_file[0,0] = 1 #only 1 "ROI" in this file (which is the electrode)
electrode_dat_file[1,0] = 0
electrode_dat_file[2,0] = len(electrode_pixel_ids) #number of pixels in electrode
electrode_dat_file[3,0] = 0
electrode_dat_file[4:len(electrode_pixel_ids)+4,0] = electrode_pixel_ids #pixel ides for pixels in electrode
np.savetxt("electrode.dat",electrode_dat_file,fmt="%i") #save dat file for electrode with values as integers

all_rois_dat_file = np.zeros((1+3*int(np.amax(dat_file_data[:,3]))+len(dat_file_data[dat_file_data[:,3] != 0]),1))
all_rois_dat_file[0,0] = np.amax(dat_file_data[:,3])
all_roi_indexes_list = range(1,int(np.amax(dat_file_data[:,3]))+1)
start_row_index = 1
for roi_index in all_roi_indexes_list:
    roi_index = int(roi_index)
    roi_n_pixels = len(dat_file_data[dat_file_data[:,3]==roi_index])
    all_rois_dat_file[start_row_index,0] = roi_index-1
    all_rois_dat_file[start_row_index+2, 0] = roi_index-1
    all_rois_dat_file[start_row_index+1,0] = roi_n_pixels+1
    all_rois_dat_file[start_row_index+3:start_row_index+3+roi_n_pixels,0] = dat_file_data[dat_file_data[:,3]==roi_index,0]
    start_row_index = start_row_index+2+roi_n_pixels+1
np.savetxt("ROIs_all.dat",all_rois_dat_file,fmt="%i")

roi_index_groups = [all_roi_indexes_list[i*5:(i + 1)*5] for i in range((len(all_roi_indexes_list) + 5 - 1) // 5)]
for group in roi_index_groups:
    group_dat_file_data = np.empty([0,5])
    for roi_index in group: #get pixel ids, x and y coordinates, roi indexes and electrode indexes for given group of ROIs
        roi_index_dat_file_data = dat_file_data[dat_file_data[:,3]==roi_index,:]
        group_dat_file_data = np.vstack([group_dat_file_data,roi_index_dat_file_data])
    group_rois_dat_file = np.zeros((1+3*int(np.amax(group_dat_file_data[:,3]))+len(group_dat_file_data[group_dat_file_data[:,3] != 0]),1))
    group_rois_dat_file[0,0] = np.amax(group_dat_file_data[:,3])
    group_rois_dat_list = group
    start_row_index = 1
    for roi_index in group_rois_dat_list:
        roi_index = int(roi_index)
        roi_n_pixels = len(group_dat_file_data[group_dat_file_data[:,3]==roi_index])
        group_rois_dat_file[start_row_index,0] = roi_index-1
        group_rois_dat_file[start_row_index+2, 0] = roi_index-1
        group_rois_dat_file[start_row_index+1,0] = roi_n_pixels+1
        group_rois_dat_file[start_row_index+3:start_row_index+3+roi_n_pixels,0] = group_dat_file_data[group_dat_file_data[:,3]==roi_index,0]
        start_row_index = start_row_index+2+roi_n_pixels+1
    np.savetxt("ROIs_"+str(min(group))+"_to_"+str(max(group))+".dat",group_rois_dat_file,fmt="%i")