import os
import pandas as pd

######################################## Create slice/ROI-level table ##################################################
########################################################################################################################
exclude = 'notUsable'

keep_fileList = []
keep_folderList =[]
keep_dirNameList = []
for dirName, subdirList, fileList in os.walk(".",topdown=False):
    # print(dirName)
    # print(subdirList)
    # print(fileList)
    for directory in dirName:
        keep_dirNameList.append(directory)
    for folder in subdirList:
        if 'notUsable' not in folder and 'Old' not in folder:
            print(folder)
            keep_folderList.append(folder)
    for file in fileList:
        if 'Not_Usable' not in file and '.txt' in file:
            keep_fileList.append(file)
    # keep_fileList = fileList
    # test = [x for x in fileList if 'Not_Usable' not in x]
    # # print("break")
    # test2 = [x for x in test if 'Not_Usable' not in x]
# print(keep_folderList)
# print(keep_fileList)

for folder in keep_folderList:
    current_fileList = []
    # print(current_fileList)
    for file in keep_fileList:
        if folder in file:
            current_fileList.append(file)
        #     print(file)
        #     print('break')
    # print(folder)
    # print(current_fileList)
    amp_file = [file for file in current_fileList if 'Amp_' in file]
    amp_name = folder + str(amp_file).replace("['", "\\")
    amp_name = amp_name.replace("']", "")
    peaktime_file = [file for file in current_fileList if 'PeakTime' in file]
    peaktime_name = folder + str(peaktime_file).replace("['", "\\")
    peaktime_name = peaktime_name.replace("']", "")
    snr_file = [file for file in current_fileList if 'SNR' in file]
    snr_name = folder + str(snr_file).replace("['", "\\")
    snr_name = snr_name.replace("']", "")
    latency_file = [file for file in current_fileList if 'Latency' in file]
    latency_name = folder + str(latency_file).replace("['", "\\")
    latency_name = latency_name.replace("']", "")
    halfwidth_file = [file for file in current_fileList if 'Halfwidth' in file]
    halfwidth_name = folder + str(halfwidth_file).replace("['", "\\")
    halfwidth_name = halfwidth_name.replace("']", "")
    distance_orig_file = [file for file in current_fileList if 'ROI_distances' in file]
    distance_orig_name = folder + str(distance_orig_file).replace("['", "\\")
    distance_orig_name = distance_orig_name.replace("']", "")
    distance_shift_file = [file for file in current_fileList if 'ROI_shifted_distances' in file]
    distance_shift_name = folder + str(distance_shift_file).replace("['", "\\")
    distance_shift_name = distance_shift_name.replace("']", "")
    layers_file = [file for file in current_fileList if 'Layers' in file]
    layers_name = folder + str(layers_file).replace("['", "\\")
    layers_name = layers_name.replace("']", "")
    visual_file = [file for file in current_fileList if 'Visual' in file]
    visual_name = folder + str(visual_file).replace("['", "\\")
    visual_name = visual_name.replace("']", "")
    metadata_file = [file for file in current_fileList if 'Metadata' in file]
    metadata_name = folder + str(metadata_file).replace("['", "\\")
    metadata_name = metadata_name.replace("']", "")

    # print(amp_name,snr_name,latency_name,halfwidth_name,distance_orig_name,distance_shift_name,layers_name,visual_name,metadata_name)

    amp = pd.read_csv(amp_name, sep='\t',names=["ROI_Id","Amp"])
    peaktime = pd.read_csv(peaktime_name, sep='\t',names=["ROI_Id","PeakTime"])
    snr = pd.read_csv(snr_name, sep='\t',names=["ROI_Id","SNR"])
    latency = pd.read_csv(latency_name, sep='\t',names=["ROI_Id","Latency"])
    halfwidth = pd.read_csv(halfwidth_name, sep='\t',names=["ROI_Id","Halfwidth"])
    distance_orig = pd.read_csv(distance_orig_name,names=['ROI_Id','X_distance','Y_distance','Euc_distance'])
    distance_orig = pd.read_csv(distance_orig_name,header=0)
    distance_shift = pd.read_csv(distance_shift_name,names=['ROI_Id','X_shifted_distance','Y_shifted_distance','Euc_shifted_distance'])
    distance_shift = pd.read_csv(distance_shift_name,header=0)
    layers = pd.read_csv(layers_name, sep='\t',names=["ROI_Id","Layers"])
    visual = pd.read_csv(visual_name, sep='\t',names=["ROI_Id","Visual"])
    metadata = pd.read_csv(metadata_name,sep='\t',names=['Variable','Value'])
    metadata = pd.DataFrame.transpose(metadata)
    metadata.columns = metadata.iloc[0]
    metadata = metadata.drop(metadata.index[0])
    data = {"Slice_Loc_Run":metadata.iloc[0,0],
            "Trial_x_Time":metadata.iloc[0,1],
            "Stim_Intensity":metadata.iloc[0,2],
            "Stim_Layer":metadata.iloc[0,3],
            "RLI":metadata.iloc[0,4],
            "Cx":metadata.iloc[0,5],
            "n_Pulses":metadata.iloc[0,6],
            "Pulse_index":metadata.iloc[0,7],
            "IPI":metadata.iloc[0,8],
            "ROI_Id":amp["ROI_Id"],
            "Visual":visual["Visual"],
            "Layers":layers["Layers"],
            "Amp":amp["Amp"],
            "PeakTime":peaktime["PeakTime"],
            "SNR":snr["SNR"],
            "Latency":latency["Latency"],
            "Halfwidth":halfwidth["Halfwidth"],
            "Dist_Orig_X":distance_orig['X_distance'],
            "Dist_Orig_Y":distance_orig['Y_distance'],
            "Dist_Orig_Euc":distance_orig['Euc_distance'],
            "Dist_Shift_X":distance_shift['X_shifted_distance'],
            "Dist_Shift_Y":distance_shift['Y_shifted_distance'],
            "Dist_Shift_Euc":distance_shift['Euc_shifted_distance'],
            }
    df = pd.DataFrame(data,columns=["Slice_Loc_Run","Trial_x_Time","Stim_Intensity","Stim_Layer",
                                    "RLI","Cx","n_Pulses","Pulse_index","IPI","ROI_Id",
                                    "Visual","Layers",
                                    "Amp","PeakTime","SNR","Latency","Halfwidth",'Dist_Orig_X',
                                    "Dist_Orig_Y","Dist_Orig_Euc","Dist_Shift_X","Dist_Shift_Y",
                                    "Dist_Shift_Euc"])

    if len(snr.count(axis='columns')) > 75:
        snr_largest = snr.nlargest(n=75,columns='SNR')
        snr_largest_id = snr_largest['ROI_Id']
        snr_largest_id = snr_largest_id-1
        snr_largest_id = snr_largest_id.sort_values(ascending=True)
        # print(snr_largest_id)
        # snr_largest_id = snr_largest_id.sort()
        # print(snr_largest_id)
        # print(type([snr_largest_id]-1))
        # print(amp.iloc[snr_largest_id,1])
        df = df.iloc[snr_largest_id,]
        # print(df)

    df.to_csv('Slice_Data_'+folder+'.csv',index=False)

