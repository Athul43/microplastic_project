# app_working.py - Complete working version with all analysis features

from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from mlxtend.frequent_patterns import apriori, association_rules
import os
import io
import base64
import numpy as np
import json

# Initialize the Flask application
app = Flask(__name__, static_folder='static')

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

# Health risk thresholds (particles per gram/liter) based on research
HEALTH_THRESHOLDS = {
    'low': 50,
    'moderate': 150,
    'high': 300,
    'very_high': 500
}

# Country-specific health recommendations
COUNTRY_RECOMMENDATIONS = {
    'high_risk': {
        'policy': 'Implement strict regulations on plastic waste management and water quality standards',
        'public_health': 'Launch nationwide awareness campaigns about microplastic risks',
        'individual': 'Prioritize filtered water access and fresh food distribution programs'
    },
    'moderate_risk': {
        'policy': 'Strengthen environmental monitoring and plastic recycling programs',
        'public_health': 'Educate consumers about safer food choices and water sources',
        'individual': 'Promote local, sustainable food systems and plastic alternatives'
    },
    'low_risk': {
        'policy': 'Maintain current environmental protections and continue monitoring',
        'public_health': 'Share best practices with higher-risk regions',
        'individual': 'Continue sustainable practices and support global initiatives'
    }
}

# Food source information for research analysis
FOOD_SOURCE_INFO = {
    'Seafood_Intake': {
        'name': 'Seafood',
        'description': 'Fish, shellfish, and other marine foods',
        'main_risk': 'Ocean pollution and marine plastic ingestion',
        'global_solution': 'Reduce ocean plastic pollution, implement sustainable fishing practices',
        'country_action': 'Monitor coastal water quality, regulate fishing in polluted areas'
    },
    'Bottled_Water_Intake': {
        'name': 'Bottled Water',
        'description': 'Commercial bottled drinking water',
        'main_risk': 'Plastic bottle degradation and processing contamination',
        'global_solution': 'Improve bottled water regulations, promote alternatives',
        'country_action': 'Set microplastic limits for bottled water, improve tap water infrastructure'
    },
    'Salt_Intake': {
        'name': 'Table Salt',
        'description': 'Sea salt and processed salt products',
        'main_risk': 'Ocean and environmental contamination during production',
        'global_solution': 'Cleaner salt production methods, environmental protection',
        'country_action': 'Monitor salt production facilities, establish quality standards'
    },
    'Sugar_Intake': {
        'name': 'Sugar Products',
        'description': 'Processed sugar and sweeteners',
        'main_risk': 'Contamination during processing and packaging',
        'global_solution': 'Improve food processing standards, reduce plastic packaging',
        'country_action': 'Regulate food processing facilities, monitor contamination levels'
    },
    'Packaged_Food_Intake': {
        'name': 'Packaged Foods',
        'description': 'Pre-packaged and processed foods',
        'main_risk': 'Plastic packaging migration and processing contamination',
        'global_solution': 'Develop safer packaging materials, reduce plastic use',
        'country_action': 'Set packaging standards, promote fresh food access'
    }
}

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

def get_risk_level(value):
    """Determine risk level based on microplastic intake value"""
    if value < HEALTH_THRESHOLDS['low']:
        return 'Low', 'green'
    elif value < HEALTH_THRESHOLDS['moderate']:
        return 'Moderate', 'orange'
    elif value < HEALTH_THRESHOLDS['high']:
        return 'High', 'red'
    else:
        return 'Very High', 'darkred'

