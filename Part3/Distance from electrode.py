import pandas as pd
import math
import numpy

# print('test')

ROIs_dat = pd.read_csv('ROIs_1_to_93.dat',header=None)
# print(ROIs_dat.head())
angle_deg_clock = 359
angle_deg = 360-angle_deg_clock #formula below needs angle in counterclockwise, imageJ rotates clockwise

### Find tip of electrode ###
electrode_dat = pd.read_csv('Electrode1_to_1.dat',header=None)
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
# print(electrode_tip_xcoord,electrode_tip_ycoord)

### Find coords for each ROI ###
nROIs = ROIs_dat[0][0]
# nROIs = 42
# print(nROIs)

ROI_row_index_breaks = []
# print(range(0,nROIs))
for ROI_Id in range(0,nROIs): #counts from 0 to 1-nROIS
    ROI_Id_row_index_choices = ROIs_dat.index[ROIs_dat[0] == ROI_Id] + 1
    print(ROI_Id_row_index_choices)
    # print(ROIs_dat)
    choice_diff_list = numpy.diff(ROI_Id_row_index_choices)
    if 1 in choice_diff_list: #if any ROI has ROI_Id + 1 pixels (so three lines in a row have ROI_Id)
        val_index_list = []
        for val in range(0, len(choice_diff_list)):
            if choice_diff_list[val] != len(choice_diff_list) + 1 and choice_diff_list[val] == 1:
                val_index_list.append(val)
        n_index_diff = val_index_list[-1]
        # nth diff is between some row index and a second row index where that
        # first row index is the target row index
        ROI_Id_row_index = ROI_Id_row_index_choices[n_index_diff] + 1
        ROI_row_index_breaks.append(ROI_Id_row_index)
    else:
        for choice in range(len(ROI_Id_row_index_choices) - 1):
            # get second instance of ROI_Id which is one line before PixelIDs
            if ROI_Id_row_index_choices[choice + 1] - ROI_Id_row_index_choices[choice] == 2:
                ROI_Id_row_index = ROI_Id_row_index_choices[choice + 1]
        ROI_row_index_breaks.append(ROI_Id_row_index)
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
        pixel_xdistance = pixel_xcoord - electrode_tip_xcoord
        ROI_xdistance_list.append(pixel_xdistance)
        pixel_ycoord = pixelID_to_coords.iloc[pixel][:].loc[:]['YCoord']
        pixel_ydistance = pixel_ycoord - electrode_tip_ycoord
        ROI_ydistance_list.append(pixel_ydistance)
        pixel_euc_distance = math.sqrt(pixel_xdistance**2 + pixel_ydistance**2)
        ROI_euc_distance_list.append(pixel_euc_distance)
        # print(pixel_xcoord,pixel_ycoord)
        # print(pixel_xdistance,pixel_ydistance,pixel_euc_distance)
    # print(ROI_xdistance_list,ROI_ydistance_list)
    ROI_xdistance = sum(ROI_xdistance_list) / len(ROI_xdistance_list)
    ROI_ydistance = sum(ROI_ydistance_list) / len(ROI_ydistance_list)
    ROI_euc_distance = sum(ROI_euc_distance_list) / len(ROI_euc_distance_list)
    ROI_distances_list.append([ROI_Id+1,ROI_xdistance,ROI_ydistance,ROI_euc_distance])
ROI_distances = pd.DataFrame(ROI_distances_list,columns = ['ROI_Id','X_distance','Y_distance','Euc_distance'])
# print(ROI_distances)
ROI_distances.to_csv('ROI_distances.txt', index=False)

### Rotating so that layers are parallel with X-axis
### x2 = cos(angle)*x1 - sin(angle)*y1
### x2 = math.cos(angle_rad)*x1 - math.sin(angle_rad)*y1
### y2 = sin(angle)*x1 - cos(angle)*y1
#### y2 = math.sin(angle_rad)*x1 - math.cos(angle_rad)*y1
### ref: https://matthew-brett.github.io/teaching/rotation_2d.html
### this only works, though, assuming you rotate from the center of the object, so need to shift origin from
###     upper L corner (1,1) to middle of image (40.5,40.5)

angle_rad = math.radians(angle_deg) #converts angle in degrees to angle in radians
# print(angle_rad)

pixelID_to_coords_shifted = pixelID_to_coords
    # old origin is top L corner where y up as go down and x up as go right
    # want to get to origin at middle where y up as go up and x up as go right
    # first shift x to R (+40.5) and y down (-40.5) keeping directions so y up as go down and x up as go right
    # then flip over x axis (y * -1) so y up as go up and x up as go right
