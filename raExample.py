#Ra usage example
#By: Christopher Mendoza
"""
This example script uses ra to create a geographic visualization of NetFlow data that is stored in a csv file.
Ra only uses the netflow data that has a destination within the US and further aggregates the markers by region i.e. state.
This example also shows how you can create custom line color decisions as well as custom popup plots.
"""

from ra import ra
import pandas as pd

#Define function to color lines based on if any flow between two locations has a packet count less than 2    
def lineColor(self, df):
    if min(df['dPkts'] < 2):
        return 'blue'
    else:
        return 'black'

#Read csv with NetFlow Data into pandas DataFrame
df = pd.read_csv('temp.csv',index_col = 0)
#Type cast the AS numbers to make sure they are integers
df['src_as'] = df['src_as'].astype(int)
df['dst_as'] = df['dst_as'].astype(int)
#Drop NaN rows from the DataFrame
df = df.dropna().reset_index(drop=True)
#Format the columns to be the way ra needs them i.e. "src_lat", "src_long", "dst_lat" and "dst_long" columns
mI = df.columns.tolist()
newMI = []
for x in range(0,len(mI)):
    if 'src_' not in mI[x]:
        mI[x] = mI[x].replace('src','src_')
    if 'dst_' not in mI[x]:
        mI[x] = mI[x].replace('dst','dst_')
    newMI.append(mI[x])
df.columns = newMI

#Get urls for AS logos from UTEP database
df['src_logo'] = '<img src="' + "http://engsrvdb00.utep.edu/amis/images/as_images/" + df['src_as'].astype(str) + ".png" + '" height="50" width="50">'
df['dst_logo'] = '<img src="' + "http://engsrvdb00.utep.edu/amis/images/as_images/" + df['dst_as'].astype(str) + ".png" + '" height="50" width="50">'

#Make instance of ra
ra = ra(df)
#Set the line fuction to color lines based on the defined function "lineColor"
ra.setLineFunction(lineColor)
#Only include flows that have the destination country as the United States 
ra.focus("dst_country == 'United States'")
#Tell ra to get logos for markers and check if the url is valid
ra.logoCheck = True
ra.getMarkerLogos = True
#Treat all markers in the same region as if they are in the same location i.e. aggregate flows on a region level
ra.aggregate('region')
#Make marker popup widths an appropriate size
ra.popupWidth['marker'] = 700
#Set how many flows to show up in popup
ra.popupLen = 5
#Set up plot variables for map popups
ra.plotX = 'app'
ra.plotY = 'dOctets'
ra.sortVar = 'dOctets'
ra.plotHue = 'app'
ra.plotType = 'bar'
#Select which columns to show in the map popups
ra.markerInfo = ['as','org','lat','long','region','country','continent','logo']
#Create and save map
ra.createMap()
ra.saveMap('MyMap.html')