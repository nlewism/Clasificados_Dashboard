from supabase import create_client, Client
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_elements import elements, dashboard
from dotenv import load_dotenv
import os

# Load environment Variable
load_dotenv("/Users/natalielewis/Desktop/Programming/AGENT_DASHBOARD/.env")

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL") 
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit App
st.set_page_config(page_title="All Properties", page_icon="📷", layout="wide")

# Sidebar filters
st.sidebar.header("Filters")

# Fetch unique values for dropdowns
all_properties = supabase.table("properties").select("type").execute().data
if isinstance(all_properties, list) and all_properties and isinstance(all_properties[0], dict):
    property_types = list({prop['type'] for prop in all_properties if 'type' in prop})
elif isinstance(all_properties, list):
    property_types = list(set(all_properties))
else:
    property_types = []

all_brokers = supabase.table("properties").select("broker").execute().data
if isinstance(all_brokers, list) and all_brokers and isinstance(all_brokers[0], dict):
    property_brokers = list({prop['broker'] for prop in all_brokers if 'broker' in prop})
elif isinstance(all_brokers, list):
    property_brokers = list(set(all_brokers))
else:
    property_brokers = []

all_regions = supabase.table("properties").select("region").execute().data
if isinstance(all_regions, list) and all_regions and isinstance(all_regions[0], dict):
    regions = list({prop['region'] for prop in all_regions if 'region' in prop})
elif isinstance(all_regions, list):
    regions = list(set(all_regions))
else:
    regions = []

all_pueblos = supabase.table("properties").select("pueblo").execute().data
if isinstance(all_pueblos, list) and all_pueblos and isinstance(all_pueblos[0], dict):
    pueblos = list({prop['pueblo'] for prop in all_pueblos if 'pueblo' in prop})
elif isinstance(all_pueblos, list):
    pueblos = list(set(all_pueblos))
else:
    pueblos = []

all_barrios = supabase.table("properties").select("barrio").execute().data
if isinstance(all_barrios, list) and all_barrios and isinstance(all_barrios[0], dict):
    barrios = list({prop['barrio'] for prop in all_barrios if 'barrio' in prop})
elif isinstance(all_barrios, list):
    barrios = list(set(all_barrios))
else:
    barrios = []

# Sidebar filters
max_price_db = supabase.table("properties").select("price").order("price", desc=True).limit(1).execute().data
max_price_value = int(max_price_db[0]['price']) if max_price_db else 1000000  # Ensure max_price_value is an integer
min_price = st.sidebar.number_input("Minimum Price", min_value=0, max_value=max_price_value, value=0, step=1000)
max_price = st.sidebar.number_input("Maximum Price", min_value=0, max_value=max_price_value, value=max_price_value, step=1000)
# Ensure min_price is not greater than max_price
if min_price > max_price:
    st.sidebar.error("Minimum price cannot be greater than maximum price.")
selected_types = st.sidebar.multiselect("Property Types", property_types)
selected_brokers = st.sidebar.multiselect("Brokers", property_brokers)
min_bedrooms, max_bedrooms = st.sidebar.slider("Bedrooms", 0, 10, (0, 10), step=1)
min_bathrooms, max_bathrooms = st.sidebar.slider("Bathrooms", 0, 10, (0, 10), step=1)
selected_region = st.sidebar.multiselect("Region", regions)
selected_pueblo = st.sidebar.multiselect("Pueblo", pueblos)
selected_barrio = st.sidebar.multiselect("Barrio", barrios)
optioned_status = st.sidebar.selectbox("Optioned", ["Any", "Yes", "No"])
price_changed_status = st.sidebar.selectbox("Price Changed", ["Any", "Yes", "No"])

# Build the query
query = supabase.table("properties").select("*").order("last_seen", desc=True)
# Apply filters to the query
query = query.gte("price", min_price).lte("price", max_price)
query = query.gte("bedrooms", min_bedrooms)
if max_bedrooms < 10:
    query = query.lte("bedrooms", max_bedrooms)
query = query.gte("bathrooms", min_bathrooms)
if max_bathrooms < 10:
    query = query.lte("bathrooms", max_bathrooms)
if selected_types:
    query = query.in_("type", selected_types)
if selected_brokers:
    query = query.in_("broker", selected_brokers)
if selected_region:
    query = query.in_("region", selected_region)