pixelID_to_coords_shifted.insert(len(pixelID_to_coords.columns),'XCoord_shifted',
                                 value=[x+40.5 for x in pixelID_to_coords.loc[:]['XCoord']])
pixelID_to_coords_shifted.insert(len(pixelID_to_coords.columns),'YCoord_shifted',
                                 value=[y-40.5 for y in pixelID_to_coords.loc[:]['YCoord']])
pixelID_to_coords_shifted.loc[:]['YCoord_shifted'] = pixelID_to_coords_shifted.loc[:]['YCoord_shifted']*-1
electrode_tip_x1coord = electrode_tip_xcoord+40.5
electrode_tip_y1coord = (electrode_tip_ycoord-40.5)*-1
# print(pixelID_to_coords_shifted)
# print(ROI_row_index_breaks)

ROI_shifted_distances_list = []
electrode_tip_x2coord = math.cos(angle_rad) * electrode_tip_x1coord - math.sin(angle_rad) * electrode_tip_y1coord
electrode_tip_y2coord = math.sin(angle_rad) * electrode_tip_x1coord + math.cos(angle_rad) * electrode_tip_y1coord
# print(electrode_tip_xcoord,electrode_tip_ycoord,
#       electrode_tip_x1coord,electrode_tip_y1coord,
#       electrode_tip_x2coord,electrode_tip_y2coord)
for ROI_Id in range(0,nROIs):
    if ROI_Id == nROIs-1: # if last ROI in list
        ROI_pixelIds = ROIs_dat[0][range(ROI_row_index_breaks[ROI_Id], len(ROIs_dat))]
        # print(ROI_pixelIds)
    else:
        ROI_pixelIds = ROIs_dat[0][range(ROI_row_index_breaks[ROI_Id],ROI_row_index_breaks[ROI_Id+1]-3)]
    # print(ROI_pixelIds)
    ROI_shifted_xdistance_list = []
    ROI_shifted_ydistance_list = []
    ROI_shifted_euc_distance_list = []
    for pixel in ROI_pixelIds:
        # print(pixel)
        # print(pixelID_to_coords_shifted.iloc[pixel][:])
        pixel_x1coord = pixelID_to_coords_shifted.iloc[pixel][:].loc[:]['XCoord_shifted']
        pixel_y1coord = pixelID_to_coords_shifted.iloc[pixel][:].loc[:]['YCoord_shifted']
        pixel_x2coord = math.cos(angle_rad)*pixel_x1coord - math.sin(angle_rad)*pixel_y1coord
        pixel_y2coord = math.sin(angle_rad)*pixel_x1coord + math.cos(angle_rad)*pixel_y1coord
        # print(pixel_x1coord,pixel_y1coord,pixel_x2coord,pixel_y2coord)
        pixel_x1distance = pixel_x1coord - electrode_tip_x1coord
        pixel_y1distance = pixel_y1coord - electrode_tip_y1coord
        pixel_x2distance = pixel_x2coord - electrode_tip_x2coord
        pixel_euc1_distance = math.sqrt(pixel_x1distance**2 + pixel_y1distance**2)
        # print(pixel_x1distance,pixel_y1distance,pixel_euc1_distance)
        ROI_shifted_xdistance_list.append(pixel_x2distance)
        pixel_y2distance = pixel_y2coord - electrode_tip_y2coord
        ROI_shifted_ydistance_list.append(pixel_y2distance)
        pixel_euc2_distance = math.sqrt(pixel_x2distance**2 + pixel_y2distance**2)
        print(pixel_x1distance,pixel_y1distance,pixel_euc1_distance,
              pixel_x2distance,pixel_y2distance,pixel_euc2_distance)
        # print(pixel_x2distance,pixel_y2distance,pixel_euc2_distance)
        ROI_shifted_euc_distance_list.append(pixel_euc2_distance)
    # print(ROI_shifted_xdistance_list,ROI_shifted_ydistance_list)
    ROI_shifted_xdistance = sum(ROI_shifted_xdistance_list) / len(ROI_shifted_xdistance_list)
    ROI_shifted_ydistance = sum(ROI_shifted_ydistance_list) / len(ROI_shifted_ydistance_list)
    ROI_shifted_euc_distance = sum(ROI_shifted_euc_distance_list) / len(ROI_shifted_euc_distance_list)
    ROI_shifted_distances_list.append([ROI_Id+1,ROI_shifted_xdistance,ROI_shifted_ydistance,ROI_shifted_euc_distance])
ROI_shifted_distances = pd.DataFrame(ROI_shifted_distances_list,columns = ['ROI_Id','X_shifted_distance',
                                                                   'Y_shifted_distance','Euc_shifted_distance'])
# print(ROI_shifted_distances)
ROI_shifted_distances.to_csv('ROI_shifted_distances.txt', index=False)



