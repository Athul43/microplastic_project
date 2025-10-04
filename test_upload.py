# test_upload.py - Simple test to debug upload issues

from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import traceback

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze_data():
    try:
        print("=== ANALYSIS STARTING ===")
        
        # Check if file was uploaded
        if 'file' not in request.files:
            print("ERROR: No file in request")
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        if file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({"error": "No file selected"}), 400
            
        print(f"File received: {file.filename}")
        
        # Load CSV
        df = pd.read_csv(file)
        print(f"Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        
        # Basic validation
        required_cols = ['Region', 'Seafood_Intake', 'Bottled_Water_Intake', 'Salt_Intake', 'Sugar_Intake', 'Packaged_Food_Intake']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"ERROR: Missing columns: {missing_cols}")
            return jsonify({"error": f"Missing required columns: {missing_cols}"}), 400
        
        # Get numeric data
        numeric_cols = ['Seafood_Intake', 'Bottled_Water_Intake', 'Salt_Intake', 'Sugar_Intake', 'Packaged_Food_Intake']
        numeric_df = df[numeric_cols]
        print(f"Numeric data shape: {numeric_df.shape}")
        
        # Simple analysis
        total_samples = len(df)
        global_avg = numeric_df.sum(axis=1).mean()
        
        print(f"Basic stats calculated: {total_samples} samples, avg {global_avg:.1f}")
        
        # Create simple results
        results = {
            "global_insights": {
                "total_countries": total_samples,
                "global_avg_intake": round(global_avg, 1),
                "highest_risk_country": df['Region'].iloc[0],
                "lowest_risk_country": df['Region'].iloc[-1]
            },
            "country_analyses": [],
            "population_clusters": [],
            "food_source_analysis": [],
            "consumption_patterns": [],
            "visualization_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "research_summary": {
                "total_samples": total_samples,
                "risk_distribution": {
                    "high_risk": 1,
                    "moderate_risk": max(0, total_samples - 2),
                    "low_risk": 1
                }
            }
        }
        
        print("=== ANALYSIS COMPLETED SUCCESSFULLY ===")
        return jsonify(results)
        
    except Exception as e:
        print(f"=== ERROR IN ANALYSIS ===")
        print(f"Error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting test server on port 5002...")
    app.run(debug=True, port=5002)