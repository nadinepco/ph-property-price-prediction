import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

sns.set(style="whitegrid")


def main():
    st.title("Properties Insights in the Philippines")
    df = st.session_state.listings_df
    df.reset_index(inplace=True)
    df["price_per_sqm"] = df["price"] / df["lot_area"]

    # TODO: Chloropleth map
    # # Plot 3: Price vs Lot Area
    # fig3, ax = plt.subplots(figsize=(10, 6))
    # sns.scatterplot(data=df, x="lot_area", y="price")
    # plt.title("Price vs Lot Area")
    # plt.xlabel("Lot Area")
    # plt.ylabel("Price")
    # st.pyplot(fig3)

    # # Plot 4: Price vs Bedrooms
    # fig4, ax = plt.subplots(figsize=(10, 6))
    # sns.boxplot(data=df, x="price", y="bedroom", orient="h")
    # plt.title("Bedrooms vs Price")
    # plt.xlabel("Price")
    # plt.ylabel("Bedrooms")
    # st.pyplot(fig4)

    # with st.container():
    #     regions = sorted(df["region_name"].unique())
    #     your_region = st.selectbox("Select a region", regions)
    #     fig, ax = plt.subplots(figsize=(10, 6))

    #     selected_region = df[df["region_name"] == your_region]
    #     other_regions = df[df["region_name"] != your_region]

    #     # Background
    #     sns.stripplot(
    #         data=other_regions,
    #         y="price_per_sqm",
    #         color="white",
    #         jitter=0.85,
    #         size=8,
    #         linewidth=1,
    #         edgecolor="gainsboro",
    #         alpha=0.7,
    #     )
    #     # Selected region
    #     sns.stripplot(
    #         data=selected_region,
    #         y="price_per_sqm",
    #         color="#00FF7F",
    #         jitter=0.15,
    #         size=12,
    #         linewidth=1,
    #         edgecolor="k",
    #         label="f",
    #     )

    #     # Showing up position measure
    #     avg_price_m2 = df["price_per_sqm"].median()
    #     q1_price_m2 = np.percentile(df["price_per_sqm"], 25)
    #     q3_price_m2 = np.percentile(df["price_per_sqm"], 75)

    #     # Plotting lines
    #     plt.axhline(y=avg_price_m2, linestyle="--", color="#DA70D6", lw=0.75)
    #     plt.axhline(y=q1_price_m2, linestyle="--", color="white", lw=0.75)
    #     plt.axhline(y=q3_price_m2, linestyle="--", color="white", lw=0.75)

    #     # Adding the labels for position measures
    #     ax.text(
    #         1.15,
    #         q1_price_m2,
    #         "Q1",
    #         color="white",
    #         fontsize=8,
    #         ha="center",
    #         va="center",
    #         fontweight="bold",
    #     )
    #     ax.text(
    #         1.35,
    #         avg_price_m2,
    #         "Median",
    #         color="#DA70D6",
    #         fontsize=8,
    #         ha="center",
    #         va="center",
    #         fontweight="bold",
    #     )
    #     ax.text(
    #         1.15,
    #         q3_price_m2,
    #         "Q3",
    #         color="white",
    #         fontsize=8,
    #         ha="center",
    #         va="center",
    #         fontweight="bold",
    #     )

    #     # to fill the area between the lines
    #     ax.fill_between([q1_price_m2, q3_price_m2], -2, 1, alpha=0.2, color="gray")

    #     # set the x-axis limits to show the full range of the data
    #     ax.set_xlim(-1, 1)

    #     # Axes and titles
    #     plt.xticks([])
    #     plt.ylabel("Price per sqm")
    #     plt.legend(
    #         loc="center",
    #         bbox_to_anchor=(0.5, -0.1),
    #         ncol=2,
    #         framealpha=0,
    #         labelcolor="#00FF7F",
    #     )
    #     plt.title(
    #         "Price per sqm by region",
    #         weight="bold",
    #         loc="center",
    #         pad=15,
    #         color="gainsboro",
    #     )
    #     plt.tight_layout()
    #     st.pyplot(fig)

    # # Plot 5: Price vs Region
    with st.expander("Price vs Region"):
        fig5, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df, x="region_name", y="price_per_sqm")
        plt.title("Price vs Region")
        plt.xlabel("Region")
        plt.ylabel("Price")
        st.pyplot(fig5)

    # # # Plot 6: Price vs City
    with st.expander("Price vs City"):
        fig6, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df, x="city_name", y="price_per_sqm")
        plt.title("Price vs City")
        plt.xlabel("City")
        plt.ylabel("Price")
        plt.xticks(rotation=90)
        st.pyplot(fig6)

    # # Plotly Plot: Interactive scatter plot
    with st.expander("Floor Area vs Lot Area by Price and Region"):
        fig7 = px.scatter(
            df,
            x="floor_area",
            y="lot_area",
            size="price_per_sqm",
            color="region_name",
            hover_name="city_name",
            log_x=True,
            log_y=True,
            title="Floor Area vs Lot Area by Price and Region",
        )
        st.plotly_chart(fig7)

    with st.expander("Scattermap with Color-coded Markers by city_name"):
        # # Create scattermap with color-coded markers for each town/city within a region
        fig9 = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            color="city_name",
            hover_name="city_name",
            size="price",
            zoom=10,
            center={"lat": df["latitude"].mean(), "lon": df["longitude"].mean()},
            mapbox_style="carto-positron",
            title="Scattermap with Color-coded Markers by city_name",
        )

        # Add a heatmap layer based on the price per location
        fig9.add_densitymapbox(
            lat=df["latitude"],
            lon=df["longitude"],
            z=df["price"],
            radius=15,
            colorscale="Viridis",
            showscale=False,
        )

        # Show the plot
        fig9.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig9)


if __name__ == "__main__":
    main()
