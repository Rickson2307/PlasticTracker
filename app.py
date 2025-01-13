from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server-side plotting
import matplotlib.pyplot as plt

app = Flask(__name__)

# File to store data
FILE_NAME = "plastic_usage.csv"

# Initialize the file if it doesn't exist
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Community", "Date", "Plastic_Used_kg"])
    df.to_csv(FILE_NAME, index=False)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Add data route
@app.route('/add', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        community = request.form['community']
        date = request.form['date']
        plastic_used_kg = float(request.form['plastic_used_kg'])
        
        # Load existing data and add the new entry
        df = pd.read_csv(FILE_NAME)
        new_entry = pd.DataFrame({
            "Community": [community],
            "Date": [date],
            "Plastic_Used_kg": [plastic_used_kg]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(FILE_NAME, index=False)
        
        return redirect(url_for('index'))
    return render_template('add.html')

# Analyze data route
@app.route('/analyze')
def analyze_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        df['Date'] = pd.to_datetime(df['Date'])
        total_usage = df.groupby("Community")["Plastic_Used_kg"].sum()
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_usage = df.groupby(['Community', 'Month'])['Plastic_Used_kg'].sum()
        
        return render_template(
            'analyze.html',
            total_usage=total_usage.to_dict(),
            monthly_usage=monthly_usage.to_dict()
        )
    else:
        return "No data available to analyze."

# Plot trends route
@app.route('/plot')
def plot_trends():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        df['Date'] = pd.to_datetime(df['Date'])

        # Generate the plot
        plt.figure(figsize=(10, 6))
        for community in df['Community'].unique():
            community_data = df[df['Community'] == community]
            plt.plot(community_data['Date'], community_data['Plastic_Used_kg'], label=community)
        
        plt.xlabel('Date')
        plt.ylabel('Plastic Used (kg)')
        plt.title('Plastic Usage Trends')
        plt.legend()
        plt.tight_layout()

        # Save the plot as an image file
        plot_path = os.path.join('static', 'plot.png')
        plt.savefig(plot_path)
        plt.close()

        # Render the template with the plot
        return render_template('plot.html', plot_image=plot_path)
    else:
        return "No data available to plot."

if __name__ == '__main__':
    app.run(debug=True)
