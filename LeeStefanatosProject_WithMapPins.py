"""
Name:       Lee Stefanatos
CS230:      Section 6
Data:       Fast Food USA Dataset
URL: https://leestefanatosproject-zprcovwm49cu7ttxdobcpw.streamlit.app/

Description:
This program is an interactive data explorer for fast food restaurant data across the USA. Users can filter and visualize trends like:
- Which states have the most fast food locations
- Which cities have the most variety
- Where certain chains are located
The app features maps, charts, and filtering widgets for user-driven exploration.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt #good with plotting library
import pydeck as pdk #helps with interactive maps inside streamlit

# [DA1] Clean or manipulate data, lambda function
@st.cache_data #make sure it dosen't keep rerunning
def load_data():
    df = pd.read_csv("cleaned_fast_food_usa.csv") #loads the file
    df['name'] = df['name'].str.strip() #removes space from names
    df['province'] = df['province'].str.upper() #uppercases all first letters of restaurants
    return df

df = load_data()

# [ST4] Page styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f9f9f9;
    }
    h1, h2, h3 {
        color: #d62728;
    }
    .stSidebar > div:first-child {
        background-color: #ffe6e6;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar controls
st.sidebar.title("🍔 Lee's Fast Food Explorer")
st.sidebar.write("Use the filters below to explore the data.")

# [ST3} Multiselect restaurant chains
restaurant_list = df['name'].sort_values().unique().tolist() #extracts sorted list of restaaurant names
selected_restaurants = st.sidebar.multiselect("Select Restaurant Chains", restaurant_list, default=["Taco Bell"]) #displays a multiselect widget in sidebar with default value "Tacobell"

# [ST2] Dropdown for state
state_list = sorted(df['province'].unique()) #displays a list of all US states from data
selected_state = st.sidebar.selectbox("Select State", state_list, index=state_list.index("CA") if "CA" in state_list else 0) #displays a drop down menu to let user pick one state with a default value of CA

# [ST3] Text input to filter by city
city_input = st.sidebar.text_input("Optional: Filter by City") # optional text input box where users can manually enter a city name

# [DA4] + [DA5] Filter data by condition(s) checks if restaurant's name is in the list of restaurants / checks if in state
filtered_df = df[(df['name'].isin(selected_restaurants)) & (df['province'] == selected_state)] #filters by one condition DA4
if city_input:
    filtered_df = filtered_df[filtered_df['city'].str.contains(city_input, case=False)] # filters by mutiple conditions combined with AND must be in selected state and resturant must be in it aswell

st.title("📊 Lee's U.S. Fast Food Restaurant Explorer")
st.markdown("Explore restaurant locations, trends, and maps across the USA.")

# [CHART1] Bar chart + [DA2] Sort values
st.header("Top States by Restaurant Count")
top_states = df[df['name'].isin(selected_restaurants)].groupby('province').size().sort_values(ascending=False).head(10) #filters data to only include rows for selected
fig1, ax1 = plt.subplots() # creates a bar chart using matplotlib
top_states.plot(kind='bar', ax=ax1, color='skyblue') #determines the x axis values
ax1.set_title("Top 10 States with Most Selected Restaurants") # title
ax1.set_ylabel("Number of Locations") #y axis
st.pyplot(fig1) #displays it

# Explain Bar Chart
st.markdown("""
This bar chart shows the top 10 states with the highest number of selected restaurant chains.  
It helps answer the question: **Where are fast food chains most densely located?**  
Change the selected chains in the sidebar to explore how the rankings shift.
""")

# [CHART2] Pie chart with "Other" grouping
st.header(f"Distribution in {selected_state}") #header
state_dist = df[df['province'] == selected_state]['name'].value_counts(normalize=True) #Filters to only include rows from the selected state, then counts how often each restaurant appears.normalize=True gives the proportions (percentages) rather than raw counts.
threshold = 0.03 #sets threshold of 3 any less will be grouped
main_dist = state_dist[state_dist >= threshold] #keeps the ones that are 3 or more
other = state_dist[state_dist < threshold].sum() #adds the smaller ones to combine them under "other"
if other > 0:
    main_dist["Other"] = other #this adds other to chart
main_dist = main_dist.sort_values(ascending=False) * 100 #sorts from big to small and converts to percentages
fig2, ax2 = plt.subplots() # adds new figure and axis to chart
main_dist.plot.pie(autopct='%1.1f%%', ax=ax2, startangle=90) #plots the pie chart shows percentage and make sure it starts at top
ax2.set_ylabel("") #removes y axis
ax2.set_title(f"Restaurant Chain Distribution in {selected_state}")
st.pyplot(fig2) #display

# Explain Pie Chart
st.markdown(f"""
This pie chart shows the market share of restaurant chains in **{selected_state}**.  
Smaller chains are grouped under **"Other"** to improve readability.  
Change the state in the sidebar to compare regional dominance of fast food chains.
""")

# [MAP] PyDeck pinpoint map with tooltips
st.header("Map of Locations")
icon_url = "https://cdn-icons-png.flaticon.com/512/684/684908.png" #image of pinpoint
icon_data = {"url": icon_url, "width": 242, "height": 242, "anchorY": 242} #sizing

# [DA9] Add a new column and perform caculations
if not filtered_df.empty: # checks if dataset after applying isnt empty
    filtered_df['icon_data'] = None #creates a new column and intilizes it with none
    filtered_df['icon_data'] = filtered_df['icon_data'].apply(lambda x: icon_data) # fills the new icon data by applying lamda function that sets every row icon to same icon data disiconary

    st.pydeck_chart(pdk.Deck( #rederes a pydeck interactive map
        map_style="mapbox://styles/mapbox/streets-v11", # uses mapbox style that resembles a standard street map
        initial_view_state=pdk.ViewState(                # centers the map based on average lag and longitude
            latitude=filtered_df['latitude'].mean(),
            longitude=filtered_df['longitude'].mean(),
            zoom=6,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                type="IconLayer", #uses icon layer to show pins on each location
                data=filtered_df,
                get_icon="icon_data", #pulls data from the new icon data column
                get_size=4,
                size_scale=10,
                get_position='[longitude, latitude]', #gets position from above
                pickable=True, #allows users to hover over tooltips
            ),
        ],
        tooltip={"text": "{name}\\n{address}"} #shows restaurant name and address when user hovers over
    ))
else:
    st.warning("No data available for selected filters.") #shows a warning if no data is filtered or there is no restaurant in that specific state

# Explain Map
st.markdown(f"""
This interactive map shows the locations of all selected restaurants in **{selected_state}**.  
Hover over the pins to see the name and address of each location.  
Use this view to identify regional clustering or sparse coverage.
""")

# [PY1parameters with default values], [PY2return more than 1 value], [PY4], [PY5using and displaying a dictionary], [DA3Find Top N Values], [DA7]
def get_top_cities(data, restaurant='Taco Bell', top_n=5): #py1
    filtered = data[data['name'] == restaurant] #filters the data to only include selected restaurant
    grouped = filtered.groupby('city').size().sort_values(ascending=False).head(top_n) #groups data by size, sorts most to fewest and returns top cities
    return grouped.index.tolist(), grouped.values.tolist() #py2 returns top city names and corresponding counts

# Function calls [PY1]
city_names, city_counts = get_top_cities(df, selected_restaurants[0]) # this calls gettopcities function using full dataset and first restaurant selected
_ = get_top_cities(df) # calls the same function but uses the default restaurant

# Show result [PY5]
# Show result [PY5]
st.header(f"Top Cities for {selected_restaurants[0]}")

# Create a DataFrame from the top cities and counts
city_data = {city: count for city, count in zip(city_names, city_counts)}
city_df = pd.DataFrame(list(city_data.items()), columns=["City", "Number of Locations"])

# Display it as an interactive table
st.dataframe(city_df)

# 🔍 Explain Top Cities
st.markdown(f"""
This summary shows the top cities with the highest number of **{selected_restaurants[0]}** locations.  
It's useful for spotting urban hotspots or regions of peak popularity.
""")

# [PY3] Try/except
st.subheader("Summary Table of Selected Locations") # adds a subheading in streamlit to add upcoming table selection
try: # it displays only columns while reset index resets the row to 0 without keeping original index
    st.dataframe(filtered_df[['name', 'address', 'city', 'province']].reset_index(drop=True))
except Exception as e: # this is the error message if it dosen't work
    st.error(f"Something went wrong displaying the table: {e}")

# 🔍 Explain Table
st.markdown("""
This table provides a full list of restaurant locations that match your filter selections.  
Use it to see full addresses or confirm presence in specific cities.
""")
