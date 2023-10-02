import pandas as pd # library for data analysis
import requests # library to handle requests
from bs4 import BeautifulSoup # library to parse HTML documents
import numpy as np
import geopandas as gpd
import folium
import branca

#load page with country table
wikiurl = "https://www.wikidata.org/wiki/Wikidata:WikiProject_Lighthouses/lists/lighthouses_by_country"
table_class = "wikitable sortable jquery-tablesorter"
response = requests.get(wikiurl)
print(response.status_code)

soup = BeautifulSoup(response.text, 'html.parser')

#subtract all a href's from page
links = []
for link in soup.findAll('a'):
    links.append(link.get('href'))

#filter or country pages and add rest of url for scraping
links = ["https://www.wikidata.org"+str(i) for i in links if '/lists/lighthouses_by_country/' in str(i)]

#instanciate map
m = folium.Map(location=[40.402576664939424, -3.713975969911108],zoom_start=3,tiles='cartodbdark_matter')


def lighthouse(link):

    """
    function for scraping country page. print statements help detect errors.
    try/except for dealing with exceptions on specific country pages
    """
    #connect to website
    wikiurl = link
    table_class = "wikitable sortable jquery-tablesorter"
    response = requests.get(wikiurl)
    print(response.status_code)

    #scrape text with beautifulsoup
    soup = BeautifulSoup(response.text, 'html.parser')
    indiatable = soup.find('table', {'class': "wikitable"})

    #load table as list
    df = pd.read_html(str(indiatable))
    # convert list to dataframe
    df = pd.DataFrame(df[0])

    #loop over rows in table to subtract images
    file_list = []
    trs = indiatable.find_all('tr')
    for i in trs:
        try:
            im = i.find_all('img')
            file_list.append([x['src'] for x in im])
        except:
            file_list.append('no image available')

    try:
        df['image_link'] = file_list[1:]
    except:
        pass

    #delete rows without coordinates
    df.dropna(subset=['loc (coor)'], inplace=True)

    #split coordinates on /
    df['loc (coor)'] = df['loc (coor)'].str.split('/')

    #split coordinates in lat/lon
    df['lat'] = [i[0] for i in df['loc (coor)']]
    df['lon'] = [i[1] for i in df['loc (coor)']]

    #rename exceptions for more usable data
    df = df.rename({'Lighthouse (en)': 'label (en)'}, axis='columns')
    df = df.rename({'label (zh)': 'label (en)'}, axis='columns')

    #fancy html from https://www.kaggle.com/dabaker/fancy-folium with added images
    def fancy_html(row):
        i = row

        label_en = df['label (en)'].iloc[i]
        print('label check')
        try:
            buildingheight = df['buildingheight'].iloc[i]
        except:
            buildingheight = 'Not available'
        print('buildingheight check')
        try:
            focalheight = df['focalheight'].iloc[i]
        except:
            focalheight = 'Not available'
        print('focalheight check')
        try:
            range_ = df['range'].iloc[i]
        except:
            range_ = 'Not available'
        print('range check')
        try:
            lightcharacteristics = df['lightcharacteristics'].iloc[i]
        except:
            pass
        try:
            lightcharacteristics = df['lightcharact'].iloc[i]
        except:
            lightcharacteristics = 'Not available'
        print('lightcharacteristics check')
        try:
            image = "https:" + str(df['image_link'].iloc[i][0].replace('60px', '300px').replace('50px', '300px'))
        except:
            image = 'https://freesvg.org/img/errname1.png'
        print('image check')
        left_col_colour = "#636363"
        right_col_colour = "#fee391"

        html = """<!DOCTYPE html>
            <html>
            <head>
            <h4 style="margin-bottom:0"; width="300px">{}</h4>""".format(label_en) + """

            </head>
                <table style="height: 126px; width: 300px;">
            <tbody>
            <tr>
            <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Label (En)</span></td>
            <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(label_en) + """
            </tr>
            <tr>
            <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Building Height</span></td>
            <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(buildingheight) + """
            </tr>
            <tr>
            <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Focal Height</span></td>
            <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(focalheight) + """
            </tr>
            <tr>
            <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Range</span></td>
            <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(range_) + """
            </tr>
            <tr>
            <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Light Charasteristics</span></td>
            <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(
            lightcharacteristics) + """
            </tr>
            </tbody>
            </table>
            <br>
            <center><img src={} width="300">""".format(image) + """</center>
            </html>
            """
        return html

    #loop over rows to run fancy html
    for i in range(0, len(df)):
        try:
            html = fancy_html(i)
            print('html check')

            iframe = branca.element.IFrame(html=html, width=310, height=500)
            popup = folium.Popup(iframe, parse_html=True)

            #plotting the lighthouse on the map
            folium.Circle([df['lat'].iloc[i], df['lon'].iloc[i]], radius=750,
                          popup=popup, color="#ffffb3", fill=True, fill_color="#ffffb3").add_to(m)

            print('map check')
        except:
            print(link, ': fail')
            print(df.columns)
            pass

#execute funtion for plotting data on map
for link in links:
    lighthouse(link)
#saving the map as html
# m.save('lighthouse.html')
