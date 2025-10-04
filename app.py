# app.py - Global Microplastic Intake Research Analyzer

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
import numpy as np

# Initialize the Flask application
app = Flask(__name__, static_folder='static')

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

# --- Main Route to Serve the Frontend ---
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# --- Helper Functions for Population Analysis ---
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

def analyze_country_risk(country_data):
    """Analyze risk level for a specific country/region"""
    total_intake = sum([country_data[col] for col in country_data.index if col in FOOD_SOURCE_INFO])
    avg_intake = total_intake / len([col for col in country_data.index if col in FOOD_SOURCE_INFO])
    
    risk_level, color = get_risk_level(avg_intake)
    
    # Generate country-specific recommendations
    if risk_level in ['High', 'Very High']:
        recommendations = COUNTRY_RECOMMENDATIONS['high_risk']
    elif risk_level == 'Moderate':
        recommendations = COUNTRY_RECOMMENDATIONS['moderate_risk']
    else:
        recommendations = COUNTRY_RECOMMENDATIONS['low_risk']
    
    return {
        'average_intake': round(avg_intake, 1),
        'total_intake': round(total_intake, 1),
        'risk_level': risk_level,
        'color': color,
        'recommendations': recommendations
    }

def generate_global_insights(df):
    """Generate insights for the global dataset"""
    numeric_df = df.select_dtypes(include=['number'])
    
    insights = {
        'total_countries': len(df),
        'global_avg_intake': round(numeric_df.sum(axis=1).mean(), 1),
        'highest_risk_country': '',
        'lowest_risk_country': '',
        'most_problematic_food': '',
        'safest_food': ''
    }
    
    # Find highest and lowest risk countries
    country_risks = []
    for idx, row in df.iterrows():
        country = row.get('Region', f'Sample {idx+1}')
        # Get only numeric values from the row
        numeric_row = row[numeric_df.columns]
        total_intake = sum([numeric_row[col] for col in numeric_row.index if col in FOOD_SOURCE_INFO])
        country_risks.append((country, total_intake))
    
    country_risks.sort(key=lambda x: x[1], reverse=True)
    insights['highest_risk_country'] = country_risks[0][0] if country_risks else 'Unknown'
    insights['lowest_risk_country'] = country_risks[-1][0] if country_risks else 'Unknown'
    
    # Find most problematic food source
    food_averages = []
    for col in numeric_df.columns:
        if col in FOOD_SOURCE_INFO:
            avg_intake = numeric_df[col].mean()
            food_averages.append((FOOD_SOURCE_INFO[col]['name'], avg_intake))
    
    food_averages.sort(key=lambda x: x[1], reverse=True)
    insights['most_problematic_food'] = food_averages[0][0] if food_averages else 'Unknown'
    insights['safest_food'] = food_averages[-1][0] if food_averages else 'Unknown'
    
    return insights

