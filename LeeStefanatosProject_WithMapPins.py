"""
Name:       Lee Stefanatos
CS230:      Section 6
Data:       Fast Food USA Dataset
URL:

Description:
This program is an interactive data explorer for fast food restaurant data across the USA. Users can filter and visualize trends like:
- Which states have the most fast food locations
- Which cities have the most variety
- Where certain chains are located
The app features maps, charts, and filtering widgets for user-driven exploration.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# [DA1] Clean or manipulate data, lambda function (required)
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_fast_food_usa.csv")
    df['name'] = df['name'].str.strip()
    df['province'] = df['province'].str.upper()
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
st.sidebar.title("🍔 Fast Food Explorer")
st.sidebar.write("Use the filters below to explore the data.")

# [ST1] Multiselect restaurant chains
restaurant_list = df['name'].sort_values().unique().tolist()
selected_restaurants = st.sidebar.multiselect("Select Restaurant Chains", restaurant_list, default=["Taco Bell"])

# [ST2] Dropdown for state
state_list = sorted(df['province'].unique())
selected_state = st.sidebar.selectbox("Select State", state_list, index=state_list.index("CA") if "CA" in state_list else 0)

# [ST3] Text input to filter by city
city_input = st.sidebar.text_input("Optional: Filter by City")

# [DA4] + [DA5] Filter data by condition(s)
filtered_df = df[(df['name'].isin(selected_restaurants)) & (df['province'] == selected_state)]
if city_input:
    filtered_df = filtered_df[filtered_df['city'].str.contains(city_input, case=False)]

st.title("📊 U.S. Fast Food Restaurant Explorer")
st.markdown("Explore restaurant locations, trends, and maps across the USA.")

# [CHART1] Bar chart + [DA2] Sort values
st.header("Top States by Restaurant Count")
top_states = df[df['name'].isin(selected_restaurants)].groupby('province').size().sort_values(ascending=False).head(10)
fig1, ax1 = plt.subplots()
top_states.plot(kind='bar', ax=ax1, color='skyblue')
ax1.set_title("Top 10 States with Most Selected Restaurants")
ax1.set_ylabel("Number of Locations")
st.pyplot(fig1)

# 🔍 Explain Bar Chart
st.markdown("""
This bar chart shows the top 10 states with the highest number of selected restaurant chains.  
It helps answer the question: **Where are fast food chains most densely located?**  
Change the selected chains in the sidebar to explore how the rankings shift.
""")

# [CHART2] Pie chart with "Other" grouping
st.header(f"Distribution in {selected_state}")
state_dist = df[df['province'] == selected_state]['name'].value_counts(normalize=True)
threshold = 0.03
main_dist = state_dist[state_dist >= threshold]
other = state_dist[state_dist < threshold].sum()
if other > 0:
    main_dist["Other"] = other
main_dist = main_dist.sort_values(ascending=False) * 100
fig2, ax2 = plt.subplots()
main_dist.plot.pie(autopct='%1.1f%%', ax=ax2, startangle=90)
ax2.set_ylabel("")
ax2.set_title(f"Restaurant Chain Distribution in {selected_state}")
st.pyplot(fig2)

# 🔍 Explain Pie Chart
st.markdown(f"""
This pie chart shows the market share of restaurant chains in **{selected_state}**.  
Smaller chains are grouped under **"Other"** to improve readability.  
Change the state in the sidebar to compare regional dominance of fast food chains.
""")

# [MAP] PyDeck pinpoint map with tooltips
st.header("Map of Locations")
icon_url = "https://cdn-icons-png.flaticon.com/512/684/684908.png"
icon_data = {"url": icon_url, "width": 242, "height": 242, "anchorY": 242}

# [DA9] Add a new column
if not filtered_df.empty:
    filtered_df['icon_data'] = None
    filtered_df['icon_data'] = filtered_df['icon_data'].apply(lambda x: icon_data)

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v11",
        initial_view_state=pdk.ViewState(
            latitude=filtered_df['latitude'].mean(),
            longitude=filtered_df['longitude'].mean(),
            zoom=6,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                type="IconLayer",
                data=filtered_df,
                get_icon="icon_data",
                get_size=4,
                size_scale=10,
                get_position='[longitude, latitude]',
                pickable=True,
            ),
        ],
        tooltip={"text": "{name}\\n{address}"}
    ))
else:
    st.warning("No data available for selected filters.")

# 🔍 Explain Map
st.markdown(f"""
This interactive map shows the locations of all selected restaurants in **{selected_state}**.  
Hover over the pins to see the name and address of each location.  
Use this view to identify regional clustering or sparse coverage.
""")

# [PY1], [PY2], [PY4], [PY5], [DA3], [DA7]
def get_top_cities(data, restaurant='Taco Bell', top_n=5):
    filtered = data[data['name'] == restaurant]
    grouped = filtered.groupby('city').size().sort_values(ascending=False).head(top_n)
    return grouped.index.tolist(), grouped.values.tolist()

# Function calls [PY1]
city_names, city_counts = get_top_cities(df, selected_restaurants[0])
_ = get_top_cities(df)

# Show result [PY5]
st.header(f"Top Cities for {selected_restaurants[0]}")
st.write({city: count for city, count in zip(city_names, city_counts)})

# 🔍 Explain Top Cities
st.markdown(f"""
This summary shows the top cities with the highest number of **{selected_restaurants[0]}** locations.  
It's useful for spotting urban hotspots or regions of peak popularity.
""")

# [PY3] Try/except
st.subheader("Summary Table of Selected Locations")
try:
    st.dataframe(filtered_df[['name', 'address', 'city', 'province']].reset_index(drop=True))
except Exception as e:
    st.error(f"Something went wrong displaying the table: {e}")

# 🔍 Explain Table
st.markdown("""
This table provides a full list of restaurant locations that match your filter selections.  
Use it to see full addresses or confirm presence in specific cities.
""")
