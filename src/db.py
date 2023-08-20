import pandas as pd
import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
import logging
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        logger.info("Initializing database")
        self.connection = self.get_connection()
        self.cursor = self.connection.cursor()

    @st.cache_resource
    def get_connection(_self):
        """Get the database connection
        :return: Connection object
        """
        logger.info("Getting database connection")
        # Get database credentials
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_DATABASE")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        # Create a connection to the database
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
        )
        return connection

    @st.cache_data
    def get_bedrooms(_self):
        """Get number of bedrooms
        :return: List of bedrooms
        """
        logger.debug("Getting number of bedrooms...")
        _self.cursor.execute("SELECT DISTINCT bedroom FROM listing ORDER BY bedroom")
        return [row[0] for row in _self.cursor.fetchall()]

    @st.cache_data
    def get_cities(
        _self,
    ):
        """Get cities
        :param region_id: Region id
        :return: List of cities
        """
        logger.info("Getting cities...")
        _self.cursor.execute(
            "SELECT region_id, city_id, city_name FROM city ORDER BY city_name"
        )
        return pd.DataFrame(
            _self.cursor.fetchall(), columns=["region_id", "city_id", "city_name"]
        )

    @st.cache_data
    def get_regions(_self):
        """Get regions
        :return: List of regions
        """
        logger.info("Getting regions...")

        _self.cursor.execute(
            "SELECT region_id,region_name FROM region ORDER BY region_name"
        )

        return [(row[0], row[1]) for row in _self.cursor.fetchall()]

    @st.cache_data
    def get_listings(_self):
        """Get all listings
        :return: List of listings
        """
        df_listings = pd.read_sql_query(
            """SELECT 
                listing_id, 
                title, 
                price, 
                bedroom, 
                floor_area, 
                lot_area, 
                link, 
                city_name, 
                region_name, 
                latitude, 
                longitude,
                img_link
                FROM listing 
                INNER JOIN city ON listing.city_id = city.city_id 
                INNER JOIN region ON listing.region_id = region.region_id
                INNER JOIN geo_point ON listing.geo_point_id = geo_point.geo_point_id""",
            _self.connection,
        )
        return df_listings

    def insert_data(self, df):
        """Insert data into the database
        :param df: DataFrame containing the data to be inserted
        """
        logging.info("Inserting data into the database")

        # Loop through DataFrame rows and insert data into tables
        for index, row in df.iterrows():
            # Insert region into "regions" table
            self.cursor.execute(
                "INSERT INTO region (region_name) VALUES (%s) ON CONFLICT (region_name) DO NOTHING RETURNING region_id",
                (row["Region"],),
            )
            # if cursor.rowcount == 0 then select the region_id
            if self.cursor.rowcount == 0:
                self.cursor.execute(
                    "SELECT region_id FROM region WHERE region_name = %s",
                    (row["Region"],),
                )
            region_id = self.cursor.fetchone()[0]

            # Insert city into "cities" table
            self.cursor.execute(
                "INSERT INTO city (region_id,city_name) VALUES (%s,%s) ON CONFLICT (city_name,region_id) DO NOTHING RETURNING city_id",
                (
                    region_id,
                    row["Town/City"],
                ),
            )
            # if cursor.rowcount == 0 then select the city_id
            if self.cursor.rowcount == 0:
                self.cursor.execute(
                    "SELECT city_id FROM city WHERE city_name = %s", (row["Town/City"],)
                )
            city_id = self.cursor.fetchone()[0]

            # Insert geo_points to "geo_point" table
            self.cursor.execute(
                "INSERT INTO geo_point (latitude, longitude) VALUES (%s, %s) RETURNING geo_point_id",
                (row["Latitude"], row["Longitude"]),
            )
            geo_point_id = self.cursor.fetchone()[0]

            # get image bytes from url

            # Insert property listing into "listings" table with region_id and city_id
            self.cursor.execute(
                """INSERT INTO listing (
                    title, 
                    price, 
                    bedroom, 
                    floor_area, 
                    lot_area, 
                    link, 
                    region_id, 
                    city_id, 
                    geo_point_id,
                    img_link,
                    img_bytes
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    row["Title"],
                    row["Price"],
                    row["Bedrooms"],
                    row["Floor Area"],
                    row["Lot Area"],
                    row["URL"],
                    region_id,
                    city_id,
                    geo_point_id,
                    row["Image Link"],
                    row["img_bytes"],
                ),
            )

            # Commit the transaction
            self.connection.commit()
            logging.info("Data inserted successfully")

        def close_connection(self):
            """Close the database connection"""
            self.cursor.close()
            self.connection.close()

        def __del__(self):
            """Destructor"""
            logging.info("Closing database connection")
            self.close_connection()