# --- API Endpoint for Population Analysis ---
@app.route('/analyze', methods=['POST'])
def analyze_data():
    try:
        # --- 1. Data Preparation ---
        file = request.files['file']
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
        
        df = pd.read_csv(file)
        
        # Select only the numeric columns for analysis
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.empty:
            return jsonify({"error": "No numeric data found in CSV for analysis"}), 400

        # --- 2. Global Insights ---
        global_insights = generate_global_insights(df)

        # --- 3. Country/Region Analysis ---
        country_analyses = []
        for idx, row in df.iterrows():
            country_name = row.get('Region', f'Sample {idx + 1}')
            # Get only numeric values from the row
            numeric_row = row[numeric_df.columns]
            
            country_analysis = analyze_country_risk(numeric_row)
            country_analysis['country'] = country_name
            country_analysis['sample_id'] = idx + 1
            
            # Add detailed food source breakdown
            food_breakdown = []
            for col in numeric_row.index:
                if col in FOOD_SOURCE_INFO:
                    value = numeric_row[col]
                    risk_level, color = get_risk_level(value)
                    food_breakdown.append({
                        'food_source': FOOD_SOURCE_INFO[col]['name'],
                        'intake_level': round(value, 1),
                        'risk_level': risk_level,
                        'color': color
                    })
            
            country_analysis['food_breakdown'] = sorted(food_breakdown, 
                                                      key=lambda x: x['intake_level'], 
                                                      reverse=True)
            country_analyses.append(country_analysis)

        # Sort countries by risk (highest first)
        country_analyses.sort(key=lambda x: x['total_intake'], reverse=True)

        # --- 4. Population-Level Clustering ---
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(numeric_df)
        
        optimal_k = min(3, len(df))
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_features)
        df['Cluster'] = clusters
        
        # Create population cluster descriptions
        cluster_analysis = df.groupby('Cluster').mean(numeric_only=True).reset_index()
        cluster_descriptions = []
        
        for cluster_id in cluster_analysis['Cluster']:
            cluster_data = cluster_analysis[cluster_analysis['Cluster'] == cluster_id].iloc[0]
            cluster_countries = df[df['Cluster'] == cluster_id]['Region'].tolist() if 'Region' in df.columns else []
            
            avg_total = sum([cluster_data[col] for col in numeric_df.columns if col in FOOD_SOURCE_INFO])
            
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
                'sample_count': len(df[df['Cluster'] == cluster_id])
            })

        # --- 5. Food Source Global Analysis ---
        food_source_global_analysis = []
        percentile_75 = numeric_df.quantile(0.75)
        
        for column in numeric_df.columns:
            if column in FOOD_SOURCE_INFO:
                food_info = FOOD_SOURCE_INFO[column]
                avg_intake = numeric_df[column].mean()
                max_intake = numeric_df[column].max()
                min_intake = numeric_df[column].min()
                risk_level, color = get_risk_level(avg_intake)
                high_risk_countries = (numeric_df[column] > percentile_75[column]).sum()
                
                food_source_global_analysis.append({
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
        
        food_source_global_analysis.sort(key=lambda x: x['global_average'], reverse=True)

        # --- 6. Association Analysis (Food Consumption Patterns) ---
        binary_df = numeric_df.apply(lambda x: x > x.median()).astype(bool)
        
        try:
            frequent_itemsets = apriori(binary_df, min_support=0.2, use_colnames=True)
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)
            
            consumption_patterns = []
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
        except:
            consumption_patterns = []

        # --- 7. Create Visualization ---
        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(scaled_features)
        pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
        pca_df['Cluster'] = clusters
        
        # Add country labels if available
        if 'Region' in df.columns:
            pca_df['Country'] = df['Region'].values

        plt.figure(figsize=(12, 8))
        colors = ['green', 'orange', 'red']
        
        for i, cluster_desc in enumerate(cluster_descriptions):
            cluster_data = pca_df[pca_df['Cluster'] == cluster_desc['cluster_id']]
            plt.scatter(cluster_data['PC1'], cluster_data['PC2'], 
                       c=colors[i % len(colors)], 
                       label=f"{cluster_desc['risk_category']} (n={cluster_desc['sample_count']})",
                       s=120, alpha=0.7, edgecolors='black', linewidth=1)
            
            # Add country labels if available
            if 'Country' in cluster_data.columns:
                for idx, row in cluster_data.iterrows():
                    plt.annotate(row['Country'], (row['PC1'], row['PC2']), 
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

        # --- 8. Package Results ---
        results = {
            "global_insights": global_insights,
            "country_analyses": country_analyses,
            "population_clusters": cluster_descriptions,
            "food_source_analysis": food_source_global_analysis,
            "consumption_patterns": consumption_patterns,
            "visualization_url": f"data:image/png;base64,{img_base64}",
            "research_summary": {
                "total_samples": len(df),
                "risk_distribution": {
                    "high_risk": len([c for c in country_analyses if c['risk_level'] in ['High', 'Very High']]),
                    "moderate_risk": len([c for c in country_analyses if c['risk_level'] == 'Moderate']),
                    "low_risk": len([c for c in country_analyses if c['risk_level'] == 'Low'])
                }
            }
        }
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# --- Educational Content Endpoint ---
@app.route('/health-tips', methods=['GET'])
def get_health_tips():
    """Provide educational content and health tips"""
    tips = {
        "general_tips": [
            {
                "title": "Choose Glass Over Plastic",
                "description": "Use glass containers and bottles instead of plastic ones, especially for food storage and drinking water.",
                "icon": "fas fa-wine-bottle"
            },
            {
                "title": "Filter Your Water",
                "description": "Install a quality water filter that can remove microplastics, or boil water for 15+ minutes.",
                "icon": "fas fa-filter"
            },
            {
                "title": "Buy Fresh Foods",
                "description": "Choose fresh, unpackaged foods over processed or pre-packaged items when possible.",
                "icon": "fas fa-carrot"
            },
            {
                "title": "Avoid Heating Plastic",
                "description": "Never microwave food in plastic containers or leave plastic bottles in hot cars.",
                "icon": "fas fa-thermometer-half"
            },
            {
                "title": "Choose Sustainable Seafood",
                "description": "Select smaller fish, freshwater species, or seafood from less polluted waters.",
                "icon": "fas fa-fish"
            }
        ],
        "food_alternatives": {
            "high_risk_foods": [
                {"food": "Bottled Water", "alternatives": ["Filtered tap water", "Glass bottled water", "Home filtration systems"]},
                {"food": "Sea Salt", "alternatives": ["Rock salt", "Mined salt", "Certified microplastic-free salt"]},
                {"food": "Large Ocean Fish", "alternatives": ["Smaller fish", "Freshwater fish", "Plant-based proteins"]},
                {"food": "Packaged Foods", "alternatives": ["Fresh produce", "Bulk bin items", "Glass-packaged goods"]},
                {"food": "Takeout Containers", "alternatives": ["Home-cooked meals", "Bring your own containers", "Glass meal prep"]}
            ]
        },
        "health_monitoring": [
            "Track your symptoms and energy levels",
            "Maintain a food diary",
            "Regular health check-ups",
            "Stay informed about new research",
            "Consider consultation with healthcare providers"
        ]
    }
    return jsonify(tips)

if __name__ == '__main__':
    app.run(debug=True)