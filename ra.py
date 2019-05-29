"""
______       ______ _                 _   _ _                 _ _              
| ___ \      |  ___| |               | | | (_)               | (_)             
| |_/ /__ _  | |_  | | _____      __ | | | |_ ___ _   _  __ _| |_ _______ _ __ 
|    // _` | |  _| | |/ _ \ \ /\ / / | | | | / __| | | |/ _` | | |_  / _ \ '__|
| |\ \ (_| | | |   | | (_) \ V  V /  \ \_/ / \__ \ |_| | (_| | | |/ /  __/ |   
\_| \_\__,_| \_|   |_|\___/ \_/\_/    \___/|_|___/\__,_|\__,_|_|_/___\___|_|
By: Christopher Mendoza                                            
"""

import folium
import pandas as pd
from folium.features import CustomIcon
import urllib.request
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
from types import MethodType

class ra():
    """
    Ra is a class will create, save and customize point to point visualizations.
    
    Ra Map Customization Parameters:
        popupLen The amount of flows that will appear in a popup. Default = 3
        sortVar: The name of the column to sort flows by. Default = None
        MarkerInfo: The column names that will appear in the marker popups. Default = None (Shows All)
        getMarkerLogos: Add marker logos to map, will only work if you applied dfAddLogos. Default = False
        logoCheck: Verify if logo is in web-server using url request. Default = True
        lineFunction: Color of line that will be drawn (can be dynamically modified using setLineFunction). Default = 'green'
        lineOpacity: Opacity of line that will be drawn (can be dynamically modified using lineOptions). Default = 1
        popupWidth: Will modify the width of the popup, marker popup and line popup can be adjusted seperately. Default = {'marker':1000,'line':1000}
        plotX: The x-axis variable (name of pandas column) for the plot drawn in the popup. Default = None
        plotY: The y-axis variable (name of pandas column) for the polot drawn in the popup. Default = None
        plotType: Selects the type of plot to draw. Default = 'bar'
        plotHue: Variable (name of pandas column) to adjust hue of points in plot. Default = None
        plotEstimator: The estimator to be used for the plots. Default = sum
        plotCI: Confidence interval for plot. Default = None
    """
    m = folium.Map(location=[0, 0], tiles='OpenStreetMap', zoom_start=2)
    popupLen = 3
    popupOrder = None
    sortVar = None
    markerList1 = []
    markerList2 = []
    markerInfo = None
    getMarkerLogos = False
    logoCheck = True
    lineColor = 'green'
    lineOpacity = 1
    lineFunction = None
    preserve = []
    agg_lats = {}
    agg_longs = {}
    popupWidth = {'marker':1000,'line':1000}
    plotX = None
    plotY = None
    plotType = 'bar'
    plotHue = None
    plotEstimator = sum
    plotCI = None
    
    def __init__(self, df):
        """
        Loads selected dataframe as class dataframe and makes sure it's in the correct format.
        df: Pandas dataframe to set as class dataframe.
        """
        if 'src_lat' not in list(df) or 'src_long' not in list(df) or  'dst_lat' not in list(df) or 'dst_long' not in list(df):
            raise ValueError('Dataset does not contain correct columns')
        else:
            self.df = df
            
    def focus(self,op):
        """
        Filters class dataframe by df.query string given and saves original non-filtered dataframe into origdf.
        op: df.query string
        """
        self.origdf = self.df.copy()
        self.df = self.df.query(op).copy()
        if len(self.df) == 0:
            self.df = self.origdf
            raise ValueError('There are no flows found using this filter, dataset has not been changed')
            
    def lineFunction(self,df):
        """
        Function to add coloring to lines added to the map.
        """
        return 'green'
    
    def setLineFunction(self, method):
        """
        Set user defined lineFunction
        method: user defined function
        
        Example(self,df):
            if max(df['column_name']) > 10:
                return 'red'
        """
        self.lineFunction = MethodType(method, self)
    
    def makePlot(self, df):
        """
        Creates plot for popup.
        """
        try:
            fig, ax = plt.subplots()
            fig = plt.figure()
            if self.plotType == 'scatter':
                sns.scatterplot(self.plotX, self.plotY, data=df, hue = self.plotHue)
            else:
                fig = sns.catplot(self.plotX, self.plotY, data=df,ci = self.plotCI, kind = self.plotType, estimator = self.plotEstimator)
            plt.xticks(rotation = 45)
            plt.tight_layout()
            svg = StringIO()
            fig.savefig(svg, format='svg')
            svgtxt = svg.getvalue()
            svg.close()
            plt.close('all')
            return(svgtxt) 
        except ValueError:
            return('')

    def aggregate(self, column):
        """
        Aggregates class dataframe by src_column and dst_column.
        To aggregate there must be two columns that only differ in name by src_ and dst_ prefixes.
        """
        self.df['src_lat_na'] = self.df['src_lat']
        self.df['src_long_na'] = self.df['src_long']
        self.df['dst_lat_na'] = self.df['dst_lat']
        self.df['dst_long_na'] = self.df['dst_long']
        self.agg_locs = {}
        columnList = self.df['src_' + column].unique().tolist()
        columnList += self.df['dst_' + column].unique().tolist()
        columnList = set(columnList)
        for x in columnList:
            lat_sum = self.df[self.df['src_' + column] == x]['src_lat'].sum()
            lat_count = len(self.df[self.df['src_' + column] == x])
            lat_sum += self.df[self.df['dst_' + column] == x]['dst_lat'].sum()
            lat_count += len(self.df[self.df['dst_' + column] == x])
            long_sum = self.df[self.df['src_' + column] == x]['src_long'].sum()
            long_count = len(self.df[self.df['src_' + column] == x])
            long_sum += self.df[self.df['dst_' + column] == x]['dst_long'].sum()
            long_count += len(self.df[self.df['dst_' + column] == x])
            self.agg_lats[x] = lat_sum/lat_count
            self.agg_longs[x] = long_sum/long_count
        self.df['src_lat'] = self.df['src_' + column].map(self.agg_lats)
        self.df['src_long'] = self.df['src_' + column].map(self.agg_longs)
        self.df['dst_lat'] = self.df['dst_' + column].map(self.agg_lats)
        self.df['dst_long'] = self.df['dst_' + column].map(self.agg_longs)
    
    def split(self):
        """
        Splits class dataframe into intra and inter communication flows.
        """
        self.intra = self.df.query('src_lat == dst_lat and src_long == dst_long')
        self.inter = self.df.drop(self.intra.index.tolist())
            
    def makePopupHTML(self, df, data = True):
        """
        Creates HTML code to embed in marker and line popups.
        Data is enabled if a plot needs to be made.
        Plot will only be made if user defines x and y variables.
        """
        h = ''
        ipix = 75*(min(len(df),self.popupLen))
        ipix = max(ipix,130)
        if self.plotX != None and self.plotY != None and len(df) > 1 and data:
            h = self.makePlot(df)
            ipix += 400
        if len(df) > self.popupLen:
            df = df.iloc[0:self.popupLen]
        if self.sortVar != None and data:
            df = df.sort_values(by=[self.sortVar],ascending = False).reset_index(drop=True)
        if self.popupOrder != None and data:
            df = df[self.popupOrder]
        html = df.to_html(escape = False).replace('<td>','<td align = "center">').replace('<thead>','<thead align = "center">').replace('border="1"','border="5"').replace('<tr style="text-align: right;">','<tr style="text-align: center;">')
        if h != '':
            html = h + html
        return html, ipix
            
    def intraMarkers(self):
        """
        Creates html for intra-communication markers and stores them into dictionary to be rendered later.
        """
        unique = self.intra.groupby(['src_lat','src_long']).size().reset_index()
        for index, row in unique.iterrows():
            html = ''
            src_html = ''
            location = [row['src_lat'],row['src_long']]
            temp = self.intra[(self.intra['src_lat'] == location[0]) & (self.intra['src_long'] == location[1])].reset_index(drop=True)
            html,ipix = self.makePopupHTML(temp)
            if self.getMarkerLogos:
                for x in temp['src_logo'].unique().tolist():
                    try:
                        logo = x.replace('<img src="','').replace('" height="50" width="50">','')
                        if self.logoCheck:
                            urllib.request.urlretrieve(logo)
                        break
                    except urllib.error.HTTPError:
                        logo = None
            else:
                logo = None
            columns = ['lat','long','count']
            unique.columns = columns
            if self.markerInfo == None:
                markerInfo = [s.replace('src_','') for s in self.df.columns.tolist() if 'src_' in s]
            else:
                markerInfo = self.markerInfo
            colval = ['src_' + s for s in markerInfo]
            tempdf1 = temp[colval]
            tempdf1.columns = markerInfo
            if self.markerInfo == None:
                markerInfo = [s.replace('dst_','') for s in self.df.columns.tolist() if 'dst_' in s]
            else:
                markerInfo = self.markerInfo
            colval = ['dst_' + s for s in markerInfo]
            tempdf2 = temp[colval]
            tempdf2.columns = markerInfo
            tempdf = pd.concat([tempdf1,tempdf2]).reset_index(drop=True)
            tempdf = tempdf.drop_duplicates()
            src_html,ipix2 = self.makePopupHTML(tempdf,data=False)
            tempdict = {'lat':location[0],'long':location[1],'html1':html,'html2':src_html,'logo':logo,'ipix':ipix + ipix2}
            self.markerList1.append(tempdict)
                
    def interMarkers(self):
        """
        Creates html for inter-communication markers and stores them into dictionary to be rendered later.
        """
        columns = ['lat','long','count']
        unique = self.inter.groupby(['src_lat','src_long']).size().reset_index()
        unique1 = self.inter.groupby(['dst_lat','dst_long']).size().reset_index()
        unique.columns = columns
        unique1.columns = columns
        unique = pd.concat([unique,unique1]).reset_index(drop = True)
        unique = unique.groupby(['lat','long']).size().reset_index()
        for index, row in unique.iterrows():
            src_html = ''
            dst_html = ''
            location = [row['lat'],row['long']]
            temp = self.inter[((self.inter['src_lat'] == location[0]) & (self.inter['src_long'] == location[1])) | ((self.inter['dst_lat'] == location[0]) & (self.inter['dst_long'] == location[1]))].reset_index(drop=True)
            check_src = temp[(temp['src_lat'] == location[0]) & (temp['src_long'] == location[1])]
            check_dst = temp[(temp['dst_lat'] == location[0]) & (temp['dst_long'] == location[1])]
            if len(check_src) > 0:
                if self.markerInfo == None:
                    markerInfo = [s.replace('src_','') for s in self.df.columns.tolist() if 'src_' in s]
                else:
                    markerInfo = self.markerInfo
                colval = ['src_' + s for s in markerInfo]
                tempdf = check_src[colval]
                tempdf.columns = markerInfo
                tempdf = tempdf.drop_duplicates()
                src_html,ipix = self.makePopupHTML(tempdf,data=False)
                if self.getMarkerLogos:
                    for x in check_src['src_logo'].unique().tolist():
                        try:
                            logo = x.replace('<img src="','').replace('" height="50" width="50">','')
                            if self.logoCheck:
                                urllib.request.urlretrieve(logo)
                            break
                        except urllib.error.HTTPError:
                            logo = None
                else:
                    logo = None
            elif len(check_dst) > 0:
                if self.markerInfo == None:
                    markerInfo = [s.replace('dst_','') for s in self.df.columns.tolist() if 'dst_' in s]
                else:
                    markerInfo = self.markerInfo
                colval = ['dst_' + s for s in markerInfo]
                tempdf = check_dst[colval]
                tempdf.columns = markerInfo
                tempdf = tempdf.drop_duplicates()
                dst_html,ipix = self.makePopupHTML(tempdf,data=False)
                if self.getMarkerLogos:
                    for x in check_dst['dst_logo'].unique().tolist():
                        logo = x.replace('<img src="','').replace('" height="50" width="50">','')
                        if self.logoCheck and logo != None:
                            try:
                                urllib.request.urlretrieve(logo)
                                break
                            except urllib.error.HTTPError:
                                logo = None
                        else:
                            logo = None
                else:
                    logo = None
            tempdict = {'lat':location[0],'long':location[1],'html1':'','html2':src_html + dst_html,'logo':logo,'ipix':ipix}
            self.markerList2.append(tempdict)
            
    def addMarkers(self):
        """
        Renders markers on class map based on html generated from inter and intra marker functions.
        """
        df1 = pd.DataFrame(self.markerList1)
        df2 = pd.DataFrame(self.markerList2)
        df3 = pd.concat([df1,df2])
        generate = df3.groupby(['lat','long']).size().reset_index()
        for index,row in generate.iterrows():
            temp = df3[(df3['lat'] == row['lat']) & (df3['long'] == row['long'])]
            html = ''
            logo = None
            ipix = min(800,sum(temp['ipix']))
            for index,row in temp.iterrows():
                html = html + row['html1'] + row['html2']
                if row['logo'] != None and logo == None:
                    logo = row['logo']
            location = [row['lat'],row['long']]
            iframe = folium.IFrame(html=html, width=self.popupWidth['marker'], height = ipix)
            popup = folium.Popup(iframe, max_width=2650)
            if logo != None:
                icon = CustomIcon(
                        logo,
                        icon_size=(40, 40),
                        popup_anchor=(0, -20))
                m1 = folium.Marker(
                        location=location,
                        popup=popup,
                        icon = icon)
            else:
                m1 = folium.Marker(
                        location=location,
                        popup=popup
                        )
            self.m.add_child(m1)
            
    def drawLines(self):
        """
        Creates html for line popups, then renders lines on class map.
        """
        sortDF = self.inter.groupby(['src_lat','src_long','dst_lat','dst_long']).size().reset_index()
        
        droplist = []
        for index,row in sortDF.iterrows():
            test = sortDF.loc[(sortDF['src_lat'] == row['dst_lat']) & 
                            (sortDF['src_long'] == row['dst_long']) &
                            (sortDF['dst_lat'] == row['src_lat']) &
                            (sortDF['dst_long'] == row['src_long'])].index
            if len(test) > 0:
                if index not in droplist:
                    droplist.append(test[0])
        sortDF.drop(droplist,inplace = True)
        
        for index,row in sortDF.iterrows():
            location1 = [row['src_lat'],row['src_long']]
            location2 = [row['dst_lat'],row['dst_long']]
            temp = self.inter[((self.inter['src_lat'] == row['src_lat']) & 
                              (self.inter['src_long'] == row['src_long']) &
                              (self.inter['dst_lat'] == row['dst_lat']) &
                              (self.inter['dst_long'] == row['dst_long'])) |
                              ((self.inter['src_lat'] == row['dst_lat']) & 
                              (self.inter['src_long'] == row['dst_long']) &
                              (self.inter['dst_lat'] == row['src_lat']) &
                              (self.inter['dst_long'] == row['src_long']))]
            self.lineColor = self.lineFunction(temp)
            html,ipix = self.makePopupHTML(temp)
            ipix = min(800,ipix)
            iframe = folium.IFrame(html=html, width=self.popupWidth['line'], height = ipix)
            popup = folium.Popup(iframe, max_width=2650)
            myline = folium.PolyLine([location1,location2], color = self.lineColor,opacity = self.lineOpacity, popup = popup)
            self.m.add_child(myline)
        
    def saveMap(self, savefile):
        """
        Saves map file.
        Can be saved as a .ejs file to be rendered on a server.
        """
        if '.html' not in savefile and '.ejs' not in savefile:
            savefile = savefile + '.html'   
        self.m.save(savefile)
    
    def createMap(self):
        """
        Calls appropriate functions to create a map from Ra instance dataframe.
        """
        pd.set_option('display.max_colwidth', -1)
        sns.set(font_scale = 1.25)
        self.split()
        self.intraMarkers()
        self.interMarkers()
        self.addMarkers()
        self.drawLines()