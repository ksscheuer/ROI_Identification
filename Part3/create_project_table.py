import os
import pandas as pd

########################################################################################################################
########################################### Create study-level table ###################################################

animal_list = []
for dirName, subdirList, fileList in os.walk(".",topdown=True):
    for file in fileList:
        if 'Animal_Data' in file:
            # print(file)
            current_animal = pd.read_csv(file,names=["Date","Id","Genotype","Birthdate","Sex","Tx","Tx_Start",
                                                     "Slice_Loc_Run","Trial_x_Time","Stim_Intensity","Stim_Layer",
                                                     "RLI","Cx","n_Pulses","Pulse_index","IPI","ROI_Id","Visual",
                                                     "Layers","Amp","SNR","Latency","Halfwidth"])
            # print(current_animal)
            animal_list.append(current_animal)
all_animals = pd.concat(animal_list)
all_animals = all_animals.drop_duplicates()
all_animals = all_animals.drop(all_animals.index[[0]])
all_animals.to_csv('Project_Data.csv', index=False)


