from db import Database
import pandas as pd
import requests
from io import BytesIO

# to import path from src
import sys

sys.path.append("../src")

db = Database()
# read csv file
df = pd.read_csv("../data/csv/cleaned_data.csv")

# loop through each row
for index, row in df.iterrows():
    # get the image url
    img_url = row["Image Link"]
    # get the image
    img = requests.get(img_url).content
    print(img)
    # convert image to bytes
    # img_bytes = BytesIO(img)
    # add new column to dataframe
    df.loc[index, "img_bytes"] = img

# insert data into database
db.insert_data(df)
