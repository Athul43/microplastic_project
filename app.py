# app.py - The Backend

from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from mlxtend.frequent_patterns import apriori, association_rules
import os
import io
import base64

# Initialize the Flask application
app = Flask(__name__, static_folder='static')

# --- Main Route to Serve the Frontend ---
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# --- API Endpoint for Analysis ---
@app.route('/analyze', methods=['POST'])
def analyze_data():
    # --- 1. Data Preparation ---
    file = request.files['file']
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    
    df = pd.read_csv(file)
    
    # Assuming the CSV has columns for food types (and maybe a region column)
    # Let's select only the numeric columns for analysis
    numeric_df = df.select_dtypes(include=['number'])
    
    if numeric_df.empty:
        return jsonify({"error": "No numeric data found in CSV for analysis"}), 400

    # --- 2. K-Means Clustering ---
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(numeric_df)
    
    # Elbow method to find optimal k (simplified for backend)
    # In a real app, you might set a fixed k or make it a parameter
    optimal_k = 3 
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_features)
    df['Cluster'] = clusters
    
    cluster_analysis = df.groupby('Cluster').mean(numeric_only=True).reset_index()

    # --- 3. Apriori Algorithm ---
    binary_df = numeric_df.apply(lambda x: x > x.median()).astype(bool)
    frequent_itemsets = apriori(binary_df, min_support=0.2, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)
    
    # Convert frozensets to strings for JSON compatibility
    rules['antecedents'] = rules['antecedents'].apply(lambda a: ', '.join(list(a)))
    rules['consequents'] = rules['consequents'].apply(lambda c: ', '.join(list(c)))

    # --- 4. Harmful Item Analysis (New Section) ---
    # Calculate the 75th percentile for each numeric column (food source)
    percentile_75 = numeric_df.quantile(0.75)
    
    # Find items exceeding the 75th percentile for each row
    harmful_items_df = numeric_df.apply(lambda x: x > percentile_75[x.name], axis=0)
    harmful_items_summary = harmful_items_df.sum().sort_values(ascending=False)
    harmful_items_summary = harmful_items_summary[harmful_items_summary > 0].reset_index()
    harmful_items_summary.columns = ['Food Source', 'Number of High-Intake Samples']

    # --- 4. Visualization ---
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(scaled_features)
    pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
    pca_df['Cluster'] = clusters

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='PC1', y='PC2', hue='Cluster', data=pca_df, palette='viridis', s=80)
    plt.title('K-Means Clusters of Microplastic Intake')
    plt.grid(True)
    
    # Save plot to a bytes buffer and encode it to send via JSON
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close()

    # --- 5. Package Results ---
    results = {
        "cluster_analysis_html": cluster_analysis.to_html(classes='table table-striped', index=False),
        "association_rules_html": rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].to_html(classes='table table-striped', index=False),
        "cluster_plot_url": f"data:image/png;base64,{img_base64}",
        "harmful_items_html": harmful_items_summary.to_html(classes='table table-striped', index=False)
    }
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)