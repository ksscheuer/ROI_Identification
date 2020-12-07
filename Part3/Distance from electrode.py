import pandas as pd
from io import StringIO

electrode_dat = pd.read_csv('electrode.dat')
# electrode = pd.read_csv(StringIO('electrode.dat'),sep=r'\s{2,}',engine='python')
electrode_dat = electrode_dat.dropna()
electrode_dat = electrode_dat.drop([0,1,2],axis=0)
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
# print(electrode_dat.iloc[0:2])
# print(electrode_dat)
# print(pixelID_to_coords.iloc[electrode_dat.iloc[0:2]])
electrode_pixelID_to_coords = pixelID_to_coords.iloc[list(electrode_dat.iloc[:,0])]
# print(electrode_pixelID_to_coords)
max_xcoord = max(electrode_pixelID_to_coords['XCoord'])
electrode_pixelID_to_coords_max_xcoord = electrode_pixelID_to_coords.loc[electrode_pixelID_to_coords['XCoord'] == max_xcoord]['YCoord']
avg_ycoord = sum(electrode_pixelID_to_coords_max_xcoord)/len(electrode_pixelID_to_coords_max_xcoord)
# print(electrode_pixelID_to_coords.loc[electrode_pixelID_to_coords['XCoord'] == max_xcoord]['YCoord'])
electrode_tip_xcoord = max_xcoord
electrode_tip_ycoord = avg_ycoord
print(electrode_tip_xcoord,electrode_tip_ycoord)