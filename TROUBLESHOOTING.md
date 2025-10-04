# 🆘 Troubleshooting Guide - Microplastic Health Analyzer

## Quick Fixes for Common Issues

### 🚫 "No file uploaded" Error
**Problem**: You clicked "Analyze" without selecting a file
**Solution**: 
1. Click "Choose File" button
2. Select your CSV file
3. Make sure the file name appears next to the button
4. Then click "Analyze My Health Risk"

### 📊 "No numeric data found" Error  
**Problem**: Your CSV file doesn't have the right format
**Solutions**:
1. **Check column names** - Must be exactly:
   - `Region`
   - `Seafood_Intake`
   - `Bottled_Water_Intake` 
   - `Salt_Intake`
   - `Sugar_Intake`
   - `Packaged_Food_Intake`

2. **Check data types** - All intake columns must contain numbers (not text)

3. **Use the template**:
   ```bash
   python create_sample_data.py
   ```
   This creates `my_personal_data_template.csv` you can edit

### ⏳ Analysis Takes Too Long
**Problem**: The app seems stuck on "Analyzing..."
**Solutions**:
1. **File too large** - Try with fewer rows (under 100 samples)
2. **Refresh the page** and try again
3. **Check your data** - Remove any special characters or empty rows

### 📱 Website Doesn't Load
**Problem**: Can't access http://127.0.0.1:5000
**Solutions**:
1. **Make sure Flask is running**:
   ```bash
   python app.py
   ```
   Look for "Running on http://127.0.0.1:5000"

2. **Check the correct URL** - Use `127.0.0.1:5000` not `localhost:5000`

3. **Firewall issues** - Temporarily disable firewall or add Python exception

### 🔴 "Analysis failed" Error
**Problem**: Server error during processing
**Solutions**:
1. **Check your CSV format**:
   ```
   Region,Seafood_Intake,Bottled_Water_Intake,Salt_Intake,Sugar_Intake,Packaged_Food_Intake
   Asia,180,210,65,15,330
   Europe,90,280,30,8,290
   ```

2. **Remove empty rows** from your CSV

3. **Use only numbers** in intake columns (no units like "mg" or "particles")

4. **Have at least 3 rows** of data for analysis

### 📋 Results Don't Make Sense
**Problem**: Health scores or recommendations seem wrong
**Check**:
1. **Your input units** - Should be particles per gram/liter
2. **Realistic values**:
   - Seafood: 50-300 particles/gram
   - Bottled water: 50-500 particles/liter  
   - Salt: 10-80 particles/gram
   - Sugar: 3-25 particles/gram
   - Packaged food: 100-400 particles/gram

3. **Regional differences** - Pollution levels vary by location

## 🔧 Installation Issues

### Missing Packages Error
**Problem**: `ModuleNotFoundError: No module named 'flask'`
**Solution**:
```bash
pip install flask pandas matplotlib seaborn scikit-learn mlxtend numpy
```

### Python Version Issues  
**Problem**: Syntax errors or import failures
**Solution**: 
- Use Python 3.7 or newer
- Check version: `python --version`

### Permission Errors
**Problem**: Can't install packages or run scripts
**Solution**:
- Use `pip install --user` instead of `pip install`
- Run terminal as administrator (Windows)

## 📝 Data Preparation Tips

### Creating Your Personal Data

1. **Start with the template**:
   ```bash
   python create_sample_data.py
   ```

2. **Estimate your consumption**:
   - How many seafood meals per week?
   - Liters of bottled water per day?
   - Grams of salt used daily?

3. **Research typical values** for your region:
   - Check local water quality reports
   - Look up seafood contamination studies
   - Consider packaging types you use

4. **Be honest about portions**:
   - Overestimating is better than underestimating
   - Include all sources (snacks, drinks, etc.)

### Example Personal Data Entry

For someone who:
- Eats seafood 3x/week
- Drinks 2 bottles of water daily  
- Uses moderate salt
- Eats some processed foods

```csv
Region,Seafood_Intake,Bottled_Water_Intake,Salt_Intake,Sugar_Intake,Packaged_Food_Intake
North America,120,250,35,12,280
```

## 🚨 When to Seek Help

### Technical Issues
- App crashes repeatedly
- Results completely unrealistic  
- Can't install required packages

### Health Concerns
- Your results show very high risk levels
- You have symptoms that concern you
- You want to interpret results for health decisions

**Remember**: This tool is for education, not medical diagnosis!

## 📞 Getting Support

1. **Check this guide first** - Most issues have simple solutions
2. **Try the sample data** - Test if the app works with provided examples
3. **Read the README.md** - Contains detailed setup instructions
4. **Review your CSV format** - Most errors come from incorrect data format

## ✅ Success Checklist

Before running analysis, verify:
- [ ] Python 3.7+ installed
- [ ] All packages installed successfully
- [ ] Flask app running (see "Running on http://127.0.0.1:5000")
- [ ] CSV file has correct column names
- [ ] All intake values are numbers
- [ ] At least 3 rows of data
- [ ] File uploaded successfully

---

**💡 Pro Tip**: If all else fails, try the sample data first to make sure everything works, then work on formatting your personal data!