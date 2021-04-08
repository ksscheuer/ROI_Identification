############################## Import libraries, set variables by hand, load files #####################################

import matplotlib.pyplot as plt
import numpy as np
import sys
np.set_printoptions(suppress=True) #prevent np exponential notation on print
np.set_printoptions(threshold=np.inf) #print all values in numpy array

ROI_diameter_cutoff = 3 #2 if using 10x lens, 3 if using 20x
SNR_cutoff = 5
Amp_cutoff = 0.001
rlimit = 5000 #recursion limit (for identifying all potential ROIs)

pixel_cluster_data = np.loadtxt("Clusters_for_python.txt")
electrode_data = np.loadtxt("Electrode_for_python.txt")
electrode_coords = np.loadtxt("Electrode_coords.txt")
snr_data = np.loadtxt("SNR_for_python.txt")
amp_data = np.loadtxt("Amp_for_python.txt")
width = len(pixel_cluster_data)
height = len(pixel_cluster_data[0])
k = np.amax(pixel_cluster_data) #number of clusters

################################################ Define functions ######################################################

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

def produce_dat_files(width,height,trace_data,n_rois_per_file,dat_file_name):
    dat_file_data = np.zeros((width * height, 4))
    dat_file_data[:, 0] = range(height * width)  # list of pixel IDs from 0 to width*height-1
    dat_file_data[:, 1] = np.repeat(range(height), width)  # x coordinates
    dat_file_data[:, 2] = list(range(height)) * width  # y coordinates
    dat_file_data[:, 3] = trace_data.flatten()  #data to be flattened from height x width df to column

    roi_index = 1
    final_roi_snr_vals = np.delete(np.unique(dat_file_data[:, 3]), 0)
    for roi in final_roi_snr_vals:  # change ROI cluster values to be indexes not SNR values
        dat_file_data[dat_file_data[:, 3] == roi, 3] = roi_index
        roi_index = roi_index + 1

    # n_rois_per_file = 50
    all_roi_indexes_list = range(1, int(np.amax(dat_file_data[:, 3])) + 1)

    roi_index_groups = [all_roi_indexes_list[i * n_rois_per_file:(i + 1) * n_rois_per_file] for i in
                        range((len(all_roi_indexes_list) + n_rois_per_file - 1) // n_rois_per_file)]
    for group in roi_index_groups:
        group_dat_file_data = np.empty([0, 4])
        for roi_index in group:  # get pixel ids, x and y coordinates, roi indexes and electrode indexes for given group of ROIs
            roi_index_dat_file_data = dat_file_data[dat_file_data[:, 3] == roi_index, :]
            group_dat_file_data = np.vstack([group_dat_file_data, roi_index_dat_file_data])
        group_rois_dat_file = np.zeros((2 + 3 * int(np.amax(group_dat_file_data[:, 3])) + len(
            group_dat_file_data[group_dat_file_data[:, 3] != 0]), 1))
        group_rois_dat_file[0, 0] = np.amax(group_dat_file_data[:, 3])
        group_rois_dat_list = group
        start_row_index = 1
        for roi_index in group_rois_dat_list:
            roi_index = int(roi_index)
            roi_n_pixels = len(group_dat_file_data[group_dat_file_data[:, 3] == roi_index])
            group_rois_dat_file[start_row_index, 0] = roi_index - 1
            group_rois_dat_file[start_row_index + 2, 0] = roi_index - 1
            group_rois_dat_file[start_row_index + 1, 0] = roi_n_pixels + 1
            group_rois_dat_file[start_row_index + 3:start_row_index + 3 + roi_n_pixels, 0] = group_dat_file_data[
                group_dat_file_data[:, 3] == roi_index, 0]
            start_row_index = start_row_index + 2 + roi_n_pixels + 1
        np.savetxt(dat_file_name + str(min(group)) + "_to_" + str(max(group)) + ".dat", group_rois_dat_file,
                   fmt="%i")

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
      # check_collisions(xleft,yup,cell_value)
      check_collisions(xleft,y,cell_value)
      # check_collisions(xleft,ydown,cell_value)
      check_collisions(x,ydown,cell_value)
      # check_collisions(xright,ydown,cell_value)
      check_collisions(xright,y,cell_value)
      # check_collisions(xright,yup,cell_value)
    else:
      # print ("Found collision",group_index,cell_value)
      cluster_results[cluster_results == group_index] = 0
      cluster_results[cluster_results == cell_value] = 0

def amp_above_cutoff(width,height,amp_data,cluster_results):
    roi_amp_averages = np.zeros((width,height))
    for roi_group_index in np.delete(np.unique(cluster_results), 0):
      location_index = (cluster_results == roi_group_index)
      amp_data_for_group = amp_data * location_index
      average = amp_data_for_group[amp_data_for_group != 0].mean()
      # if average > Amp_cutoff:
      #   print (average)
      # else:
      #   print ("Below Amp threshold.")
      roi_amp_averages += (cluster_results == roi_group_index) * average

    # unique, counts = np.unique(roi_amp_averages, return_counts=True)
    # amp_dict= dict(zip(unique, counts)) #make dictionary of snr/count pairs
    # background_amp = max(amp_dict, key=amp_dict.get) #find snr that occurs most often ie background
    # roi_amp_averages[roi_amp_averages == background_amp] = 0 #set background to 0

    roi_amp_averages[roi_amp_averages < Amp_cutoff] = 0

    cluster_results = roi_amp_averages

    plot_cluster_results = np.ndarray.copy(cluster_results)
    plot_cluster_results[plot_cluster_results == 0] = np.nan

    plt.matshow(plot_cluster_results)
    plt.title("ROIs with Amplitude > Cutoff",fontsize=13)
    # plt.show()
    plt.savefig("ROIs_With_Amp_Greater_Than_Cutoff.jpg")
    return cluster_results

def snr_above_cutoff(width,height,snr_data,cluster_results):

    # print(cluster_results)
    roi_averages = np.zeros((width,height))

    for roi_group_index in np.delete(np.unique(cluster_results), 0):
        location_index = (cluster_results == roi_group_index) #find pixels that are part of given group
        snr_data_for_group = snr_data * location_index #keep only SNR values that are part of given group
        average = snr_data_for_group[snr_data_for_group != 0].mean() #average SNR values for given group
      # if average > SNR_cutoff:
      #   print (average)
      # else:
      #   print ("Below SNR threshold.")
        roi_averages += (cluster_results == roi_group_index) * average

    # print(roi_averages)

    # unique, counts = np.unique(roi_averages, return_counts=True)
    # snr_dict= dict(zip(unique, counts)) #make dictionary of snr/count pairs
    # background_snr = max(snr_dict, key=snr_dict.get) #find snr that occurs most often ie background
    # roi_averages[roi_averages == background_snr] = 0 #set background to 0
    #
    roi_averages[roi_averages < SNR_cutoff] = 0

    cluster_results = roi_averages

    plot_cluster_results = np.ndarray.copy(cluster_results)
    plot_cluster_results[plot_cluster_results == 0] = np.nan

    # gradient = np.linspace(0, 1, 256)
    # gradient = np.vstack((gradient, gradient))
    # plt.axes().set(facecolor="orange")
    plt.matshow(plot_cluster_results,vmin=0,vmax=2)
    # print(cluster_results)
    # plt.matshow(cluster_results)
    plt.title("ROIs with SNR > Cutoff",fontsize=13)
    # plt.show()
    plt.savefig("ROIs_With_SNR_Greater_Than_Cutoff.jpg")
    return cluster_results

############################## Identify each potential ROI and bounds for each ROI #####################################

cluster_results = np.zeros((width, height))
sys.setrecursionlimit(rlimit + 1)
group_index = 1  # 0 = never visited, 1 = first roi, 2 = second roi, etc
group_bound = []

for i in range(0, width):
    for j in range(0, height):
        result = check_cell(i, j, group_index, 0, 0)
        # print ("RETURN!", group_index)
        if result is not None:
            group_index += 1
            group_bound.append(result)

plot_cluster_results = np.ndarray.copy(cluster_results)
plot_cluster_results[plot_cluster_results==0] = np.nan

plt.matshow(plot_cluster_results)
plt.title("All Potential ROIs, Clusters: %d" % (k), fontsize=13)
plt.set_cmap("hsv")
# plt.show()
plt.savefig("All_Potential_ROIs.jpg")

# produce_dat_files(width=width,height=height,trace_data=cluster_results,n_rois_per_file=50,dat_file_name="All_Potential_ROIs_")

####################################### Remove ROIs with diameter > cutoff #############################################

bound_limit = ROI_diameter_cutoff

for i in range(0,len(group_bound)):
  group = group_bound[i]
  # print(group)
  x_big = (group[1] - group[0]) > (bound_limit-1)
  y_big = (group[3] - group[2]) > (bound_limit-1)
  if x_big or y_big:
    cluster_results[cluster_results == (i+1)] = 0 #0 vs 1 index mismatch ie counting from 0 here but index from 1 above

plot_cluster_results = np.ndarray.copy(cluster_results)
plot_cluster_results[plot_cluster_results==0] = np.nan

plt.matshow(plot_cluster_results)
plt.title("ROIs with Diameter < %d" % (ROI_diameter_cutoff),fontsize=13)
plt.set_cmap("hsv")
# plt.show()
plt.savefig("ROIS_Diameter_Within_Cutoff.jpg")

# produce_dat_files(width=width,height=height,trace_data=cluster_results,n_rois_per_file=50,dat_file_name="ROIs_Diameter_Within_Cutoff_")

########################################### Keep ROIs with SNR > cutoff ################################################

cluster_results = snr_above_cutoff(width=width,height=height,snr_data=snr_data,cluster_results=cluster_results)
# produce_dat_files(width=width,height=height,trace_data=cluster_results,n_rois_per_file=50,dat_file_name="ROIs_With_SNR_Greater_Than_Cutoff_")


########################################### Keep ROIs with Amp > cutoff ################################################

cluster_results = amp_above_cutoff(width=width,height=height,amp_data=amp_data,cluster_results=cluster_results)
# produce_dat_files(width=width,height=height,trace_data=cluster_results,n_rois_per_file=50,dat_file_name="ROIs_With_Amp_Greater_Than_Cutoff_")


############################################### Add electrode ##########################################################

electrode_data = electrode_data * (max(np.unique(cluster_results))+1) #0 if not in electrode, 1+max group number if in cluster
electrode_cluster = max(np.unique(pixel_cluster_data))+1
pixel_cluster_data_with_electrode = pixel_cluster_data

for i in range(0,width): #add electrode as new "roi"
  for j in range(0,height):
    if electrode_data[j][i] != 0:
      cluster_results[j][i] = electrode_data[j][i]
      pixel_cluster_data_with_electrode[j][i] = electrode_cluster

########################################## Remove ROIs touching electrode ##############################################

electrode_x_min = electrode_coords[0]-1
electrode_x_max = electrode_coords[3]-1
electrode_y_max = electrode_coords[2]-1
electrode_y_min = electrode_coords[1]-1

rois_touching_electrode = []
for i in range(0,height):
  for j in range(0,width):
    cell_value = cluster_results[j][i]
    if cell_value!=0 and i>(electrode_x_min-2) and i<(electrode_x_max+2) and j>(electrode_y_min-2) and j<(electrode_y_max+2):
      rois_touching_electrode.append(cell_value)

rois_touching_electrode = np.unique(rois_touching_electrode)

for i in range(0,width):
  for j in range(0,height):
    cell_value = cluster_results[j][i]
    if cell_value in rois_touching_electrode:
      cluster_results[j][i] = 0


######################################### Remove ROIs touching each other ##############################################

visited_cells = np.zeros((width,height))

for i in range(0,width):
  for j in range(0,height):
    result = check_collisions(i,j,0)

plot_cluster_results = np.ndarray.copy(cluster_results)
plot_cluster_results[plot_cluster_results==0] = np.nan

plt.matshow(plot_cluster_results)
plt.title("ROIs not Touching",fontsize=13)
plt.set_cmap("hsv")
# plt.show()
plt.savefig("ROIs_Not_Touching.jpg")

# produce_dat_files(width=width,height=height,trace_data=cluster_results,n_rois_per_file=50,dat_file_name="ROIs_Not_Touching_")

############################################ Plot final ROIs and electrode #############################################

produce_dat_files(width=width,height=height,trace_data=cluster_results,n_rois_per_file=50,dat_file_name="ROIs_")
produce_dat_files(width=width,height=height,trace_data=cluster_results,n_rois_per_file=300,dat_file_name="ROIs_")
produce_dat_files(width=width,height=height,trace_data=cluster_results,n_rois_per_file=5,dat_file_name="ROIs_")
produce_dat_files(width=width,height=height,trace_data=electrode_data,n_rois_per_file=1,dat_file_name="Electrode")

for i in range(0,width): #add electrode as new "roi"
  for j in range(0,height):
    if electrode_data[j][i] != 0:
      cluster_results[j][i] = electrode_cluster

plot_cluster_results = np.ndarray.copy(cluster_results)
plot_cluster_results[plot_cluster_results==0] = np.nan

plt.matshow(plot_cluster_results)
plt.title("Final ROIs with Electrode",fontsize=13)
# plt.show()
plt.savefig("Final ROIs.jpg")