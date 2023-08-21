import streamlit as st
import plotly.express as px
import logging
from Home import handle_currency_change, initialize
import pandas as pd

# Set page config
st.set_page_config(
    page_title="SPICEstimate",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def session_state_listings():
    df = st.session_state.listings_df.copy()
    df.reset_index(inplace=True)
    df["price_per_sqm"] = df["price"] / df["lot_area"]
    return df


def main():
    df = session_state_listings()
    logging.info(df.columns)
    logging.info(st.session_state.price_sqm)
    st.title("Detailed Price Insights")

    region_tab, city_tab, summary_tab = st.tabs(
        ["Region", "City", "Highest/Lowest Priced Locations"]
    )

    with region_tab:
        region_fig = px.box(
            df,
            x="region_name",
            y=st.session_state.price_col,
            title="Price Distribution by Region",
            width=1000,
            height=600,
            color="region_name",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        region_fig.update_yaxes(title_text="Price in " + st.session_state.currency)
        region_fig.update_xaxes(title_text="Region")
        st.plotly_chart(region_fig)

        region_fig2 = px.box(
            df,
            x="region_name",
            y=st.session_state.price_sqm,
            title="Price per sqm Distribution by Region",
            width=1000,
            height=600,
            color="region_name",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        region_fig2.update_yaxes(title_text="Price in " + st.session_state.currency)
        region_fig2.update_xaxes(title_text="Region")
        st.plotly_chart(region_fig2)

    with city_tab:
        city_fig = px.box(
            df,
            x="city_name",
            y=st.session_state.price_col,
            title="Price Distribution by City",
            width=1000,
            height=600,
            color="city_name",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        city_fig.update_yaxes(title_text="Price in " + st.session_state.currency)
        city_fig.update_xaxes(title_text="City")
        st.plotly_chart(city_fig)

        city_fig2 = px.box(
            df,
            x="city_name",
            y=st.session_state.price_sqm,
            title="Price per sqm Distribution by City",
            width=1000,
            height=600,
            color="city_name",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        city_fig2.update_yaxes(title_text="Price in " + st.session_state.currency)
        city_fig2.update_xaxes(title_text="City")
        st.plotly_chart(city_fig2)

    with summary_tab:
        # Display top 5 highest priced locations grouped by region and city
        median_price_per_location = df.groupby(["region_name", "city_name"])[
            st.session_state.price_sqm
        ].mean()

        highest_priced_locations = median_price_per_location.sort_values(
            ascending=False
        ).head(5)

        lowest_priced_locations = median_price_per_location.sort_values(
            ascending=True
        ).head(5)

        # Create a DataFrame for the box plot data
        boxplot_data_highest = []
        for region, city in highest_priced_locations.index:
            town_region_data = df[
                (df["city_name"] == city) & (df["region_name"] == region)
            ][st.session_state.price_sqm]
            # town_region_data
            boxplot_data_highest.append(
                {
                    "Location": f"{city}, {region}",
                    "Price per sqm": town_region_data.values.tolist(),
                }
            )

        boxplot_df_highest = pd.DataFrame(boxplot_data_highest).explode("Price per sqm")

        # Create the box plot using Plotly Express
        highest_priced_fig = px.box(
            boxplot_df_highest,
            x="Location",
            y="Price per sqm",
            title="Top 5 Locations with Highest Price per sqm",
            width=1000,
            height=600,
            color="Location",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )

        # Update the layout
        highest_priced_fig.update_layout(
            xaxis_title="Location", yaxis_title="Price per sqm", xaxis_tickangle=-45
        )
        st.plotly_chart(highest_priced_fig)

        ############# lowest priced locations #############
        # Create a DataFrame for the box plot data
        boxplot_data_lowest = []
        for region, city in lowest_priced_locations.index:
            town_region_data = df[
                (df["city_name"] == city) & (df["region_name"] == region)
            ][st.session_state.price_sqm]
            # town_region_data
            boxplot_data_lowest.append(
                {
                    "Location": f"{city}, {region}",
                    "Price per sqm": town_region_data.values.tolist(),
                }
            )

        boxplot_df_lowest = pd.DataFrame(boxplot_data_lowest).explode("Price per sqm")

        # Create the box plot using Plotly Express
        lowest_priced_fig = px.box(
            boxplot_df_lowest,
            x="Location",
            y="Price per sqm",
            title="Top 5 Locations with Lowest Price per sqm",
            width=1000,
            height=600,
            color="Location",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )

        # Update the layout
        lowest_priced_fig.update_layout(
            xaxis_title="Location", yaxis_title="Price per sqm", xaxis_tickangle=-45
        )
        st.plotly_chart(lowest_priced_fig)


if __name__ == "__main__":
    initialize()
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