#     print(df)
#     path = os.getcwd()+'\\'+folder
#     print(df)
#     print(path)
#     df.to_csv(path,"Slice_Data.csv",index=False)
# print(df)
# path = os.getcwd()+'\\'+folder

########################################## Create animal-level table ###################################################
########################################################################################################################

animal_list = []
for dirName, subdirList, fileList in os.walk(".",topdown=True):
    # print(fileList)
    for file in fileList:
        # print(file)
        if 'Slice_Data' in file:
            # print(file)
            # print(fileList)
            current_slice = pd.read_csv(file,names=["Slice_Loc_Run","Trial_x_Time","Stim_Intensity",
                                                    "Stim_Layer","RLI","Cx","n_Pulses","Pulse_index",
                                                    "IPI","ROI_Id",
                                                    "Visual","Layers",
                                                    "Amp","PeakTime","SNR",
                                                    "Latency","Halfwidth",'X_dist',"Y_dist","Euc_dist",
                                                    'X_shift_dist',"Y_shift_dist","Euc_shift_dist"])
            # print(current_slice)
            animal_list.append(current_slice)
# print(animal_list)
all_animals = pd.concat(animal_list)
all_animals = all_animals.drop_duplicates()
all_animals = all_animals.drop(all_animals.index[[0]])
animal_metadata = pd.read_csv('Metadata.txt', sep='\t', names=['Variable', 'Value'])
animal_metadata = pd.DataFrame.transpose(animal_metadata)
animal_metadata.columns = animal_metadata.iloc[0]
animal_metadata = animal_metadata.drop(animal_metadata.index[0])
# print(animal_metadata.iloc[0,0])
all_animals.insert(0,"Date",animal_metadata.iloc[0,0],True)
all_animals.insert(1,"Id",animal_metadata.iloc[0,1],True)
all_animals.insert(2,"Genotype",animal_metadata.iloc[0,2],True)
all_animals.insert(3,"Birthdate",animal_metadata.iloc[0,3],True)
all_animals.insert(4,"Sex",animal_metadata.iloc[0,4],True)
all_animals.insert(5,"Tx",animal_metadata.iloc[0,5],True)
all_animals.insert(6,"Tx_Start",animal_metadata.iloc[0,6],True)
# print(animal_metadata)
# print(all_animals)
all_animals.to_csv('Animal_Data.csv',index=False)