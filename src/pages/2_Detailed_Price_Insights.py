import streamlit as st
import plotly.express as px
import logging

# from utils import update_currency
from Home import handle_currency_change


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

    region_tab, city_tab = st.tabs(["Region", "City"])

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
