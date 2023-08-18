import pickle
import streamlit as st
import logging
import pandas as pd
import numpy as np


class HousePricePredictor:
    def __init__(self, model_path):
        logging.info("Initializing model")
        self.model = self.get_model(model_path)

    @st.cache_resource
    def get_model(_self, model_path):
        logging.info("Getting model")
        with open(model_path, "rb") as model_path:
            model = pickle.load(model_path)
        return model

    def predict_price(self, bedrooms, floor_area, lot_area, city, region):
        # Perform any necessary preprocessing on input features
        # For example, you might need to convert categorical variables to numerical format
        # Implement any other preprocessing steps needed

        # Prepare the input features for prediction
        input_features = [[floor_area, lot_area, city, region, bedrooms]]
        logging.info(f"Input features: {input_features}")
        input_df = pd.DataFrame(
            input_features,
            columns=["Floor Area", "Lot Area", "Town/City", "Region", "Bedrooms"],
        )

        # Make the prediction using your model
        predicted_price_log = self.model.predict(input_df)

        predicted_price = np.exp(predicted_price_log) - 1
        logging.info(f"Predicted price: {predicted_price[0]}")
        return predicted_price[0].astype(int)

    # You can add more methods here as needed for model evaluation, feature importance, etc.
