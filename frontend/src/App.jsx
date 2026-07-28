import { useState } from 'react';

const brands = [
  'Maruti','Skoda','Honda','Hyundai','Toyota','Ford','Renault','Mahindra','Tata','Chevrolet','Datsun','Jeep','Mercedes-Benz','Mitsubishi','Audi','Volkswagen','BMW','Nissan','Lexus','Jaguar','Land','MG','Volvo','Daewoo','Kia','Fiat','Force','Ambassador','Ashok','Isuzu','Opel'
];

const fuelTypes = ['Diesel','Petrol','LPG','CNG'];
const sellerTypes = ['Individual','Dealer','Trustmark Dealer'];
const transmissions = ['Manual','Automatic'];
const owners = ['First Owner','Second Owner','Third Owner','Fourth & Above Owner','Test Drive Car'];

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData(event.currentTarget);
    const payload = Object.fromEntries(formData.entries());

    payload.year = Number(payload.year);
    payload.km_driven = Number(payload.km_driven);
    payload.mileage = Number(payload.mileage);
    payload.engine = Number(payload.engine);
    payload.max_power = Number(payload.max_power);
    payload.seats = Number(payload.seats);

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Prediction failed');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-shell">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">AI-powered valuation</p>
          <h1>Estimate your car value with confidence.</h1>
          <p>Use the trained regression model to get a realistic price estimate for your vehicle in seconds.</p>
        </div>

        <form className="form-card" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Brand
              <select name="brand" defaultValue="Honda">
                {brands.map((brand) => <option key={brand} value={brand}>{brand}</option>)}
              </select>
            </label>
            <label>
              Year
              <input type="number" name="year" min="1994" max="2026" defaultValue="2020" />
            </label>
            <label>
              Kilometers Driven
              <input type="number" name="km_driven" min="0" max="300000" defaultValue="30000" />
            </label>
            <label>
              Fuel
              <select name="fuel" defaultValue="Petrol">
                {fuelTypes.map((fuel) => <option key={fuel} value={fuel}>{fuel}</option>)}
              </select>
            </label>
            <label>
              Seller Type
              <select name="seller_type" defaultValue="Dealer">
                {sellerTypes.map((seller) => <option key={seller} value={seller}>{seller}</option>)}
              </select>
            </label>
            <label>
              Transmission
              <select name="transmission" defaultValue="Manual">
                {transmissions.map((transmission) => <option key={transmission} value={transmission}>{transmission}</option>)}
              </select>
            </label>
            <label>
              Owner
              <select name="owner" defaultValue="First Owner">
                {owners.map((owner) => <option key={owner} value={owner}>{owner}</option>)}
              </select>
            </label>
            <label>
              Seats
              <input type="number" name="seats" min="2" max="10" defaultValue="5" />
            </label>
            <label>
              Mileage (kmpl)
              <input type="number" step="0.1" name="mileage" min="5" max="40" defaultValue="18" />
            </label>
            <label>
              Engine (CC)
              <input type="number" name="engine" min="700" max="5000" defaultValue="1400" />
            </label>
            <label>
              Max Power (bhp)
              <input type="number" step="0.1" name="max_power" min="40" max="250" defaultValue="90" />
            </label>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Predicting...' : 'Predict Price'}
          </button>

          {result && (
            <div className="result-box">
              <h3>Estimated Price</h3>
              <p className="price">₹{result.price.toLocaleString('en-IN')}</p>
              <span>{result.message}</span>
            </div>
          )}

          {error && <div className="error-box">{error}</div>}
        </form>
      </section>
    </div>
  );
}

export default App;
