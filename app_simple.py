# app_simple.py - Simplified version to debug the 500 error

from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import json

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze_data():
    try:
        print("🔍 Starting analysis...")
        
        # --- 1. Data Preparation ---
        file = request.files.get('file')
        if not file:
            print("❌ No file uploaded")
            return jsonify({"error": "No file uploaded"}), 400
        
        print(f"✅ File received: {file.filename}")
        
        df = pd.read_csv(file)
        print(f"✅ Data loaded: {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {list(df.columns)}")
        
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=['number'])
        print(f"✅ Numeric columns: {list(numeric_df.columns)}")
        
        if numeric_df.empty:
            print("❌ No numeric data found")
            return jsonify({"error": "No numeric data found in CSV for analysis"}), 400

        # Simple analysis
        total_samples = len(df)
        avg_total_intake = numeric_df.sum(axis=1).mean()
        
        # Create simple results
        results = {
            "global_insights": {
                "total_countries": total_samples,
                "global_avg_intake": round(avg_total_intake, 1),
                "highest_risk_country": df.iloc[0]['Region'] if 'Region' in df.columns else 'Unknown',
                "lowest_risk_country": df.iloc[-1]['Region'] if 'Region' in df.columns else 'Unknown'
            },
            "country_analyses": [
                {
                    "country": row.get('Region', f'Sample {idx+1}'),
                    "total_intake": round(sum([row[col] for col in numeric_df.columns]), 1),
                    "risk_level": "Moderate",
                    "color": "orange"
                }
                for idx, row in df.iterrows()
            ],
            "research_summary": {
                "total_samples": total_samples,
                "risk_distribution": {
                    "high_risk": 1,
                    "moderate_risk": total_samples - 2,
                    "low_risk": 1
                }
            }
        }
        
        print("✅ Analysis completed successfully")
        return jsonify(results)
        
    except Exception as e:
        print(f"❌ Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting simplified Flask app...")
    app.run(debug=True, port=5001)