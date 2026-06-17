from pathlib import Path
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "age specific morbility.xlsx"

# Allow running this file directly while still importing the db package.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


class MentalHealthDataExtractor:
    """Extract age-specific morbidity data from the Excel workbook."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.raw_data = None
        self.processed_data = None

    def load(self):
        """Load the workbook into memory."""
        self.raw_data = pd.read_excel(self.file_path, sheet_name=0, header=None)
        print(f"Loaded: {self.raw_data.shape[0]} rows, {self.raw_data.shape[1]} columns")
        return self

    def extract(self):
        """Extract the workbook into normalized records."""
        records = []
        current_month = None

        for i, row in self.raw_data.iterrows():
            values = ["" if pd.isna(cell) else str(cell).strip() for cell in row.tolist()]

            # Detect month headers like 'MONTH: JULY 2024'
            if values and values[0].upper().startswith("MONTH:"):
                current_month = values[0].split(":", 1)[1].strip()
                continue

            # Detect header rows.
            if values and values[0] == "NO." and values[1] == "DIAGNOSIS":
                continue
            if values and values[0] == "" and values[1] == "" and values[2] == "M":
                continue

            # Skip rows that are clearly not data.
            if len(values) < 2:
                continue
            if values[0].isdigit() is False:
                continue

            diagnosis = values[1]
            if not diagnosis or diagnosis.upper() in {"TOTAL", "GRAND TOTAL"}:
                continue

            # Map age-group columns to M/F pairs.
            age_pairs = {
                "0-9": (2, 3),
                "10-18": (4, 5),
                "19-24": (6, 7),
                "25-34": (8, 9),
                "35-64": (10, 11),
                "65+": (12, 13),
                "U/Age": (14, 15),
                "TOTAL": (16, 17),
            }

            for age_group, (male_col, female_col) in age_pairs.items():
                male_value = self._clean_number(values[male_col]) if male_col < len(values) else 0
                female_value = self._clean_number(values[female_col]) if female_col < len(values) else 0

                if male_value == 0 and female_value == 0:
                    continue

                records.append(
                    {
                        "month": current_month or "UNKNOWN",
                        "diagnosis": diagnosis,
                        "age_group": age_group,
                        "gender": "M",
                        "count": male_value,
                    }
                )
                records.append(
                    {
                        "month": current_month or "UNKNOWN",
                        "diagnosis": diagnosis,
                        "age_group": age_group,
                        "gender": "F",
                        "count": female_value,
                    }
                )

        self.processed_data = pd.DataFrame(records)
        print(f"\n✅ Extracted {len(self.processed_data)} total records")
        return self.processed_data

    def _clean_number(self, value):
        if value is None or value == "":
            return 0
        if isinstance(value, str):
            value = value.replace(",", "").strip()
            if value == "":
                return 0
            try:
                return int(float(value))
            except ValueError:
                return 0
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0


def main():
    print("=" * 60)
    print("MENTAL HEALTH DATA EXTRACTOR")
    print("=" * 60)

    extractor = MentalHealthDataExtractor(DATA_FILE)
    extractor.load()
    data = extractor.extract()

    print("Data columns:", data.columns.tolist())
    print("First 10 rows:")
    print(data.head(10))

    # Save a CSV for quick inspection if needed.
    csv_path = BASE_DIR / "extracted_mental_health_data.csv"
    data.to_csv(csv_path, index=False)
    print(f"\n✅ Saved to: {csv_path}")

    # Store the extracted data in the database.
    from db.dbOperations import create_tables, insert_records

    create_tables()
    records = [
        (row["month"], row["diagnosis"], row["age_group"], row["gender"], int(row["count"]))
        for _, row in data.iterrows()
    ]
    inserted = insert_records(records)
    print(f"\n✅ Inserted {inserted} records into the database")


if __name__ == "__main__":
    main()