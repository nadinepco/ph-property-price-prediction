import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import geopandas as gpd
import logging
from utils import update_currency
from Home import handle_currency_change

sns.set(style="whitegrid")


@st.cache_data
def session_state_listings():
    df = st.session_state.listings_df.copy()
    df.reset_index(inplace=True)
    df["price_per_sqm"] = df["price"] / df["lot_area"]
    return df


# def handle_currency_change():
#     logging.info("Handling currency change")
#     (
#         st.session_state.currency,
#         st.session_state.price_col,
#         st.session_state.price_sqm,
#     ) = update_currency(st.session_state.sel_currency)


def main():
    df = session_state_listings()
    st.title("Property Prices in the Philippines Overview")

    with st.container():
        col_price_avg, col_price_sqm_avg = st.columns(2)

        with col_price_avg:
            # average price per region
            median_price_per_region = (
                df.groupby("region_name")[st.session_state.price_col]
                .median()
                .reset_index()
            )

            # Create the initial bar chart for average prices per region
            region_fig = px.bar(
                median_price_per_region,
                x="region_name",
                y=st.session_state.price_col,
                title="Median Prices by Region",
                width=550,
            )
            region_fig.update_yaxes(title_text="Price in " + st.session_state.currency)
            region_fig.update_xaxes(title_text="Region")
            st.plotly_chart(region_fig)

        with col_price_sqm_avg:
            # average price per region
            median_price_per_sqm_region = (
                df.groupby("region_name")[st.session_state.price_sqm]
                .median()
                .reset_index()
            )

            # Create the initial bar chart for average prices per region
            region_fig2 = px.bar(
                median_price_per_sqm_region,
                x="region_name",
                y=st.session_state.price_sqm,
                title="Median Prices per sqm by Region",
                width=550,
            )
            region_fig2.update_yaxes(title_text="Price in " + st.session_state.currency)
            region_fig2.update_xaxes(title_text="Region")
            st.plotly_chart(region_fig2)

    selectbox_city_avg_price = st.selectbox(
        "Select a Region",
        ["Select a Region"] + median_price_per_region["region_name"].tolist(),
        index=0,
    )

    with st.container():
        col_city_price_avg, col_city_price_sqm_avg = st.columns(2)

        if selectbox_city_avg_price != "Select a Region":
            city_data = df[df["region_name"] == selectbox_city_avg_price]
            with col_city_price_avg:
                median_price_per_city = (
                    city_data.groupby("city_name")[st.session_state.price_col]
                    .median()
                    .reset_index()
                )
                # Display the bar chart for average prices per city in the selected region
                city_fig = px.bar(
                    median_price_per_city,
                    x="city_name",
                    y=st.session_state.price_col,
                    title=f"Median Prices in {selectbox_city_avg_price}",
                    width=550,
                )
                city_fig.update_yaxes(
                    title_text="Price in " + st.session_state.currency
                )
                city_fig.update_xaxes(title_text="City")
                st.plotly_chart(city_fig)

            with col_city_price_sqm_avg:
                median_price_sqm_per_city = (
                    city_data.groupby("city_name")[st.session_state.price_sqm]
                    .median()
                    .reset_index()
                )
                # Display the bar chart for average prices per sqm per city in the selected region
                city_fig2 = px.bar(
                    median_price_sqm_per_city,
                    x="city_name",
                    y=st.session_state.price_sqm,
                    title=f"Median Prices per sqm in {selectbox_city_avg_price}",
                    width=550,
                )
                city_fig2.update_yaxes(
                    title_text="Price in " + st.session_state.currency
                )
                city_fig2.update_xaxes(title_text="City")
                st.plotly_chart(city_fig2)


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
                st.experimental_rerun()
