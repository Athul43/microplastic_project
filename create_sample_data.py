#!/usr/bin/env python3
"""
Sample Data Generator for Global Microplastic Research Analyzer
==============================================================

This script creates sample data files representing microplastic intake
across different countries and regions for research analysis.
"""

import pandas as pd
import numpy as np
import random

def create_research_dataset():
    """Create sample microplastic intake data for global research analysis"""
    
    # Set random seed for reproducible results
    np.random.seed(42)
    random.seed(42)
    
    # Define countries/regions with varying pollution levels
    countries_data = [
        # High pollution regions
        ('China', 'high', 200, 350),
        ('India', 'high', 180, 320),
        ('Indonesia', 'high', 190, 340),
        ('Philippines', 'high', 170, 330),
        ('Bangladesh', 'high', 160, 310),
        
        # Moderate pollution regions
        ('USA', 'moderate', 130, 240),
        ('Brazil', 'moderate', 140, 250),
        ('Japan', 'moderate', 120, 220),
        ('South Korea', 'moderate', 125, 230),
        ('Mexico', 'moderate', 135, 260),
        ('Turkey', 'moderate', 115, 225),
        ('Russia', 'moderate', 110, 210),
        
        # Low pollution regions
        ('Norway', 'low', 80, 180),
        ('Sweden', 'low', 75, 170),
        ('Finland', 'low', 85, 190),
        ('Denmark', 'low', 90, 200),
        ('Switzerland', 'low', 70, 160),
        ('New Zealand', 'low', 95, 205),
        ('Canada', 'low', 100, 220),
        ('Australia', 'low', 105, 215),
        
        # European countries (mixed)
        ('Germany', 'moderate', 95, 205),
        ('France', 'moderate', 100, 210),
        ('UK', 'moderate', 105, 215),
        ('Italy', 'moderate', 110, 220),
        ('Spain', 'moderate', 115, 225),
        
        # Additional regions for better analysis
        ('Nigeria', 'high', 150, 290),
        ('Egypt', 'moderate', 125, 235),
        ('South Africa', 'moderate', 120, 230),
        ('Argentina', 'moderate', 115, 225),
        ('Chile', 'low', 90, 195)
    ]
    
    data = []
    
    for country, pollution_level, seafood_base, bottled_water_base in countries_data:
        # Add some variation within each country (multiple samples)
        for sample in range(random.randint(1, 3)):  # 1-3 samples per country
            
            # Pollution level affects all food sources
            if pollution_level == 'high':
                pollution_multiplier = random.uniform(1.2, 1.8)
            elif pollution_level == 'moderate':
                pollution_multiplier = random.uniform(0.8, 1.2)
            else:  # low
                pollution_multiplier = random.uniform(0.5, 0.9)
            
            # Generate realistic values with regional variations
            seafood_intake = max(20, seafood_base + random.randint(-40, 60)) * pollution_multiplier
            bottled_water_intake = max(50, bottled_water_base + random.randint(-60, 80)) * pollution_multiplier
            salt_intake = max(5, random.randint(15, 80)) * pollution_multiplier
            sugar_intake = max(2, random.randint(3, 25)) * pollution_multiplier
            packaged_food_intake = max(100, random.randint(200, 400)) * pollution_multiplier
            
            # Round to reasonable precision
            data.append({
                'Region': country,
                'Seafood_Intake': round(seafood_intake, 1),
                'Bottled_Water_Intake': round(bottled_water_intake, 1),
                'Salt_Intake': round(salt_intake, 1),
                'Sugar_Intake': round(sugar_intake, 1),
                'Packaged_Food_Intake': round(packaged_food_intake, 1)
            })
    
    return pd.DataFrame(data)

def create_small_sample():
    """Create a smaller sample for quick testing"""
    
    small_data = [
        {'Region': 'Japan', 'Seafood_Intake': 85.0, 'Bottled_Water_Intake': 180.0, 'Salt_Intake': 25.0, 'Sugar_Intake': 8.0, 'Packaged_Food_Intake': 220.0},
        {'Region': 'China', 'Seafood_Intake': 280.0, 'Bottled_Water_Intake': 420.0, 'Salt_Intake': 65.0, 'Sugar_Intake': 18.0, 'Packaged_Food_Intake': 380.0},
        {'Region': 'Norway', 'Seafood_Intake': 60.0, 'Bottled_Water_Intake': 120.0, 'Salt_Intake': 15.0, 'Sugar_Intake': 5.0, 'Packaged_Food_Intake': 140.0},
        {'Region': 'USA', 'Seafood_Intake': 120.0, 'Bottled_Water_Intake': 250.0, 'Salt_Intake': 35.0, 'Sugar_Intake': 12.0, 'Packaged_Food_Intake': 290.0},
        {'Region': 'Brazil', 'Seafood_Intake': 95.0, 'Bottled_Water_Intake': 200.0, 'Salt_Intake': 30.0, 'Sugar_Intake': 10.0, 'Packaged_Food_Intake': 260.0},
        {'Region': 'India', 'Seafood_Intake': 220.0, 'Bottled_Water_Intake': 380.0, 'Salt_Intake': 55.0, 'Sugar_Intake': 15.0, 'Packaged_Food_Intake': 350.0}
    ]
    
    return pd.DataFrame(small_data)

if __name__ == "__main__":
    print("🌍 Creating global microplastic research dataset...")
    
    # Create comprehensive research dataset
    research_df = create_research_dataset()
    research_df.to_csv('global_microplastic_research_data.csv', index=False)
    print(f"✅ Created 'global_microplastic_research_data.csv' with {len(research_df)} samples from {research_df['Region'].nunique()} countries")
    
    # Create small sample for quick testing
    small_df = create_small_sample()
    small_df.to_csv('quick_test_data.csv', index=False)
    print("✅ Created 'quick_test_data.csv' with 6 countries for quick testing")
    
    print("\n📊 Global dataset preview:")
    print(research_df.head(10))
    
    print(f"\n� Dataset Statistics:")
    print(f"Countries included: {research_df['Region'].nunique()}")
    print(f"Total samples: {len(research_df)}")
    print(f"Average samples per country: {len(research_df) / research_df['Region'].nunique():.1f}")
    
    print("\n🌍 Risk Level Distribution:")
    # Calculate risk levels for preview
    research_df['Total_Intake'] = research_df[['Seafood_Intake', 'Bottled_Water_Intake', 'Salt_Intake', 'Sugar_Intake', 'Packaged_Food_Intake']].sum(axis=1)
    high_risk = len(research_df[research_df['Total_Intake'] > 800])
    moderate_risk = len(research_df[(research_df['Total_Intake'] >= 400) & (research_df['Total_Intake'] <= 800)])
    low_risk = len(research_df[research_df['Total_Intake'] < 400])
    
    print(f"High Risk (>800): {high_risk} samples")
    print(f"Moderate Risk (400-800): {moderate_risk} samples") 
    print(f"Low Risk (<400): {low_risk} samples")
    
    print("\n💡 Research Notes:")
    print("- Data represents particles per gram/liter measurements")
    print("- Regional variations reflect different pollution levels")
    print("- Multiple samples per country show within-country variation")
    print("- Use this data to test global analysis algorithms")
    
    print("\n🚀 Ready for analysis! Upload either file to the research analyzer.")