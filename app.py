from flask import Flask, request, render_template_string
from REAItools import PropertyDeal, StrategyType, underwrite_deal_with_ai

app = Flask(__name__)

FORM_HTML = """
<!doctype html>
<html>
  <head>
    <title>Paris Properties – Deal Underwriter</title>
    <style>
      body { font-family: -apple-system, Arial, sans-serif; max-width: 800px; margin: 40px auto; }
      label { display:block; margin-top:10px; }
      input { width:100%; padding:6px; margin-top:4px; }
      button { margin-top:15px; padding:8px 16px; }
      pre { background:#f4f4f4; padding:10px; white-space:pre-wrap; }
    </style>
  </head>
  <body>
    <h1>Deal Underwriter</h1>
    <form method="post">
      <label>Address
        <input name="address" required>
      </label>
      <label>City
        <input name="city" value="Gastonia" required>
      </label>
      <label>State
        <input name="state" value="NC" required>
      </label>
      <label>ZIP
        <input name="zip_code" value="28052" required>
      </label>
      <label>Bedrooms (total across all units)
        <input name="bedrooms" type="number" value="6">
      </label>
      <label>Bathrooms (total)
        <input name="bathrooms" type="number" step="0.5" value="3">
      </label>
      <label>Units
        <input name="units" type="number" value="3">
      </label>
      <label>Year built
        <input name="year_built" type="number" value="1985">
      </label>
      <label>Purchase price
        <input name="purchase_price" type="number" value="375000">
      </label>
      <label>Projected monthly rent per unit (comma-separated, e.g. 1300,1300,1250)
        <input name="rents" value="1300,1300,1250">
      </label>
      <button type="submit">Underwrite Deal</button>
    </form>

    {% if result %}
      <h2>Underwriting Result</h2>
      <pre>{{ result }}</pre>
    {% endif %}
  </body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(FORM_HTML, result=None)

    # POST: read form and underwrite
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    state = request.form.get("state", "").strip()
    zip_code = request.form.get("zip_code", "").strip()

    def to_int(name, default):
        try:
            return int(request.form.get(name, default))
        except Exception:
            return default

    def to_float(name, default):
        try:
            return float(request.form.get(name, default))
        except Exception:
            return default

    bedrooms = to_int("bedrooms", 0)
    bathrooms = to_float("bathrooms", 0.0)
    units = to_int("units", 1)
    year_built = to_int("year_built", 1980)
    purchase_price = to_float("purchase_price", 0.0)

    # rents: "1300,1300,1250" -> dict {"Unit1":1300,...}
    rents_raw = request.form.get("rents", "")
    projected_rent_roll = {}
    if rents_raw.strip():
        parts = [p.strip() for p in rents_raw.split(",") if p.strip()]
        for idx, val in enumerate(parts, start=1):
            try:
                projected_rent_roll[f"Unit{idx}"] = float(val)
            except Exception:
                continue

    deal = PropertyDeal(
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        units=units,
        year_built=year_built,
        purchase_price=purchase_price,
        projected_rent_roll=projected_rent_roll or None,
        strategy=StrategyType.BRRRR,
    )

    bundle = underwrite_deal_with_ai(deal, photos=["photo1.jpg"])

    # Convert objects to simple dicts/strings for display
    result_display = {
        "deal": deal.__dict__,
        "underwriting": bundle["underwriting"].__dict__,
        "reno_plan": bundle["reno_plan"].__dict__ if bundle["reno_plan"] else None,
        "refi_readiness": bundle["refi_readiness"].__dict__,
    }

    return render_template_string(FORM_HTML, result=result_display)


if __name__ == "__main__":
    app.run(debug=True)
