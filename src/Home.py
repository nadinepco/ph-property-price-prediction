import streamlit as st

# Set page config
st.set_page_config(
    page_title="SPICEstimate",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)
##### classes #####
from db import Database
from model import HousePricePredictor

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import time
import os

import logging
from utils import formatPrice, convert_to_eur, add_eur_price, update_currency
import warnings

# Set warning display to show the complete message
warnings.filterwarnings("always", category=UserWarning)
logging.basicConfig(level=logging.INFO)

# Define CSS to style the property container
st.markdown(
    """
    <style>
    .property-listings {
            max-height: 400px; /* Set the desired height */
            overflow-y: auto;
        }
    .property-container {
        display: flex;
        align-items: flex-start;
        margin-bottom: 20px;
    }
    .property-image {
        flex: 0 0 50%;
        margin-right: 20px;
    }
    .property-details {
        flex: 1;
        padding: 10px;
        margin-top: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_classes():
    """Instantiate the classes
    :return: Database and HousePricePredictor class
    """
    logging.info("Instantiating Database and HousePricePredictor classes...")
    model_path = os.path.join(os.path.dirname(__file__), "../models/rf_model.pkl")

    db = Database()
    model = HousePricePredictor(model_path)
    return db, model


##### global variables #####
db, model = load_classes()


#################################################################
###                      Functions                            ###
#################################################################
@st.cache_data
def get_regions():
    """Get a dictionary of region_name: region_id that is read from the database
    :return: dictionary of region_name: region_id
    """
    # Get regions from the database
    region_list = db.get_regions()

    # Create a dictionary of region_name: region_id
    region_dict = {region_name: region_id for region_id, region_name in region_list}
    return region_dict


@st.cache_data
def get_cities():
    """Get cities from the database in a dataframe with region_id,city_id,city_name
    :return: dataframe with region_id as index; city_id,city_name as columns
    """
    city_df = db.get_cities()
    city_df.set_index("region_id", inplace=True)

    return city_df


def get_listings():
    """Get all propertyu listings from the database in a dataframe with region_name, city_name as index
    :return: dataframe with region_name, city_name as index
    """
    logging.info("Getting property listings from the database...")
    df = db.get_listings()

    # set index to region_name and city_name
    df.set_index(["region_name", "city_name"], inplace=True)

    # add price_per_sqm column
    df["price_per_sqm"] = df["price"] / df["lot_area"]

    # add price_eur and price_per_sqm_eur column
    df = add_eur_price(df)
    return df


def initialize():
    logging.info("Initializing values and session state")
    if "set_region" not in st.session_state:
        st.session_state.set_region = False
        st.session_state.region_dict = get_regions()

    if "city_df" not in st.session_state:
        st.session_state.city_df = get_cities()
        st.session_state.city_filtered_list = st.session_state.city_df[
            "city_name"
        ].to_list()

    if "listings_df" not in st.session_state:
        st.session_state.listings_df = get_listings()
        st.session_state.filtered_listings_df = st.session_state.listings_df

    if "currency" not in st.session_state:
        # set the starting currency
        st.session_state.currency = "PHP"

        # set the initial columns to read based on the currency
        st.session_state.price_col = "price"
        st.session_state.price_sqm = "price_per_sqm"


#################################################################
###                     Action Handlers                       ###
#################################################################
def handle_region_change():
    """Enable or disable the city selectbox depending on the region selected.
    Filter the cities based on the selected region.
    """
    if st.session_state.region != -1:
        # to enable city selectbox
        st.session_state.set_region = True

        # filter cities based on the region
        cities = st.session_state.city_df.loc[
            st.session_state.region_dict.get(st.session_state.region)
        ]

        # turn the cities into a list if there are multiple results, else, just return the city name
        st.session_state.city_filtered_list = (
            cities["city_name"].to_list()
            if not isinstance(cities, pd.Series)
            else [cities["city_name"]]
        )
    else:
        # show all cities
        st.session_state.set_region = False
        st.session_state.city_df = get_cities()


def handle_btn_estimate():
    """Handle the estimate button click"""
    # filter listings based on selected city and region
    st.session_state.filtered_listings_df = st.session_state.listings_df.loc[
        (st.session_state.region, st.session_state.city)
    ].sort_values(by=[st.session_state.price_col])


def handle_currency_change():
    logging.info("Handling currency change")
    (
        st.session_state.currency,
        st.session_state.price_col,
        st.session_state.price_sqm,
    ) = update_currency(st.session_state.sel_currency)
    # if st.session_state.sel_currency == "PHP":
    #     st.session_state.currency = "PHP"
    #     st.session_state.price_col = "price"
    #     st.session_state.price_sqm = "price_per_sqm"
    # else:
    #     st.session_state.currency = "EUR"
    #     st.session_state.price_col = "price_eur"
    #     st.session_state.price_sqm = "price_per_sqm_eur"


#################################################################
###                     Main function                         ###
#################################################################
def main():
    initialize()
    st.title("*SPICEstimate* - Philippines House Price Estimator")
    st.markdown("#### Is the Price right? *Enter the details to find out!*")
    st.write(
        "Use SPICEstimate to get an instant home-value estimate and see nearby sales."
    )

    bedrooms, floor_area, lot_area, city, region = st.columns(
        [
            1,
            1.5,
            1.5,
            2,
            2,
        ]
    )
    btn_estimate = st.button("Estimate", on_click=handle_btn_estimate)

    with bedrooms:
        selected_bedrooms = st.selectbox("Bedrooms", db.get_bedrooms())

    with floor_area:
        floor_area_value = st.number_input(
            "Floor Area (sqm)", value=0, format="%d", min_value=0
        )

    with lot_area:
        lot_area_value = st.number_input(
            "Lot Area (sqm)", value=0, format="%d", min_value=0
        )

    with region:
        region_placeholder = "Select a Region"
        selected_region_name = st.selectbox(
            "Region",
            ["-1"] + list(st.session_state.region_dict.keys()),
            index=0,
            format_func=lambda x: region_placeholder if x == "-1" else x,
            on_change=handle_region_change,
            key="region",
        )

    with city:
        city_placeholder = "Select a City"
        selected_city_name = st.selectbox(
            "City",
            # ["-1"] + list(st.session_state.city_df_filtered["city_name"]),
            ["-1"] + st.session_state.city_filtered_list,
            index=0,
            format_func=lambda x: city_placeholder if x == "-1" else x,
            disabled=not st.session_state.set_region,
            key="city",
        )
    with st.container():
        if btn_estimate:
            with st.spinner("Please wait..."):
                time.sleep(2)
            #################################################################
            ###                Display estimated price                    ###
            #################################################################
            logging.info("Estimating price")
            # Get the predicted price
            predicted_price = model.predict_price(
                selected_bedrooms,
                floor_area_value,
                lot_area_value,
                selected_city_name,
                selected_region_name,
            )
            predicted_price = (
                convert_to_eur(predicted_price)
                if st.session_state.currency == "EUR"
                else predicted_price
            )
            # Display the predicted price
            st.markdown(
                f"#### Estimated Price: **{formatPrice(predicted_price,st.session_state.currency)}**"
            )

            with st.container():
                #################################################################
                ###                Display Map of listings                    ###
                #################################################################
                st.markdown("##### Map View of Listings in the area")
                df_map = st.session_state.filtered_listings_df[
                    [
                        "latitude",
                        "longitude",
                        st.session_state.price_col,
                        st.session_state.price_sqm,
                        "link",
                        "title",
                        "img_link",
                    ]
                ]
                # Create a folium map
                m = folium.Map(
                    location=[df_map["latitude"].mean(), df_map["longitude"].mean()],
                    zoom_start=12,
                    width=1000,
                )

                # Create a marker cluster group
                marker_cluster = MarkerCluster().add_to(m)

                # Add markers to the marker cluster
                for index, row in df_map.iterrows():
                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=f"<a href='{row['link']}' target='_blank'>{row['title']}</a>",
                        tooltip=formatPrice(
                            row[st.session_state.price_col], st.session_state.currency
                        ),
                    ).add_to(marker_cluster)

                # Display the folium map using folium_static
                folium_static(m, width=2000, height=600)

            #################################################################
            ###                Display other listings                     ###
            #################################################################
            with st.expander("Listings in the area"):
                st.markdown('<div class="property-listings">', unsafe_allow_html=True)
                # Display each property listing
                for index, row in st.session_state.filtered_listings_df.iterrows():
                    # img_bytes = BytesIO(row["img_bytes"])
                    st.markdown(
                        f'<div class="property-container">'
                        f'<div class="property-image">'
                        f'<img src="{row["img_link"]}" width="100%">'
                        f"</div>"
                        f'<div class="property-details">'
                        f'<strong>Bedrooms:</strong> {row["bedroom"]}<br>'
                        f'<strong>Floor Area (sqm):</strong> {row["floor_area"]}<br>'
                        f'<strong>Lot Area (sqm):</strong> {row["lot_area"]}<br>'
                        f"<strong>Price:</strong> {formatPrice(row[st.session_state.price_col], st.session_state.currency)}<br>"
                        f"<strong>Price per sqm:</strong> {formatPrice(row[st.session_state.price_sqm], st.session_state.currency)}<br>"
                        f'<strong><a href="{row["link"]}">View Listing</a></strong>'
                        f"</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            #################################################################
            ###         Display Price Range in the Location               ###
            #################################################################
            with st.expander("Price range"):
                df_price_range = st.session_state.filtered_listings_df.reset_index()

                ################ Start Plot Price range : Boxplot ################
                fig_price = px.box(
                    df_price_range,
                    x=st.session_state.price_col,
                    y="city_name",
                    orientation="h",
                    title="Price Range in " + st.session_state.currency,
                    height=300,
                    color_discrete_sequence=["#FECB52"],
                )

                fig_price.add_scatter(
                    x=[predicted_price],
                    y=[selected_city_name],
                    mode="markers",
                    marker=dict(size=10, color="red", symbol="circle"),
                    name="Estimated Price",
                )
                # Update y-axis label
                fig_price.update_yaxes(title_text="City")
                fig_price.update_layout(
                    xaxis=dict(showgrid=True), yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_price, use_container_width=True)
                ################ End Plot Price range ################

                ################ Start Plot Price in SQM range : Boxplot ################
                fig_pps = px.box(
                    df_price_range,
                    x=st.session_state.price_sqm,
                    y="city_name",
                    orientation="h",
                    title="Price per sqm in " + st.session_state.currency,
                    height=300,
                    color_discrete_sequence=["#FECB52"],
                )
                estimated_price_per_sqm = predicted_price / lot_area_value

                logging.info(f"estimated_price_per_sqm: {estimated_price_per_sqm}")
                fig_pps.add_scatter(
                    x=[estimated_price_per_sqm],
                    y=[selected_city_name],
                    mode="markers",
                    marker=dict(size=10, color="red", symbol="circle"),
                    name="Estimated Price per sqm",
                )
                # Update y-axis label
                fig_pps.update_yaxes(title_text="City")
                fig_pps.update_layout(
                    xaxis=dict(showgrid=True), yaxis=dict(showgrid=True)
                )
                st.plotly_chart(fig_pps, use_container_width=True)

                ################ End Plot Price in SQM range ################


if __name__ == "__main__":
    main()
    with st.sidebar:
        st.title("SPICEstimate")
        cur_col, _ = st.columns([1, 2])
        # set currency
        with cur_col:
            if "currency" not in st.session_state:
                index_currency = 0
            else:
                index_currency = 0 if st.session_state.currency == "PHP" else 1

            # select currency
            currency = st.selectbox(
                "Currency", ["PHP", "EUR"], index=index_currency, key="sel_currency"
            )
            if currency != st.session_state.currency:
                handle_currency_change()
