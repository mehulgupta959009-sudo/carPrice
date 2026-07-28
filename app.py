from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import numpy as np
import pickle
import os

app = Flask(__name__)

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


brands = sorted(brand_mapping.keys())
fuel_types = ['Diesel', 'Petrol', 'LPG', 'CNG']
seller_types = ['Individual', 'Dealer', 'Trustmark Dealer']
transmissions = ['Manual', 'Automatic']
owners = ['First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner', 'Test Drive Car']

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CarPrice AI</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Arial, sans-serif;
      background: linear-gradient(135deg, #07111f, #10253b 55%, #15314d);
      color: #eef6ff;
      min-height: 100vh;
    }
    .page { max-width: 1100px; margin: 0 auto; padding: 32px 20px 60px; }
    .hero {
      display: grid; gap: 24px; grid-template-columns: 1.2fr 0.8fr; align-items: center;
      background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);
      border-radius: 24px; padding: 28px; backdrop-filter: blur(14px);
      box-shadow: 0 16px 40px rgba(0,0,0,0.25);
    }
    .badge { display: inline-block; padding: 8px 12px; border-radius: 999px; background: #1f7a8c; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; }
    h1 { font-size: 2.3rem; margin: 10px 0 12px; }
    p { line-height: 1.6; color: #dce9f5; }
    .card { background: rgba(8, 18, 32, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 24px; }
    form { display: grid; gap: 16px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 14px; }
    label { font-size: 0.95rem; color: #c8d8e7; }
    select, input { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid #36526b; background: #0f1f2f; color: white; }
    button { padding: 13px 16px; border: 0; border-radius: 12px; background: linear-gradient(90deg, #2cb1c9, #4f6df5); color: white; font-weight: 700; cursor: pointer; }
    .result { margin-top: 18px; padding: 16px; border-radius: 14px; background: rgba(44,177,201,0.15); border: 1px solid rgba(44,177,201,0.35); }
    .meta { font-size: 0.9rem; color: #a7bed5; margin-top: 8px; }
    @media (max-width: 800px) { .hero { grid-template-columns: 1fr; } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div>
        <span class="badge">AI-powered valuation</span>
        <h1>Estimate your car’s market value in seconds.</h1>
        <p>Our model combines real-world vehicle data to give you a fast, professional price estimate for your next car decision.</p>
      </div>
      <div class="card">
        <form id="predict-form">
          <div class="grid">
            <div><label>Brand</label><select name="brand">{% for brand in brands %}<option value="{{ brand }}">{{ brand }}</option>{% endfor %}</select></div>
            <div><label>Year</label><input type="number" name="year" min="1994" max="2026" value="2020" /></div>
            <div><label>Kilometers Driven</label><input type="number" name="km_driven" min="0" max="300000" value="30000" /></div>
            <div><label>Fuel</label><select name="fuel">{% for fuel in fuel_types %}<option value="{{ fuel }}">{{ fuel }}</option>{% endfor %}</select></div>
            <div><label>Seller Type</label><select name="seller_type">{% for seller in seller_types %}<option value="{{ seller }}">{{ seller }}</option>{% endfor %}</select></div>
            <div><label>Transmission</label><select name="transmission">{% for transmission in transmissions %}<option value="{{ transmission }}">{{ transmission }}</option>{% endfor %}</select></div>
            <div><label>Owner</label><select name="owner">{% for owner in owners %}<option value="{{ owner }}">{{ owner }}</option>{% endfor %}</select></div>
            <div><label>Seats</label><input type="number" name="seats" min="2" max="10" value="5" /></div>
            <div><label>Mileage (kmpl)</label><input type="number" step="0.1" name="mileage" min="5" max="40" value="18" /></div>
            <div><label>Engine (CC)</label><input type="number" name="engine" min="700" max="5000" value="1400" /></div>
            <div><label>Max Power (bhp)</label><input type="number" step="0.1" name="max_power" min="40" max="250" value="90" /></div>
          </div>
          <button type="submit">Predict Price</button>
        </form>
        <div id="result" class="result" style="display:none"></div>
      </div>
    </section>
  </div>
  <script>
    const form = document.getElementById('predict-form');
    const result = document.getElementById('result');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = new FormData(form);
      const payload = Object.fromEntries(data.entries());
      result.style.display = 'block';
      result.innerHTML = 'Generating estimate...';
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const json = await response.json();
      result.innerHTML = `<strong>Estimated Price:</strong> ₹${json.price.toLocaleString('en-IN')}<br><span class="meta">${json.message}</span>`;
    });
  </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, brands=brands, fuel_types=fuel_types, seller_types=seller_types, transmissions=transmissions, owners=owners)


@app.route('/api/predict', methods=['POST'])
def predict():
    payload = request.get_json()

    try:
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

        prediction = float(model.predict(input_df[feature_names])[0])
        return jsonify({
            'price': round(prediction, 2),
            'message': 'This estimate is generated from your selected vehicle profile.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))