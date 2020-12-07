########################################################################################################################
###################################### Load libraries and read in data #################################################

import pandas as pd

snr_cutoff = 4
amp_cutoff = 0.001

full_df = pd.read_csv("FXR1_Data.csv",header=0)
# print(full_df)

########################################################################################################################
############################################### Exclude rows ###########################################################

### Stim1 and SNR < cutoff or
### Stim1 and amp < cutoff or
### Layers = edge or
### Stim1 and visual == 0
remove_index_list = []
for i in range(len(full_df)):
    if 'Stim1' in full_df.iloc[1].loc["Pulse_index"] and full_df.iloc[1].loc["SNR"] < snr_cutoff:
        remove_index_list.append(i)
    elif 'Stim1' in full_df.iloc[1].loc["Pulse_index"] and full_df.iloc[1].loc["Amp"] < amp_cutoff:
        remove_index_list.append(i)
    elif 'Edge' in full_df.iloc[i,18]:
        remove_index_list.append(i)
    elif 'Stim1' in full_df.iloc[1].loc["Pulse_index"] and full_df.iloc[1].loc["Visual"] == 0:
        remove_index_list.append(i)
# print(len(remove_index_list))
trimmed_df = full_df.drop(remove_index_list)

########################################################################################################################
#######################################  Add intra/interlaminar column #################################################

trimmed_df.insert(17,'Laminar',value='')
# print(trimmed_df)
laminar_col_index = trimmed_df.columns.get_loc('Laminar')
for i in range(len(trimmed_df)):
    stim_layer = trimmed_df.iloc[i].loc['Stim_Layer']
    roi_layer = trimmed_df.iloc[i].loc['Layers']
    if stim_layer == roi_layer:
        trimmed_df.iloc[i,laminar_col_index] = 'Intra'
    else:
        trimmed_df.iloc[i,laminar_col_index] = 'Inter'

########################################################################################################################
################################################  Fix Latencies ########################################################

### assuming all 2019 is NP and all 2020 is photoZ --> this is a bad assumption
# if '2020' in trimmed_df['Date']:
    # trimmed_df['Latency'] = trimmed_df['Latency'] - ((96+7)/2) #photoZ, + 7 bc throws away first 7 pts?
    # trimmed_df['Latency'] = trimmed_df['Latency'] - (13/2) #photoZ, stim is 13 frame after stim in NP
# else:
#     trimmed_df['Latency'] = trimmed_df['Latency'] - ((83+7)/2) #NP,  + 7 bc throws away first 7 pts?
# print(trimmed_df)
# trimmed_df.to_csv('Trimmed_Data.csv',index=False)
# print(trimmed_df)

########################################################################################################################
##############################################  Create Stim1 table #####################################################

stim1_df = trimmed_df[trimmed_df['Pulse_index'].str.match('Stim1')]
stim1_df = stim1_df.copy()
stim1_df.insert(8,'Slice_Loc',value = stim1_df['Slice_Loc_Run'].str[:5])
stim1_df[stim1_df.columns[0:19]] = stim1_df[stim1_df.columns[0:19]].astype(str)
# print(stim1_df)
stim1_df.insert(9,'Full_ROI_Id',value = stim1_df['Date']+'__'+stim1_df['Slice_Loc']+'__'+stim1_df['ROI_Id'].astype(str))
stim1_df = stim1_df.groupby(list(stim1_df['Full_ROI_Id']),sort=False).agg(
    {'Date': lambda x: x.iloc[0], 'Id': lambda x: x.iloc[0],'Genotype': lambda x: x.iloc[0],
     'Birthdate': lambda x: x.iloc[0],'Sex': lambda x: x.iloc[0],'Tx': lambda x: x.iloc[0],
     'Tx_Start': lambda x: x.iloc[0],'Slice_Loc_Run': lambda x: x.iloc[0],'Slice_Loc': lambda x: x.iloc[0],
     'Full_ROI_Id': lambda x: x.iloc[0],'Trial_x_Time': lambda x: x.iloc[0],'Stim_Intensity': lambda x: x.iloc[0],
     'Stim_Layer': lambda x: x.iloc[0],'RLI': lambda x: x.iloc[0],'Cx': lambda x: x.iloc[0],
     'n_Pulses': lambda x: x.iloc[0],'Pulse_index': lambda x: x.iloc[0],'IPI': lambda x: x.iloc[0],
     'ROI_Id': lambda x: x.iloc[0],'Laminar': lambda x: x.iloc[0],'Visual': lambda x: x.iloc[0],
     'Layers': lambda x: x.iloc[0],'Amp':'mean','SNR':'mean','Latency':'mean'})
# print(stim1_df)
stim1_df.to_csv('Stim1_Data.csv',index=False)

########################################################################################################################
#########################################  Create Stim2 and PP tables ##################################################

stim2_df = trimmed_df.copy()
stim2_df.insert(8,'Slice_Loc',value = stim2_df['Slice_Loc_Run'].str[:5])
stim2_df.insert(9,'Full_ROI_Id',value = stim2_df['Date']+'__'+stim2_df['Slice_Loc_Run']+'__'+stim2_df['ROI_Id'].astype(str))
# print(stim2_df)

stim2_dup = stim2_df[stim2_df.duplicated(subset='Full_ROI_Id')] #identifies everything that is a duplicate but still no original
# stim2_dup.to_csv('stim2dup.csv',index=Falyse)
# print(stim2_dup)

dup_index = []
full_roi_id_col_index = stim2_df.columns.get_loc('Full_ROI_Id')
for i in range(len(stim2_dup)):
    # print('test')
    # print(stim2_dup.iloc[i,9])
    for j in range(len(stim2_df)):
        if stim2_dup.iloc[i,full_roi_id_col_index] == stim2_df.iloc[j,full_roi_id_col_index]:
            # print(stim2_dup.iloc[i,9])
            # print(stim2_df.iloc[j,9])
            dup_index.append(j)
# print(dup_index)
stim2_df = stim2_df.iloc[dup_index]
# print(stim2_orig)
# print(test)
stim2_df.to_csv('Stim2_Data.csv',index=False)


PP_df = stim2_df.copy()
PP_df = PP_df[PP_df.duplicated(subset='Full_ROI_Id',keep='first')]
PP_df['Pulse_index'] = 'PP'
PP_df['PPR'] = ''
# print(PP_df)
row_index = []
for i in range(len(stim2_df)):
    for j in range(len(stim2_df)):
        if stim2_df.iloc[i,full_roi_id_col_index] == stim2_df.iloc[j,full_roi_id_col_index] and j>i:
        #so no [[0,0]] and no duplication of pairs
            # print(stim2_df.iloc[i,9],stim2_df.iloc[j,9])
            row_index.append([i,j])
# print(row_index)
amp_col_index = stim2_df.columns.get_loc('Amp')
ppr_col_index = PP_df.columns.get_loc('PPR')
for i in range(len(row_index)):
    current_amp = stim2_df.iloc[row_index[i][1],amp_col_index]/stim2_df.iloc[row_index[i][0],amp_col_index]
    PP_df.iloc[i,ppr_col_index] = current_amp
    # print(current_amp)
PP_df.to_csv('PP_Data.csv',index=False)

