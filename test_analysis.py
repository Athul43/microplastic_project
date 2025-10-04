# Simple test script to debug the analysis function
import pandas as pd
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analysis():
    print("Testing analysis function...")
    
    # Load test data
    try:
        df = pd.read_csv('quick_test_data.csv')
        print(f"✅ Successfully loaded test data with {len(df)} rows")
        print("Data preview:")
        print(df.head())
        
        # Test the key components
        numeric_df = df.select_dtypes(include=['number'])
        print(f"✅ Numeric columns: {list(numeric_df.columns)}")
        
        # Test basic analysis
        total_countries = len(df)
        global_avg = numeric_df.sum(axis=1).mean()
        print(f"✅ Basic stats - Countries: {total_countries}, Avg intake: {global_avg:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_analysis()