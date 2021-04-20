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
            keep_folderList.append(folder)
    for file in fileList:
        if 'Not_Usable' not in file and '.txt' in file:
            keep_fileList.append(file)
    # keep_fileList = fileList
    # test = [x for x in fileList if 'Not_Usable' not in x]
    # # print("break")
    # test2 = [x for x in test if 'Not_Usable' not in x]
print(keep_folderList)
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
    amp_file = [file for file in current_fileList if 'Amp' in file]
    amp_name = folder + str(amp_file).replace("['", "\\")
    amp_name = amp_name.replace("']", "")
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

    print(amp_name,snr_name,latency_name,halfwidth_name,distance_orig_name,distance_shift_name,layers_name,metadata_name)

    amp = pd.read_csv(amp_name, sep='\t',names=["ROI_Id","Amp"])
    snr = pd.read_csv(snr_name, sep='\t',names=["ROI_Id","SNR"])
    latency = pd.read_csv(latency_name, sep='\t',names=["ROI_Id","Latency"])
    halfwidth = pd.read_csv(halfwidth_name, sep='\t',names=["ROI_Id","Halfwidth"])
    # distance_orig = pd.read_csv(distance_orig_name,names=['ROI_Id','X_distance','Y_distance','Euc_distance'])
    distance_orig = pd.read_csv(distance_orig_name,header=0)
    # distance_shift = pd.read_csv(distance_shift_name,names=['ROI_Id','X_shifted_distance','Y_shifted_distance','Euc_shifted_distance'])
    distance_shift = pd.read_csv(distance_shift_name,header=0)