if selected_pueblo:
    query = query.in_("pueblo", selected_pueblo)
if selected_barrio:
    query = query.in_("barrio", selected_barrio)
if optioned_status != "Any":
    query = query.eq("optioned", optioned_status == "Yes")
if price_changed_status != "Any":
    query = query.eq("price_changed", price_changed_status == "Yes")

# Execute the query
response = query.execute()
properties = response.data

# Visualization
df = pd.DataFrame(properties)

# Ensure price is numeric
df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

# Remove duplicates
df = df.drop_duplicates()

# Group by County and calculate the number of listings and average price
county_summary = df.groupby('region').agg(
    properties_sold=('region', 'size'),
    average_price=('price', 'mean')
).reset_index()

def main_page():
    st.title("Real Estate Dashboard")
    layout = [
        dashboard.Item("average_price_cards", 0, 0, 6, 2),
        dashboard.Item("bar_chart", 0, 2, 6, 3),
        dashboard.Item("pie_chart", 6, 2, 6, 3),
        dashboard.Item("scatter_plot_type", 0, 5, 6, 3),
        dashboard.Item("box_plot", 6, 5, 6, 3),
    ]
    with elements("dashboard"):
        with dashboard.Grid(layout):
            st.subheader("Average Home Price per Region")
            cols = st.columns(5)
            for index, row in county_summary.iterrows():
                with cols[index % 5]:
                    st.markdown(
                        f"""
                        <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 5px;">
                            <h3 style="text-align: center;">{row['region']}</h3>
                            <p style="text-align: center; font-size: 24px;">${int(row['average_price']):,}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.subheader("Average Prices by Region")
            fig_bar = px.bar(county_summary, x='region', y='average_price', title='Average Prices by Region')
            st.plotly_chart(fig_bar, key="bar_chart")

            st.subheader("Distribution of Property Types")
            property_type_counts = df['type'].value_counts()
            fig_pie = px.pie(df, names='type', title='Distribution of Property Types')
            st.plotly_chart(fig_pie, key="pie_chart")

            st.subheader("Property Type vs Price")
            fig_scatter_property_type = px.strip(df, x='type', y='price', title='Scatter Plot of Property Type vs Price')
            st.plotly_chart(fig_scatter_property_type, key="scatter_plot_type")

            st.subheader("Prices by Property Type")
            fig_box = px.box(df, x='type', y='price', title='Box Plot of Prices by Property Type')
            st.plotly_chart(fig_box, key="box_plot")

def page2():
    st.markdown("# Page 2 ❄️")
    st.sidebar.markdown("# Page 2 ❄️")
    #this is the region breakdown place. You choose a region to breakdown and you have a different landing page for each 

def page3():
    st.markdown("# Page 3 🎉")
    st.sidebar.markdown("# Page 3 🎉")
    #this is your property type breakdown page. You can see the different property types available and compare the prices + number of listings available (could possibly include financing info)

page_names_to_funcs = {
    "Main Page": main_page,
    "Page 2": page2,
    "Page 3": page3,
}
selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()

# Display properties
st.title("📷 Properties")

if not properties:
    st.warning("No properties available.")
else:
    st.write("These are properties based on your filters:")
    for property in properties:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(
                f"""
                <a href="{property['link']}" target="_blank">
                    <img src="{property['piclink']}" alt="Property Image" style="width:100%; height:auto; border-radius:8px;"/>
                </a>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.write(f"**Title**: {property['title']}")
            st.write(f"**Price**: ${property['price']:,.2f}")
            st.write(f"**Pueblo**: {property['pueblo']}")
            st.write(f"**Barrio**: {property['barrio']}")
            st.write(f"**Bedrooms**: {property['bedrooms']}")
            st.write(f"**Bathrooms**: {property['bathrooms']}")
            st.write(f"**Last Seen**: {property['last_seen']}")

            if property["assigned_agent"]:
                st.write(f"**Assigned Agent**: {property['assigned_agent']}")
            else:
                if st.button(f"Assign Property ID {property['id']}", key=f"assign-{property['id']}"):
                    username = "agent_1"  # Replace with dynamic username from your authentication system
                    supabase.table("properties").update({"assigned_agent": username}).eq("id", property["id"]).execute()
                    st.success(f"Property ID {property['id']} assigned to {username}!")
                    st.experimental_rerun()



# Footer
st.write("---")

