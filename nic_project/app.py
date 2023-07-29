from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import io
import base64
import os

app = Flask(__name__)

# Load the dataset
data = pd.read_csv('nic_data.csv')
# Convert 'EntryDate' column to datetime format
data['EntryDate'] = pd.to_datetime(data['EntryDate'])

# Perform SARIMA modeling and prediction
def perform_sarima_prediction(commodity_name):
    commodity_data = data[data['CommodityName'].str.lower() == commodity_name.lower()]
    if len(commodity_data) > 0:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")

            model = SARIMAX(commodity_data['ModalPrice'], order=(1, 1, 1), seasonal_order=(1, 0, 0, 12))
            model_fit = model.fit(disp=False)

            # Forecast the prices for the next year
            next_year_forecast = model_fit.get_forecast(steps=12)
            forecasted_prices = next_year_forecast.predicted_mean
            next_year_price = forecasted_prices.iloc[-1]

        return next_year_price
    else:
        return None

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_option_details')
def get_option_details():
    vegetable = request.args.get('vegetable')
    option = request.args.get('option')

    vegetable_data = data[data['CommodityName'].str.lower() == vegetable.lower()]
    if not vegetable_data.empty:
        if option == 'Price':
            return jsonify({option: '₹ {:.2f} per Quintals'.format(vegetable_data['ModalPrice'].mean())})
        elif option == 'Market':
            markets = vegetable_data['MarketName'].unique()
            return jsonify({option: list(markets)})
        elif option == 'Season':
            if 'Season' in vegetable_data:
                return jsonify({option: vegetable_data['Season'].iloc[-1]})
            else:
                return jsonify({option: 'N/A'})
        elif option == 'NextYearPrice':
            next_year_price = perform_sarima_prediction(vegetable)
            if next_year_price is not None:
                return jsonify({option: '₹ {:.2f} per Quintals'.format(next_year_price)})
            else:
                return jsonify({option: 'N/A'})

    return jsonify({option: 'N/A'})


# Analysis route
@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        commodity_input = request.form.get('commodity')
        year_input = int(request.form.get('year'))

        selected_data = data[(data['CommodityName'].str.lower() == commodity_input.lower()) & (data['EntryDate'].dt.year.isin([year_input, year_input-1]))]

        if selected_data.empty:
            return render_template('errors.html', error_message="No data found for the given commodity and year.")
        else:
            # Create subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

            # Line plot for ModalPrice
            for year in [year_input, year_input-1]:
                modal_price_mean = selected_data[selected_data['EntryDate'].dt.year == year].groupby(selected_data['EntryDate'].dt.month)['ModalPrice'].mean()
                ax1.plot(modal_price_mean.index, modal_price_mean.values, marker='o', label=f"{year}")

            ax1.set_title(f"ModalPrice for {commodity_input} in {year_input} and {year_input-1}")
            ax1.set_xlabel("Month")
            ax1.set_ylabel("ModalPrice (Per Quintal)")
            ax1.legend()

            # Bar plot for Arrival
            bar_width = 0.35
            for i, year in enumerate([year_input, year_input-1]):
                arrival_mean = selected_data[selected_data['EntryDate'].dt.year == year].groupby(selected_data['EntryDate'].dt.month)['Arrival'].mean()
                ax2.bar(np.array(arrival_mean.index) + i * bar_width, arrival_mean.values, width=bar_width, label=f"{year}")

            ax2.set_title(f"Arrival for {commodity_input} in {year_input} and {year_input-1}")
            ax2.set_xlabel("Month")
            ax2.set_ylabel("Arrival (Per Quintal)")
            ax2.legend()

            # Display only the month in a year (without year)
            all_months = sorted(selected_data['EntryDate'].dt.month.unique())
            month_labels = [pd.Timestamp(2000, month, 1).strftime('%b') for month in all_months]
            ax2.set_xticks(all_months)
            ax2.set_xticklabels(month_labels, rotation=45)

            # Save the plot to BytesIO
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()

            # Render the template with the plot data
            return render_template('analysis.html', plot_data=plot_data)

    return render_template('analysis.html')

if __name__ == '__main__':
    app.run(debug=True)