#     layers = pd.read_csv(layers_name, sep='\t',names=["ROI_Id","Layers"])
#     visual = pd.read_csv(visual_name, sep='\t',names=["ROI_Id","Visual"])
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
            # "Visual":visual["Visual"],
            # "Layers":layers["Layers"],
            "Amp":amp["Amp"],
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
                                    # "Visual","Layers",
                                    "Amp","SNR","Latency","Halfwidth",'Dist_Orig_X',
                                    "Dist_Orig_Y","Dist_Orig_Euc","Dist_Shift_X","Dist_Shift_Y",
                                    "Dist_Shift_Euc"])

    # if len(snr.count(axis='columns')) > 75:
    #     snr_largest = snr.nlargest(n=75,columns='SNR')
    #     snr_largest_id = snr_largest['ROI_Id']
    #     snr_largest_id = snr_largest_id-1
    #     snr_largest_id = snr_largest_id.sort_values(ascending=True)
    #     # print(snr_largest_id)
    #     # snr_largest_id = snr_largest_id.sort()
    #     # print(snr_largest_id)
    #     # print(type([snr_largest_id]-1))
    #     # print(amp.iloc[snr_largest_id,1])
    #     df = df.iloc[snr_largest_id,]
    #     # print(df)

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
    for file in fileList:
        print(file)
        if 'Slice_Data' in file:
            # print(file)
            current_slice = pd.read_csv(file,names=["Slice_Loc_Run","Trial_x_Time","Stim_Intensity",
                                                    "Stim_Layer","RLI","Cx","n_Pulses","Pulse_index",
                                                    "IPI","ROI_Id",
                                                    # "Visual","Layers",
                                                    "Amp","SNR",
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














# for item in keep_fileList:
    #     if 'Not_Usable' in item:

    # file_keep = []
    # if 'Not_Usable' not in subdirList:
    #     print(subdirList)
    # for file in fileList:
    #     if 'Not_Usable' not in file:
    #         file_keep.append(file)
    #         # print(file)
    # print(file_keep)
    # for thing in file_keep:
    #     print(*thing)
    # test = flatten(file_keep)

    # print(type(subdirList[0]))

    # print(fileList)
    # print(file_keep)
    # folder_keep = []
    # for folder in subdirList:
        # print(file_keep)
        # print(len(folder))
        # if 'notUsable' not in folder:
        # if 'notUsable' not in folder and len(folder) < 18:
        #     print(len(folder))
        #     print(folder)
        #     current_folder = folder
        #     print(file_keep)
        #     for usable_file in file_keep:
        #         if current_folder in usable_file and '.txt' in usable_file:
        #             print(usable_file)
        #     if folder in fileList:
        #         print(folder)
            # print(folder in fileList)
            # print(fileList)
            # for file in fileList:
            #     print(file)
            # folder_keep.append(folder)

    # print(folder_keep)
    # for usable_file in file_keep:
    #     if '01-01-06' in usable_file and '.txt' in usable_file:
            # print(usable_file)
    # print(len(folder_keep))
    # for folder_row in folder_keep:
    #     print(len(folder_row))
    # for folder_name in dirName:
    #     if "notUsable" not in folder_name:
    #         print(folder_name)
    # print(subdirList)
    # print(fileList)
    # test = [d for d in subdirList if d in exclude]
    # subdirList[:] = [d for d in subdirList if d not in exclude]
    # print(subdirList[0])
    # print(dirName)
    # filtered = [str for str in dirName if exclude not in str]
    # for folder in fileList:
    #     print(folder)
    # filtered = [str for str in subdirList if "notUsable" not in str]
    # for folder in filtered:
    #     folder_name = filtered[folder]
        # print(folder_name)
# print(join(os.getcwd(),subdirList))
#     for file in fileList:
#         if ".txt" in file and "Not_Usable" not in file and "Metadata" not in file:
            # print(os.path.abspath(file))
            # file_names = os.path.join(dirName,file)
            # print(file_names)
    # filtered = [str for str in os.path.join(dirName,subdirList) if "notUsable" not in str]
    # filtered = [str for str in filtered if not str.isalpha()]
    # filtered = [str for str in subdirList if not any(i in str for i in exclude)]
    # print(filtered)
    # folder_keep = []
    # for folder in filtered:
    # print(folder_keep)
    # print(filtered)
    # print(type(filtered))
    # keep = [filtered[0]]
    # print(keep)
    # for folder in filtered:
    #     if "notUsable" not in folder:
    #         full_folder_name = os.getcwd()+'\\'+folder+'.txt'
    #         # print(os.getcwd())
    #         # print(folder)
    #         print(full_folder_name)
    # print(subdirList)
    # for fname in fileList:
    #     fullpath = os.path.join(dirName,fname)
    #     # if fname != "Not_Usable.txt" and ".txt" in fname:
        #     print(fname)
        # with open(fullpath,'r') as f:
        #     data =
        # print(fname)
        # if "Amp_" in fname:
        #     print(os.path.join(dirName, fname))

# amp = pd.read_csv('01-01-06\Amp_01-01-06_ROIs01to20.txt', sep='\t',names=["ROI_Id","Amp"])
# print(amp)

# amp = pd.read_csv('Amp_01-01-06_ROIs01to20.txt', sep='\t',names=["ROI_Id","Amp"])
# snr = pd.read_csv('SNR_01-01-06_ROIs01to20.txt', sep='\t',names=["ROI_Id","SNR"])
# layers = pd.read_csv('Layers_01-01-06_ROIs01to20.txt', sep='\t',names=["ROI_Id","Layers"])
# visual = pd.read_csv('Visual_01-01-06_ROIs01to20.txt', sep='\t',names=["ROI_Id","Visual"])
# metadata = pd.read_csv('Metadata.txt',sep='\t',names=['Variable','Value'])
# ## remove extra tabs for stim_layer, rli, cx, ipi AND add Slice_Loc_Run  01_01_06
# ## add Pulse_index       Stim1 after nPulses, separate stim1 and 2 into two diff folders
# metadata = pd.DataFrame.transpose(metadata)
# metadata.columns = metadata.iloc[0]
# metadata = metadata.drop(metadata.index[0])
# data = {"Slice_Loc_Run":metadata.iloc[0,0],
#         "Trial_x_Time":metadata.iloc[0,1],
#         "Stim_Intensity":metadata.iloc[0,2],
#         "Stim_Layer":metadata.iloc[0,3],
#         "RLI":metadata.iloc[0,4],
#         "Cx":metadata.iloc[0,5],
#         "n_Pulses":metadata.iloc[0,6],
#         "IPI":metadata.iloc[0,7],
#         "ROI_Id":amp["ROI_Id"],
#         "Visual":visual["Visual"],
#         "Layers":layers["Layers"],
#         "Amp":amp["Amp"],
#         "SNR":snr["SNR"]}
# df = pd.DataFrame(data,columns=["Slice_Loc_Run","Trial_x_Time","Stim_Intensity","Stim_Layer",
#                                 "RLI","Cx","n_Pulses","IPI","ROI_Id","Visual","Layers","Amp","SNR"])
# df.to_csv("Slice_Data.csv",index=False)

# import os
# for dirName, subdirList, fileList in os.walk("."):
#     for fname in fileList:
#         if fname != "Not_Usable.txt" and ".txt" in fname:
#             print(os.path.join(dirName, fname))
        # print("Found file with filename {}".format(fname))

# for dirName, subdirList, fileList in os.walk("."):
#     for fname in fileList:
#         print("Found file with filename {}".format(fname))

# import numpy as np

# with open('G:\\My Drive\\Jackson\\PhotoZ_data\\Step2_ROI_Values\\2020-09-11_BC_FXR1\\01-01-06\\Amp_01-01-06_ROIs01to20_test.csv','r') as file:
#     test = file.read()
# print(test)
# print(type(test))
# test2 = np.array(test)
# print(test2)

# test = open('G:\\My Drive\\Jackson\\PhotoZ_data\\Step2_ROI_Values\\2020-09-11_BC_FXR1\\01-01-06\\Amp_01-01-06_ROIs01to20_test.txt',"r")
# test.read()
# with open('G:\\My Drive\\Jackson\\PhotoZ_data\\Step2_ROI_Values\\2020-09-11_BC_FXR1\\01-01-06\\Amp_01-01-06_ROIs01to20.txt',"r") as f:
#     test = [x.strip().split('\t') for x in f]
#     print(test)
# print(type(test))
# test2 = np.array(test)
# print(test2)

# amp = np.genfromtxt('G:\\My Drive\\Jackson\\PhotoZ_data\\Step2_ROI_Values\\2020-09-11_BC_FXR1\\01-01-06\\Amp_01-01-06_ROIs01to20.txt', delimiter='\t',dtype=None,encoding=None)
# snr = np.genfromtxt('G:\\My Drive\\Jackson\\PhotoZ_data\\Step2_ROI_Values\\2020-09-11_BC_FXR1\\01-01-06\\SNR_01-01-06_ROIs01to20.txt', delimiter='\t', dtype=None)
# layers = np.genfromtxt('G:\\My Drive\\Jackson\\PhotoZ_data\\Step2_ROI_Values\\2020-09-11_BC_FXR1\\01-01-06\\Layers_01-01-06_ROIs01to20.txt', delimiter='\t', dtype=None)
# visual = np.genfromtxt('G:\\My Drive\\Jackson\\PhotoZ_data\\Step2_ROI_Values\\2020-09-11_BC_FXR1\\01-01-06\\Visual_01-01-06_ROIs01to20.txt', delimiter='\t', dtype=None)
# amp = pd.read_csv('G:\\My Drive\\Jackson\\PhotoZ_data\\Step2_ROI_Values\\2020-09-11_BC_FXR1\\01-01-06\\Amp_01-01-06_ROIs01to20.txt', sep='\t',names=["ROI_Id","Amp"])

# print(snr[:,1])
# print(layers[:,1])
# print(visual[:,1])
# np.savetxt("test2.csv",data,delimiter=",",fmt="%i,%f")

# test = open("./Amp_01-01-06_ROIs01to20.txt","r")
# print(test)

# import os
# for dirName, subdirList, fileList in os.walk("."):
#     for fname in fileList:
#         print(fname)
#         if "Amp_" in fname:
#             print(fname)
#             # amp = open(fname,"r")
