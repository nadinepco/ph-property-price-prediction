import streamlit as st

# Set page config
st.set_page_config(
    page_title="SPICEstimate",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

from db import Database
from model import HousePricePredictor
from PIL import Image
from io import BytesIO
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from folium import IFrame
from streamlit_folium import folium_static
from matplotlib.ticker import FuncFormatter
import requests
import logging
from utils import formatPrice
import warnings

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)


# initialize values
model_path = "../models/rf_model.pkl"
db = Database()
model = HousePricePredictor(model_path)

# Define CSS to style the property container
st.markdown(
    """
    <style>
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
# border: 1px solid #e0e0e0;
#         border-radius: 5px;
# max-height: 300px; /* Set the maximum height for the content */
#         overflow-y: auto; /* Enable vertical scrolling */


@st.cache_data
def get_regions():
    # Get a list of city tuples (city_id, city_name) from the database
    region_list = db.get_regions()

    # Create a dictionary of city_name: city_id
    region_dict = {region_name: region_id for region_id, region_name in region_list}
    return region_dict


@st.cache_data
def get_cities():
    # Get a list of city tuples (city_id, city_name) from the database
    city_df = db.get_cities()
    city_df.set_index("region_id", inplace=True)

    return city_df


def initialize():
    logging.info("Initializing values and session state")
    if "set_region" not in st.session_state:
        st.session_state.set_region = False
        st.session_state.region_dict = get_regions()
    if "city_df" not in st.session_state:
        st.session_state.city_df = get_cities()
        st.session_state.city_df_filtered = st.session_state.city_df
    if "listings_df" not in st.session_state:
        st.session_state.listings_df = db.get_listings()
        st.session_state.listings_df.set_index(
            ["region_name", "city_name"], inplace=True
        )
    if "currency" not in st.session_state:
        st.session_state.currency = "PHP"


########## action handlers ##########
def handle_region_change():
    """Enable or disable the city selectbox depending on the region selected.
    Filter the cities based on the selected region.
    """
    if st.session_state.region != -1:
        # filter cities based on selected region
        st.session_state.set_region = True
        st.session_state.city_df_filtered = st.session_state.city_df.loc[
            st.session_state.region_dict.get(st.session_state.region)
        ]
    else:
        # show all cities
        st.session_state.set_region = False
        st.session_state.city_df = get_cities()


def handle_btn_estimate():
    # show listings based on selected city and region
    st.session_state.filtered_listings_df = st.session_state.listings_df.loc[
        (st.session_state.region, st.session_state.city)
    ]


def handle_currency_change():
    if st.session_state.sel_currency == "PHP":
        st.session_state.currency = "PHP"
    else:
        st.session_state.currency = "EUR"


def main():
    initialize()

    st.title("House Price Estimator")
    st.markdown("#### How much should it cost?")
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
        floor_area_value = st.number_input("Floor Area (sqm)", value=0, format="%d")

    with lot_area:
        lot_area_value = st.number_input("Lot Area (sqm)", value=0, format="%d")

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
            ["-1"] + list(st.session_state.city_df_filtered["city_name"]),
            index=0,
            format_func=lambda x: city_placeholder if x == "-1" else x,
            disabled=not st.session_state.set_region,
            key="city",
        )
    with st.container():
        if btn_estimate:
            logging.info("Estimating price")
            # Get the predicted price
            predicted_price = model.predict_price(
                selected_bedrooms,
                floor_area_value,
                lot_area_value,
                selected_city_name,
                selected_region_name,
            )
            # Display the predicted price
            st.markdown(f"#### Estimated Price: **{formatPrice(predicted_price)}**")

            with st.container():
                st.markdown("#### Nearby Listings")
                df_map = st.session_state.filtered_listings_df[
                    ["latitude", "longitude", "price", "link", "title", "img_link"]
                ]
                # Create a folium map
                m = folium.Map(
                    location=[df_map["latitude"].mean(), df_map["longitude"].mean()],
                    zoom_start=12,
                )

                # Add clickable markers to the map
                for index, row in df_map.iterrows():
                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=f"<a href='{row['link']}' target='_blank'>{row['title']}</a>",
                        tooltip=formatPrice(row["price"]),
                    ).add_to(m)

                # Display the folium map using folium_static
                folium_static(m)

            with st.expander("Listings in the area"):
                # sort by price
                st.session_state.filtered_listings_df.sort_values(
                    by=["price"], inplace=True
                )
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
                        f'<strong>Price:</strong> {formatPrice(row["price"])}<br>'
                        f'<strong><a href="{row["link"]}">View Listing</a></strong>'
                        f"</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            with st.expander("Price range"):
                # # Calculate mean, max, and min prices by town/city and region
                agg_df = (
                    st.session_state.filtered_listings_df.groupby(["city_name"])[
                        "price"
                    ]
                    .agg(["mean", "max", "min"])
                    .reset_index()
                )

                # Plot: Mean, Max, Min Prices by city_name within Region
                fig, ax = plt.subplots(figsize=(10, 2))
                df_price_range = st.session_state.filtered_listings_df.reset_index()
                sns.boxplot(data=df_price_range, x="price", y="city_name", orient="h")
                formatter = FuncFormatter(lambda x, pos: "{:,}".format(int(x)))
                ax.xaxis.set_major_formatter(formatter)
                # sns.barplot(
                #     data=agg_df,
                #     x="city_name",
                #     y="mean",
                #     color="blue",
                #     label="Avg Price",
                # )
                # sns.barplot(
                #     data=agg_df,
                #     x="city_name",
                #     y="min",
                #     color="green",
                #     label="Min Price",
                # )
                # sns.barplot(
                #     data=agg_df,
                #     x="city_name",
                #     y="max",
                #     color="red",
                #     label="Max Price",
                # )
                plt.title("Price Range")
                plt.xlabel("Price")
                plt.ylabel("City")
                plt.xticks(rotation=45)
                # plt.legend()
                st.pyplot(fig)

                # # Display the barplot using st.pyplot()
                # st.pyplot(fig)
                # fig8, ax = plt.subplots(figsize=(12, 6))
                # sns.barplot(data=agg_df, x="city_name", y="mean", hue="region_name")
                # plt.title("Mean, Max, Min Prices by city_name within Region")
                # plt.xlabel("city_name")
                # plt.ylabel("Price")
                # plt.xticks(rotation=45)
                # st.pyplot(fig8)

            # Display nearby listings
            # img_link, listing_details = st.columns([3, 2])
            # for index, row in st.session_state.filtered_listings_df.iterrows():
            #     with st.container():
            #         with img_link:
            #             img_bytes = BytesIO(row["img_bytes"])
            #             # response = requests.get(row["img_link"])
            #             # img_bytes = (
            #             #     BytesIO(response.content)
            #             #     if response.status_code == 200
            #             #     else None
            #             # )
            #             # img_bytes
            #             st.image(Image.open(img_bytes), use_column_width=True)
            #         with listing_details:
            #             # st.markdown(
            #             #     f'<div class="property-details">'
            #             #     f'<strong>Bedrooms:</strong> {row["bedroom"]}<br>'
            #             #     f'<strong>Floor Area (sqm):</strong> {row["floor_area"]}<br>'
            #             #     f'<strong>Lot Area (sqm):</strong> {row["lot_area"]}<br>'
            #             #     f'<strong>Price:</strong> {formatPrice(row["price"])}<br>'
            #             #     f'<strong><a href="{row["link"]}">View Listing</a></strong>'
            #             #     f"</div>",
            #             #     unsafe_allow_html=True,
            #             # )
            #             st.write(f"**Bedrooms:** {row['bedroom']}")
            #             st.write(f"**Floor Area:** {row['floor_area']} sqm")
            #             st.write(f"**Lot Area:** {row['lot_area']} sqm")
            #             st.write(f"**Price:** {formatPrice(row['price'])}")
            #             st.write(f"**Link:** [View Listing]({row['link']})")
            #         st.write("---")
            # st.session_state.filtered_listings_df


if __name__ == "__main__":
    main()
    with st.sidebar:
        st.title("SPICEstimate")
        # convert currency
        # st.radio("Currency", ["PHP", "EUR"],)
        cur_col, _ = st.columns([1, 2])
        with cur_col:
            currency = st.selectbox(
                "Currency", ["PHP", "EUR"], index=0, key="sel_currency"
            )
