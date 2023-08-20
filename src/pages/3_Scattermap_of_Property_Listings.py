import streamlit as st
import plotly.express as px
import logging
from Home import handle_currency_change

# from utils import update_currency


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
    st.title("Scattermap of Property Listings")
    st.write(
        """This page shows the location of the property listings. 
             The bigger circle markers represent higher price per sqm.
             Hover over the markers to see the details."""
    )
    # # Create scattermap with color-coded markers for each town/city within a region
    scattermap = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="city_name",
        hover_name="city_name",
        size=st.session_state.price_sqm,
        zoom=10,
        center={"lat": df["latitude"].mean(), "lon": df["longitude"].mean()},
        mapbox_style="carto-positron",
        # title="Scattermap with Color-coded Markers by city_name",
        width=1000,
        height=600,
    )

    # Add a heatmap layer based on the price per location
    scattermap.add_densitymapbox(
        lat=df["latitude"],
        lon=df["longitude"],
        z=df[st.session_state.price_sqm],
        radius=15,
        colorscale="Viridis",
        showscale=False,
    )

    # Show the plot
    scattermap.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(scattermap)


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
