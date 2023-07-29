import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

# Load data into DataFrame
df = pd.read_csv('nic_data.csv')

# Convert the 'EntryDate' column to datetime type
df['EntryDate'] = pd.to_datetime(df['EntryDate'], format='%m/%d/%Y')

def generate_plot(commodity_input, year_input):
    # Analysis for one commodity and one year
    selected_data = df[(df['CommodityName'] == commodity_input) & (df['EntryDate'].dt.year.isin([year_input, year_input-1]))]
    if selected_data.empty:
        return None

    # Determine the season months from the dataset
    all_months_in_data = selected_data['EntryDate'].dt.month.unique()
    all_months = list(range(1, 13))  # All months in a year

    # Find the missing months for each year and fill them with NaN
    filled_data = []
    for year in [year_input, year_input-1]:
        missing_months = list(set(all_months) - set(selected_data[selected_data['EntryDate'].dt.year == year]['EntryDate'].dt.month.unique()))
        for month in missing_months:
            filled_data.append({'EntryDate': pd.Timestamp(year, month, 1), 'ModalPrice': None, 'Arrival': None})

    # Concatenate the filled_data with selected_data
    filled_data_df = pd.DataFrame(filled_data)
    selected_data = pd.concat([selected_data, filled_data_df], ignore_index=True)

    # Sort data by EntryDate to ensure the months are in order
    selected_data = selected_data.sort_values(['EntryDate', 'CommodityName'])

    # Calculate statistics for each period
    modal_price_mean = selected_data.groupby([selected_data['EntryDate'].dt.year, selected_data['EntryDate'].dt.month])['ModalPrice'].mean()
    arrival_mean = selected_data.groupby([selected_data['EntryDate'].dt.year, selected_data['EntryDate'].dt.month])['Arrival'].mean()

    # Create line and bar graphs to visualize the results
    plt.figure(figsize=(14, 6))

    # Line plot for ModalPrice
    plt.subplot(2, 1, 1)
    for year in [year_input, year_input-1]:
        plt.plot(modal_price_mean[year].index, modal_price_mean[year].values, marker='o', label=f"{year}")
    plt.title(f"ModalPrice for {commodity_input} in {year_input} and {year_input-1}")
    plt.xlabel("Month")
    plt.ylabel("ModalPrice (Per Quintal)")
    plt.legend()

    # Bar plot for Arrival
    plt.subplot(2, 1, 2)
    bar_width = 0.35
    for i, year in enumerate([year_input, year_input-1]):
        plt.bar(np.array(arrival_mean[year].index) + i * bar_width, arrival_mean[year].values, width=bar_width, label=f"{year}")
    plt.title(f"Arrival for {commodity_input} in {year_input} and {year_input-1}")
    plt.xlabel("Month")
    plt.ylabel("Arrival (Per Quintal)")
    plt.legend()

    # Display only the month in a year (without year)
    month_labels = [pd.Timestamp(2000, month, 1).strftime('%b') for month in all_months]
    plt.xticks(all_months, month_labels, rotation=45)

    plt.tight_layout()

    # Save the plot to a BytesIO object and encode it as base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return plot_data

# This analysis.py file is intended to be called from the Flask app as a function,
# so there is no need for the code below when using it in the Flask app context.
# It is provided here for reference purposes only.
# Uncomment and provide the desired commodity name and year_input values to test the function.
# commodity_input = 'Tomato'
# year_input = 2022
# plot_data = generate_plot(commodity_input, year_input)
# if plot_data:
#     print(plot_data)
# else:
#     print("No data found for the given commodity and year.")