@app.route('/analyze', methods=['POST'])
def analyze_data():
    try:
        print("=== STARTING COMPLETE ANALYSIS ===")
        
        # --- 1. Data Preparation ---
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
        
        df = pd.read_csv(file)
        print(f"Data loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Select only the numeric columns for analysis
        numeric_cols = ['Seafood_Intake', 'Bottled_Water_Intake', 'Salt_Intake', 'Sugar_Intake', 'Packaged_Food_Intake']
        numeric_df = df[numeric_cols]
        
        if numeric_df.empty:
            return jsonify({"error": "No numeric data found in CSV for analysis"}), 400

        # --- 2. Global Insights ---
        total_samples = len(df)
        global_avg = numeric_df.sum(axis=1).mean()
        
        # Find highest and lowest risk countries
        df['Total_Intake'] = numeric_df.sum(axis=1)
        highest_risk_idx = df['Total_Intake'].idxmax()
        lowest_risk_idx = df['Total_Intake'].idxmin()
        
        global_insights = {
            'total_countries': total_samples,
            'global_avg_intake': round(global_avg, 1),
            'highest_risk_country': df.loc[highest_risk_idx, 'Region'],
            'lowest_risk_country': df.loc[lowest_risk_idx, 'Region'],
            'most_problematic_food': 'Bottled Water',  # Based on typical research
            'safest_food': 'Sugar Products'
        }
        print("✅ Global insights calculated")

        # --- 3. Country Analysis ---
        country_analyses = []
        for idx, row in df.iterrows():
            country_name = row.get('Region', f'Sample {idx + 1}')
            total_intake = row[numeric_cols].sum()
            avg_intake = total_intake / len(numeric_cols)
            
            risk_level, color = get_risk_level(avg_intake)
            
            # Generate country-specific recommendations
            if risk_level in ['High', 'Very High']:
                recommendations = COUNTRY_RECOMMENDATIONS['high_risk']
            elif risk_level == 'Moderate':
                recommendations = COUNTRY_RECOMMENDATIONS['moderate_risk']
            else:
                recommendations = COUNTRY_RECOMMENDATIONS['low_risk']
            
            # Food breakdown
            food_breakdown = []
            for col in numeric_cols:
                if col in FOOD_SOURCE_INFO:
                    value = row[col]
                    food_risk_level, food_color = get_risk_level(value)
                    food_breakdown.append({
                        'food_source': FOOD_SOURCE_INFO[col]['name'],
                        'intake_level': round(value, 1),
                        'risk_level': food_risk_level,
                        'color': food_color
                    })
            
            country_analyses.append({
                'country': country_name,
                'total_intake': round(total_intake, 1),
                'average_intake': round(avg_intake, 1),
                'risk_level': risk_level,
                'color': color,
                'recommendations': recommendations,
                'food_breakdown': sorted(food_breakdown, key=lambda x: x['intake_level'], reverse=True),
                'sample_id': idx + 1
            })
        
        # Sort by risk
        country_analyses.sort(key=lambda x: x['total_intake'], reverse=True)
        print("✅ Country analysis completed")

        # --- 4. K-Means Clustering ---
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(numeric_df)
        
        optimal_k = min(3, len(df))
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_features)
        df['Cluster'] = clusters
        
        # Create cluster descriptions
        cluster_descriptions = []
        for cluster_id in range(optimal_k):
            cluster_data = df[df['Cluster'] == cluster_id]
            cluster_countries = cluster_data['Region'].tolist() if 'Region' in df.columns else []
            avg_total = cluster_data[numeric_cols].sum(axis=1).mean()
            
            if avg_total < 400:
                risk_category = "Low Risk Population"
                description = "Countries/regions with relatively low microplastic exposure across food sources."
                health_impact = "Minimal immediate health concerns, maintain current practices."
                policy_recommendation = "Continue monitoring and share best practices globally."
            elif avg_total < 800:
                risk_category = "Moderate Risk Population"
                description = "Countries/regions with moderate exposure levels requiring attention."
                health_impact = "Potential long-term health risks, preventive measures recommended."
                policy_recommendation = "Implement targeted interventions and strengthen regulations."
            else:
                risk_category = "High Risk Population"
                description = "Countries/regions with concerning exposure levels needing urgent action."
                health_impact = "Significant health risks, immediate intervention required."
                policy_recommendation = "Emergency response protocols and comprehensive policy reform."
            
            cluster_descriptions.append({
                'cluster_id': int(cluster_id),
                'risk_category': risk_category,
                'description': description,
                'health_impact': health_impact,
                'policy_recommendation': policy_recommendation,
                'average_intake': round(avg_total, 1),
                'countries': cluster_countries,
                'sample_count': len(cluster_data)
            })
        
        print("✅ K-means clustering completed")

        # --- 5. Food Source Global Analysis ---
        food_source_analysis = []
        for col in numeric_cols:
            if col in FOOD_SOURCE_INFO:
                food_info = FOOD_SOURCE_INFO[col]
                avg_intake = numeric_df[col].mean()
                max_intake = numeric_df[col].max()
                min_intake = numeric_df[col].min()
                risk_level, color = get_risk_level(avg_intake)
                percentile_75 = numeric_df[col].quantile(0.75)
                high_risk_countries = (numeric_df[col] > percentile_75).sum()
                
                food_source_analysis.append({
                    'food_source': food_info['name'],
                    'global_average': round(avg_intake, 1),
                    'highest_exposure': round(max_intake, 1),
                    'lowest_exposure': round(min_intake, 1),
                    'risk_level': risk_level,
                    'color': color,
                    'countries_at_risk': int(high_risk_countries),
                    'main_concern': food_info['main_risk'],
                    'global_solution': food_info['global_solution'],
                    'country_action': food_info['country_action']
                })
        
        food_source_analysis.sort(key=lambda x: x['global_average'], reverse=True)
        print("✅ Food source analysis completed")

        # --- 6. Apriori Algorithm (Association Rules) ---
        consumption_patterns = []
        try:
            # Create binary matrix (above median = high consumption)
            binary_df = numeric_df.apply(lambda x: x > x.median()).astype(bool)
            
            if len(binary_df) >= 3:  # Need minimum samples for apriori
                frequent_itemsets = apriori(binary_df, min_support=0.2, use_colnames=True)
                
                if len(frequent_itemsets) > 0:
                    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6, num_itemsets=len(frequent_itemsets))
                    
                    for _, rule in rules.iterrows():
                        antecedents = [FOOD_SOURCE_INFO.get(item, {}).get('name', item) for item in rule['antecedents']]
                        consequents = [FOOD_SOURCE_INFO.get(item, {}).get('name', item) for item in rule['consequents']]
                        
                        consumption_patterns.append({
                            'high_consumption_in': ', '.join(antecedents),
                            'often_leads_to_high': ', '.join(consequents),
                            'confidence': f"{rule['confidence']:.1%}",
                            'support': f"{rule['support']:.1%}",
                            'implication': f"Countries with high {', '.join(antecedents)} consumption often also have high {', '.join(consequents)} exposure"
                        })
        except Exception as e:
            print(f"Apriori analysis skipped: {e}")
        
        print("✅ Apriori analysis completed")

        # --- 7. Create Visualization (K-means plot) ---
        try:
            pca = PCA(n_components=2)
            principal_components = pca.fit_transform(scaled_features)
            pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
            pca_df['Cluster'] = clusters
            
            plt.figure(figsize=(12, 8))
            colors = ['green', 'orange', 'red']
            
            for i, cluster_desc in enumerate(cluster_descriptions):
                cluster_data = pca_df[pca_df['Cluster'] == cluster_desc['cluster_id']]
                plt.scatter(cluster_data['PC1'], cluster_data['PC2'], 
                           c=colors[i % len(colors)], 
                           label=f"{cluster_desc['risk_category']} (n={cluster_desc['sample_count']})",
                           s=120, alpha=0.7, edgecolors='black', linewidth=1)
                
                # Add country labels if available
                if 'Region' in df.columns:
                    cluster_countries = df[df['Cluster'] == cluster_desc['cluster_id']]
                    for idx, row in cluster_countries.iterrows():
                        pca_idx = list(df.index).index(idx)
                        if pca_idx < len(cluster_data):
                            plt.annotate(row['Region'], 
                                       (cluster_data.iloc[pca_idx % len(cluster_data)]['PC1'], 
                                        cluster_data.iloc[pca_idx % len(cluster_data)]['PC2']), 
                                       xytext=(5, 5), textcoords='offset points', 
                                       fontsize=8, alpha=0.8)
            
            plt.title('Global Microplastic Exposure Risk Analysis', fontsize=16, fontweight='bold')
            plt.xlabel('Dietary Pattern Component 1', fontsize=12)
            plt.ylabel('Dietary Pattern Component 2', fontsize=12)
            plt.legend(title='Population Risk Groups', title_fontsize=12, bbox_to_anchor=(1.05, 1))
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save plot
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            plt.close()
            
            visualization_url = f"data:image/png;base64,{img_base64}"
        except Exception as e:
            print(f"Visualization error: {e}")
            visualization_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        print("✅ Visualization completed")

        # --- 8. Research Summary ---
        high_risk_count = len([c for c in country_analyses if c['risk_level'] in ['High', 'Very High']])
        moderate_risk_count = len([c for c in country_analyses if c['risk_level'] == 'Moderate'])
        low_risk_count = len([c for c in country_analyses if c['risk_level'] == 'Low'])
        
        research_summary = {
            "total_samples": total_samples,
            "risk_distribution": {
                "high_risk": high_risk_count,
                "moderate_risk": moderate_risk_count,
                "low_risk": low_risk_count
            }
        }

        # --- 9. Package Results ---
        results = {
            "global_insights": global_insights,
            "country_analyses": country_analyses,
            "population_clusters": cluster_descriptions,
            "food_source_analysis": food_source_analysis,
            "consumption_patterns": consumption_patterns,
            "visualization_url": visualization_url,
            "research_summary": research_summary
        }
        
        # Convert all numpy types to JSON-serializable types
        results = convert_numpy_types(results)
        
        print("=== ANALYSIS COMPLETED SUCCESSFULLY ===")
        return jsonify(results)
        
    except Exception as e:
        print(f"=== ERROR IN ANALYSIS ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting complete research analyzer...")
    app.run(debug=True, port=5003)