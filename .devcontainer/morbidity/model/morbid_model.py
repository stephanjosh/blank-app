
import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings('ignore')

# ============================================
# DATA EXTRACTION CLASS
# ============================================

class MentalHealthDataExtractor:
    """
    Extract mental health disorder data from Excel
    """
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_data = None
        self.processed_data = None
        
        # These map to EXACT columns in your Excel file
        self.col_mapping = {
            '0-9_M': 2, '0-9_F': 3,
            '10-18_M': 4, '10-18_F': 5,
            '19-24_M': 6, '19-24_F': 7,
            '25-34_M': 8, '25-34_F': 9,
            '35-64_M': 10, '35-64_F': 11,
            '65+_M': 12, '65+_F': 13,
            'Unknown_M': 14, 'Unknown_F': 15
        }
        
        self.month_starts = {
            'July 2024': 5,
            'August 2024': 63,
            'September 2024': 117,
            'October 2024': 165,
            'November 2024': 217,
            'December 2024': 269,
            'January 2025': 319,
            'February 2025': 363,
            'March 2025': 428,
            'April 2025': 473,
            'May 2025': 523,
            'June 2025': 568
        }
        
    def load(self):
        """Load the Excel file"""
        self.raw_data = pd.read_excel(self.file_path, sheet_name=0, header=None)
        print(f"Loaded: {self.raw_data.shape[0]} rows, {self.raw_data.shape[1]} columns")
        return self
    
    def extract(self):
        """Extract all records from Excel"""
        all_records = []
        
        for month, start_row in self.month_starts.items():
            print(f"Extracting {month}...")
            records = self._extract_month(start_row, month)
            all_records.extend(records)
        
        self.processed_data = pd.DataFrame(all_records)
        print(f"\n✅ Extracted {len(self.processed_data)} total records")
        return self.processed_data
    
    def _extract_month(self, start_row, month):
        """Extract one month's data"""
        records = []
        row = start_row + 8  # Start after header
        
        while row < len(self.raw_data):
            diagnosis = self._get_text(row, 1)
            
            if not diagnosis or diagnosis == '':
                break
            if 'MONTH:' in diagnosis.upper():
                break
            if diagnosis.upper() == 'TOTAL':
                break
            
            record = {'month': month, 'diagnosis': diagnosis.strip()}
            male_total = 0
            female_total = 0
            
            for col_name, col_idx in self.col_mapping.items():
                val = self._get_number(row, col_idx)
                record[col_name] = val
                
                if '_M' in col_name:
                    male_total += val
                else:
                    female_total += val
            
            record['total_male'] = male_total
            record['total_female'] = female_total
            record['total_cases'] = male_total + female_total
            
            records.append(record)
            row += 1
        
        return records
    
    def _get_number(self, row, col):
        """Get numeric value from cell"""
        try:
            val = self.raw_data.iloc[row, col]
            if pd.isna(val):
                return 0
            if isinstance(val, str):
                cleaned = re.sub(r'[^0-9.-]', '', val)
                return int(float(cleaned)) if cleaned else 0
            return int(val) if val else 0
        except:
            return 0
    
    def _get_text(self, row, col):
        """Get text value from cell"""
        try:
            val = self.raw_data.iloc[row, col]
            return str(val).strip() if pd.notna(val) else ''
        except:
            return ''


# ============================================
# MAIN - JUST EXTRACT AND SAVE
# ============================================

def main():
    print("="*60)
    print("MENTAL HEALTH DATA EXTRACTOR")
    print("="*60)
    
    # Extract
    extractor = MentalHealthDataExtractor('/workspaces/workspaces/.devcontainer/morbidity/data/age specific morbility.xlsx')
    extractor.load()
    data = extractor.extract()
    # Debug: Check what's in your data
    print("Data columns:", data.columns.tolist())
    print("Total cases sum:", data['total_cases'].sum())
    print("Total male sum:", data['total_male'].sum())
    print("Total female sum:", data['total_female'].sum())

    # Check first few rows
    print(data[['total_cases', 'total_male', 'total_female']].head(10)) 
    # Quick summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total cases: {data['total_cases'].sum():,}")
    print(f"Unique diagnoses: {data['diagnosis'].nunique()}")
    print(f"Months: {data['month'].nunique()}")
    
    # Save to CSV
    data.to_csv('extracted_mental_health_data.csv', index=False)
    print("\n✅ Saved to: extracted_mental_health_data.csv")
    
    # Show first few rows
    print("\nFirst 5 records:")
    print(data.head()[['month', 'diagnosis', 'total_male', 'total_female', 'total_cases']])


if __name__ == "__main__":
    main()