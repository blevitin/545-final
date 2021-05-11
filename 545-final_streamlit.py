import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import json


st.title("Massachusetts Invasive Species Data Visualizations")
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("# Brenna Levitin")
st.markdown("## IS 545: Advanced Data Visualization <br> University of Illinois, Urbana-Champaign <br> Spring 2021", unsafe_allow_html=True)

st.sidebar.subheader("Invasive species data from EDDMapS (2021).")
st.sidebar.markdown("These visualizations are based on a dataset aggregated by EDDMapS and lightly cleaned by Brenna Levitin. Numbers within do not represent the absolute occurrences of these species, merely the number of reports of the species in the dataset.")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

@st.cache
def get_dataframe():
    dataframe = pd.read_csv("edited_dataset.csv", usecols=['FID', 'SciName', 'ComName', 'Nativity', 'Location'], dtype={'FID':str, 'SciName':str, 'ComName':str, 'Nativity':str, 'Location':str})
    return dataframe

dataframe = get_dataframe()

counties = dataframe['Location'].unique()
countiesNoNan = counties[0:14]

nativity = dataframe['Nativity'].unique()
nativityNoNan = nativity[0:3]

new_DF = dataframe.replace("nan", float("nan"))
new_new_DF = new_DF.dropna(subset=['Location', 'Nativity'])


testDict = {}

for species in new_new_DF['ComName']:
    if species in testDict:
        testDict[species] = testDict[species] + 1
    else:
        testDict[species] = 1

parentsList = []
for i in range(782):
    parentsList.append("species")

def getListKeys(dict):
    return list(dict.keys())

def getListValues(dict):
    return list(dict.values())

labels1 = getListKeys(testDict)
values1 = getListValues(testDict)
parents1 = parentsList

st.sidebar.subheader("Select a species by common name")
speciesSelect = st.sidebar.selectbox(' ', labels1)
st.sidebar.subheader("Select a county")
countySelect = st.sidebar.selectbox(' ', countiesNoNan)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("EDDMapS. 2021. Early Detection & Distribution Mapping System. The University of Georgia - Center for Invasive Species and Ecosystem Health. Available online at http://www.eddmaps.org/; data downloaded 03/21/2021.")


# Make a stacked bar chart of Nativity by county
aChart = alt.Chart(new_new_DF).mark_bar().encode(
    x='Location',
    y="count(Nativity)",
    color=alt.Color('Nativity', scale=alt.Scale(scheme='category10')),
    tooltip="count(Nativity)"
)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.subheader("Breakdown of nativity for reports from each county.")
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.altair_chart(aChart,use_container_width=True)


# Make a treemap of all species reported in MA by number of reports over entire dataset
fig1 = go.Figure(go.Treemap(labels = labels1, values = values1, parents = parents1))

st.markdown("---")
st.subheader("All reports for Massachusetts, sorted by species and count.")
st.plotly_chart(fig1, use_container_width=True)


# Make a treemap of reports' nativity
isNative = new_new_DF.apply(lambda x: True if x['Nativity'] == 'Native' else False, axis = 1)
nativeCount = len(isNative[isNative == True].index)

isInvasive = new_new_DF.apply(lambda x: True if x['Nativity'] == 'Introduced' else False, axis = 1)
invasiveCount = len(isInvasive[isInvasive == True].index)

isBoth = new_new_DF.apply(lambda x: True if x['Nativity'] == 'Native and Introduced' else False, axis = 1)
bothCount = len(isBoth[isBoth == True].index)

labels = ['Nativity', 'Native', 'Introduced', 'Native and Introduced']
values = ['35224', '2263', '31936', '1025']
parents = ["", 'Nativity', 'Nativity', 'Nativity']

fig = go.Figure(go.Treemap(labels = labels, values = values, parents = parents, marker_colors = ['white', 'light blue', 'orange', 'royal blue']))

st.markdown("---")
st.subheader("All reports for Massachusetts, sorted by nativity.")
st.plotly_chart(fig, use_container_width=True)



# Make a heatmap of report quantities in the shape of MA, divided by county
DATA = json.load(open("correctedCoords.geojson"))
INITIAL_VIEW_STATE = pdk.ViewState(latitude=42.40, longitude=-71.38, zoom=7,max_zoom=7.5, min_zoom=6,pitch=0,bearing=0)

countPerCounty = {}

for c in countiesNoNan:
    selectedSpecCount = new_new_DF.apply(lambda x: True if (x['ComName'] == '%s' % (speciesSelect)) and (x['Location'] == '%s' % (c)) else False, axis = 1)

    countPerCounty[c.upper()] = len(selectedSpecCount[selectedSpecCount].index)

for place in DATA["features"]:
     county = place["properties"]["COUNTY"]
     if county in countPerCounty.keys():
         place["colorValue"] = countPerCounty.get(county)

geojson = pdk.Layer(
    "GeoJsonLayer",
    DATA,
    stroked=True,
    filled=True,
    extruded = False,
    wireframe = False,
    get_fill_color = "[47,255,0,(colorValue/600)*255]",
    get_line_color = [0,0,0],
    get_line_width = 150,
)

testMap = pdk.Deck(layers=geojson, map_style="light_no_labels", initial_view_state=INITIAL_VIEW_STATE)

st.subheader("Choose a species in the left sidebar to see a heatmap of which counties have reported more occurrences. Pan and zoom as desired.")
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Suggested species: purple loosestrife, multiflora rose, and oriental bittersweet.")
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.pydeck_chart(pydeck_obj=testMap,use_container_width=True)
st.markdown("<br>",unsafe_allow_html=True)
st.markdown("Note: Pydeck tooltips do not work in Streamlit (reported bug). Values for %s are listed below." % (speciesSelect))
st.table(pd.DataFrame(list(countPerCounty.items()),columns=["County","Total"]))




# Make a treemap of all species reported in a selected county by number of reports
countPerSelectedCounty = {}

for s in labels1:
    selectedSpecCount = new_new_DF.apply(lambda x: True if (x['Location'] == '%s' % (countySelect)) and (x['ComName'] == '%s' % (s)) else False, axis = 1)
    if len(selectedSpecCount[selectedSpecCount].index) != 0:
        countPerSelectedCounty[s] = len(selectedSpecCount[selectedSpecCount].index)

labels2 = getListKeys(countPerSelectedCounty)
values2 = getListValues(countPerSelectedCounty)

st.markdown("---")
st.subheader("All reports for %s County, arranged by species. To view data for a new County, use the drop-down box in the left sidebar. Note: takes a while to load!" % (countySelect))
newFig = go.Figure(go.Treemap(labels = labels2, values = values2, parents = parents1))
st.plotly_chart(newFig, use_container_width=True)