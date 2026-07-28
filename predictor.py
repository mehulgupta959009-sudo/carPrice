import os
import pickle
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')

with open(MODEL_PATH, 'rb') as f:
    artifact = pickle.load(f)

model = artifact['model']
brand_mapping = artifact['brand_mapping']
fuel_mapping = artifact['fuel_mapping']
seller_mapping = artifact['seller_mapping']
transmission_mapping = artifact['transmission_mapping']
owner_mapping = artifact['owner_mapping']
feature_names = artifact['features']


def clean_brand_name(name: str) -> str:
    return str(name).split()[0].strip()


def predict_price(payload: dict) -> float:
    input_df = pd.DataFrame([{
        'name': payload.get('brand', 'Maruti'),
        'year': int(payload.get('year', 2020)),
        'km_driven': int(payload.get('km_driven', 30000)),
        'fuel': payload.get('fuel', 'Petrol'),
        'seller_type': payload.get('seller_type', 'Individual'),
        'transmission': payload.get('transmission', 'Manual'),
        'owner': payload.get('owner', 'First Owner'),
        'mileage': float(payload.get('mileage', 18.0)),
        'engine': float(payload.get('engine', 1400)),
        'max_power': float(payload.get('max_power', 90)),
        'seats': float(payload.get('seats', 5)),
    }])

    input_df['name'] = input_df['name'].apply(clean_brand_name)
    input_df['name'] = input_df['name'].map(brand_mapping)
    input_df['fuel'] = input_df['fuel'].map(fuel_mapping)
    input_df['seller_type'] = input_df['seller_type'].map(seller_mapping)
    input_df['transmission'] = input_df['transmission'].map(transmission_mapping)
    input_df['owner'] = input_df['owner'].map(owner_mapping)

    return float(model.predict(input_df[feature_names])[0])
