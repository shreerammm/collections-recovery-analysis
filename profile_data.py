
from pathlib import Path
import pandas as pd

# Find CSV files in this project, including subfolders.
project = Path.cwd()
excluded = {".venv", "venv", ".git", "__pycache__"}

csv_files = [
    p for p in project.rglob("*.csv")
    if not any(part in excluded for part in p.parts)
]

if not csv_files:
    print("No CSV files found. Check that VS Code opened the correct folder.")
else:
    print(f"Found {len(csv_files)} CSV files\n")

    for file in sorted(csv_files):
        print("=" * 70)
        print(f"FILE: {file.relative_to(project)}")

        try:
            df = pd.read_csv(file, low_memory=False)

            print(f"Rows: {len(df):,}")
            print(f"Columns: {len(df.columns)}")
            print("Column names:")
            print(", ".join(map(str, df.columns)))

            print(f"Exact duplicate rows: {df.duplicated().sum():,}")

            missing = df.isna().sum()
            missing = missing[missing > 0]

            if missing.empty:
                print("Missing values: none detected")
            else:
                print("Missing values by column:")
                for column, count in missing.items():
                    percentage = count / len(df) * 100 if len(df) else 0
                    print(f"  {column}: {count:,} ({percentage:.2f}%)")

        except Exception as error:
            print(f"Could not inspect this file: {error}")

print("\nProfiling complete. No source files were modified.")
