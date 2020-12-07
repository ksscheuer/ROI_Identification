import pandas as pd
import math
import numpy

### Find tip of electrode ###
electrode_dat = pd.read_csv('electrode.dat',header=None)
electrode_dat = electrode_dat.dropna()
electrode_dat = electrode_dat.drop([0,1,2,3],axis=0)
    #drop first four rows bc not pixel IDs
    #note that photoZ pixelID of 1 (on traces) listed as 0 in .dat file
electrode_dat = electrode_dat.reset_index(drop=True)
pixelID_to_coords = {'PixelID_trace': list(range(1,6401)),
                     'PixelID_dat': list(range(0,6400)),
                     'XCoord': list(range(1,81))*80,
                     'YCoord': [val for val in list(range(1,81)) for i in range(80)]}
pixelID_to_coords = pd.DataFrame(pixelID_to_coords,columns = ['PixelID_trace',
                                                              'PixelID_dat',
                                                              'XCoord','YCoord'])
# print(pixelID_to_coords)
electrode_pixelID_to_coords = pixelID_to_coords.iloc[list(electrode_dat.iloc[:,0])]
max_xcoord = max(electrode_pixelID_to_coords['XCoord'])
electrode_pixelID_to_coords_max_xcoord = electrode_pixelID_to_coords.loc[electrode_pixelID_to_coords['XCoord'] == max_xcoord]['YCoord']
avg_ycoord = sum(electrode_pixelID_to_coords_max_xcoord)/len(electrode_pixelID_to_coords_max_xcoord)
electrode_tip_xcoord = max_xcoord
electrode_tip_ycoord = avg_ycoord


# for dirName, subdirList, fileList in os.walk(".",topdown=False):
#     # print(dirName)
#     # print(subdirList)
#     # print(fileList)
#     for directory in dirName:
#         keep_dirNameList.append(directory)
#     for folder in subdirList:
#         if 'notUsable' not in folder:
#             keep_folderList.append(folder)
#     for file in fileList:
#         if 'Not_Usable' not in file and '.txt' in file:
#             keep_fileList.append(file)


### Find coords for each ROI ###
ROIs_dat = pd.read_csv('ROIs01to16.dat',header=None)
nROIs = ROIs_dat[0][0]
# print(nROIs)

ROI_row_index_breaks = []
for ROI_Id in range(0,nROIs): #counts from 0 to 1-nROIS
    ROI_Id_row_index_choices = ROIs_dat.index[ROIs_dat[0] == ROI_Id] + 1
    if ROI_Id == 2:  # if second ROI and has 1 pixel then three lines in a row will be 2 so choose first and third line
        choice_diff_list = numpy.diff(ROI_Id_row_index_choices)
        # print(choice_diff_list)
        if 1 in choice_diff_list: #if ROI 2 has 3 pixels in it
            val_index_list = []
            for val in range(0, len(choice_diff_list)):
                # print(val,val!= len(choice_diff_list))
                if choice_diff_list[val] != len(choice_diff_list) + 1 and choice_diff_list[val] == 1:
                    val_index_list.append(val)
            n_index_diff = val_index_list[-1]
                # nth diff is between some row index and a second row index where that
                # first row index is the target row index
            ROI_Id_row_index = ROI_Id_row_index_choices[n_index_diff]+1
        else:
            for choice in range(len(ROI_Id_row_index_choices) - 1):
                # get second instance of ROI_Id which is one line before PixelIDs
                if ROI_Id_row_index_choices[choice + 1] - ROI_Id_row_index_choices[choice] == 2:
                    ROI_Id_row_index = ROI_Id_row_index_choices[choice + 1]
        # print(ROI_Id_row_index)
        ROI_row_index_breaks.append(ROI_Id_row_index)
    else:
        for choice in range(len(ROI_Id_row_index_choices) - 1):
            # get second instance of ROI_Id which is one line before PixelIDs
            if ROI_Id_row_index_choices[choice + 1] - ROI_Id_row_index_choices[choice] == 2:
                ROI_Id_row_index = ROI_Id_row_index_choices[choice + 1]
        ROI_row_index_breaks.append(ROI_Id_row_index)
print(ROI_row_index_breaks)

#         choice_diff_list = numpy.diff(ROI_Id_row_index_choices)
#         # print(choice_diff_list)
#         val_index_list = []
#         for val in range(0, len(choice_diff_list)):
#             # print(val,val!= len(choice_diff_list))
#             if choice_diff_list[val] != len(choice_diff_list) + 1 and choice_diff_list[val] == 1:
#                 val_index_list.append(val)
#         n_index_diff = val_index_list[-1]
#             # nth diff is between some row index and a second row index where that first row index is the target row index
#         ROI_Id_row_index = ROI_Id_row_index_choices[n_index_diff]+1
#         ROI_row_index_breaks.append(ROI_Id_row_index)
#     else:
#         for choice in range(len(ROI_Id_row_index_choices) - 1):
#             # get second instance of ROI_Id which is one line before PixelIDs
#             if ROI_Id_row_index_choices[choice + 1] - ROI_Id_row_index_choices[choice] == 2:
#                 ROI_Id_row_index = ROI_Id_row_index_choices[choice + 1]
#         ROI_row_index_breaks.append(ROI_Id_row_index)
# print(ROI_row_index_breaks)

# ROI_distances_list = []
# for ROI_Id in range(0,nROIs):
#     if ROI_Id == nROIs-1: # if last ROI in list
#         ROI_pixelIds = ROIs_dat[0][range(ROI_row_index_breaks[ROI_Id], len(ROIs_dat))]
#         # print(ROI_pixelIds)
#     else:
#         ROI_pixelIds = ROIs_dat[0][range(ROI_row_index_breaks[ROI_Id],ROI_row_index_breaks[ROI_Id+1]-3)]
#     # print(ROI_pixelIds)
#     ROI_xdistance_list = []
#     ROI_ydistance_list = []
#     ROI_euc_distance_list = []
#     for pixel in ROI_pixelIds:
#         # print(pixel)
#         pixel_xcoord = pixelID_to_coords.iloc[pixel][:].loc[:]['XCoord']
#         pixel_xdistance = abs(pixel_xcoord - electrode_tip_xcoord)
#         ROI_xdistance_list.append(pixel_xdistance)
#         pixel_ycoord = pixelID_to_coords.iloc[pixel][:].loc[:]['YCoord']
#         pixel_ydistance = abs(pixel_ycoord - electrode_tip_ycoord)
#         ROI_ydistance_list.append(pixel_ydistance)
#         pixel_euc_distance = math.sqrt(pixel_xdistance**2 + pixel_ydistance**2)
#         ROI_euc_distance_list.append(pixel_euc_distance)
#     ROI_xdistance = sum(ROI_xdistance_list) / len(ROI_xdistance_list)
#     ROI_ydistance = sum(ROI_ydistance_list) / len(ROI_ydistance_list)
#     ROI_euc_distance = sum(ROI_euc_distance_list) / len(ROI_euc_distance_list)
#     ROI_distances_list.append([ROI_Id+1,ROI_xdistance,ROI_ydistance,ROI_euc_distance])
# ROI_distances = pd.DataFrame(ROI_distances_list,columns = ['ROI_Id','X_distance','Y_distance','Euc_distance'])
# print(ROI_distances)
# # ROI_distances.to_csv('ROI_distances.csv', index=False)
