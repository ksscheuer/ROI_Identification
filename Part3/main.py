## test change


import os
import pandas as pd

######################################## Create slice/ROI-level table ##################################################
########################################################################################################################

for dirName, subdirList, fileList in os.walk("."):
    for fname in fileList:
        print(fname)
        if "Amp_" in fname:
            print(os.path.join(dirName, fname))




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
