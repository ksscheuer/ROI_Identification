import pandas as pd
import math

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

### Find coords for each ROI ###
ROIs_dat = pd.read_csv('ROIs01to10.dat',header=None)
nROIs = ROIs_dat[0][0]
# print(nROIs)

ROI_row_index_breaks = []
for ROI_Id in range(0,nROIs): #counts from 0 to 1-nROIS
    # print(ROI_Id)
    # ROI_Id_row_index = ROIs_dat.index[ROIs_dat[0]==ROI_Id]
    # ROI_Id_row_index = ROIs_dat.index[ROIs_dat[0]==ROI_Id][1]+1
    ROI_Id_row_index_choices = ROIs_dat.index[ROIs_dat[0] == ROI_Id] + 1
    for choice in range(len(ROI_Id_row_index_choices) - 1):
        #get second instance of ROI_Id which is one line before PixelIDs
        if ROI_Id_row_index_choices[choice + 1] - ROI_Id_row_index_choices[choice] == 2:
            ROI_Id_row_index = ROI_Id_row_index_choices[choice + 1]
    ROI_row_index_breaks.append(ROI_Id_row_index)
    # print(ROI_Id_row_index)
# print(ROI_row_index_breaks)

ROI_distances_list = []
for ROI_Id in range(0,nROIs):
    if ROI_Id == nROIs-1: # if last ROI in list
        ROI_pixelIds = ROIs_dat[0][range(ROI_row_index_breaks[ROI_Id], len(ROIs_dat))]
        # print(ROI_pixelIds)
    else:
        ROI_pixelIds = ROIs_dat[0][range(ROI_row_index_breaks[ROI_Id],ROI_row_index_breaks[ROI_Id+1]-3)]
    # print(ROI_pixelIds)
    ROI_xdistance_list = []
    ROI_ydistance_list = []
    ROI_euc_distance_list = []
    for pixel in ROI_pixelIds:
        # print(pixel)
        pixel_xcoord = pixelID_to_coords.iloc[pixel][:].loc[:]['XCoord']
        pixel_xdistance = abs(pixel_xcoord - electrode_tip_xcoord)
        ROI_xdistance_list.append(pixel_xdistance)
        pixel_ycoord = pixelID_to_coords.iloc[pixel][:].loc[:]['YCoord']
        pixel_ydistance = abs(pixel_ycoord - electrode_tip_ycoord)
        ROI_ydistance_list.append(pixel_ydistance)
        pixel_euc_distance = math.sqrt(pixel_xdistance**2 + pixel_ydistance**2)
        ROI_euc_distance_list.append(pixel_euc_distance)
    ROI_xdistance = sum(ROI_xdistance_list) / len(ROI_xdistance_list)
    ROI_ydistance = sum(ROI_ydistance_list) / len(ROI_ydistance_list)
    ROI_euc_distance = sum(ROI_euc_distance_list) / len(ROI_euc_distance_list)
    ROI_distances_list.append([ROI_Id,ROI_xdistance,ROI_ydistance,ROI_euc_distance])
ROI_distances = pd.DataFrame(ROI_distances_list,columns = ['ROI_Id','X_distance','Y_distance','Euc_distance'])
ROI_distances.to_csv('ROI_distances.csv', index=False)
