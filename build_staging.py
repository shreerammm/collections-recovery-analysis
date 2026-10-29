
from pathlib import Path
import pandas as pd

root = Path.cwd()
staging_dir = root / "data_staging"
review_dir = root / "data_rejected_review"

staging_dir.mkdir(exist_ok=True)
review_dir.mkdir(exist_ok=True)

report = []

for file in sorted(root.glob("*.csv")):
    try:
        df = pd.read_csv(file, low_memory=False)

        # Separate exact duplicate rows, keeping one copy in staging.
        duplicate_mask = df.duplicated(keep="first")
        staging_df = df.loc[~duplicate_mask].copy()
        review_df = df.loc[duplicate_mask].copy()

        staging_df.to_csv(staging_dir / file.name, index=False)
        review_df.to_csv(review_dir / file.name, index=False)

        report.append({
            "file": file.name,
            "original_rows": len(df),
            "exact_duplicate_excess_rows": int(duplicate_mask.sum()),
            "staging_rows": len(staging_df),
            "review_rows": len(review_df),
        })

        print(
            f"{file.name}: {len(df):,} original rows | "
            f"{int(duplicate_mask.sum()):,} exact duplicates flagged | "
            f"{len(staging_df):,} staging rows"
        )

    except Exception as error:
        print(f"ERROR processing {file.name}: {error}")

if report:
    report_df = pd.DataFrame(report)
    report_df.to_csv(root / "staging_audit_report.csv", index=False)

    print("\nStaging build complete.")
    print(f"Original CSVs unchanged: {len(report)} files processed.")
    print(f"Audit report: {root / 'staging_audit_report.csv'}")
    print(f"Staging folder: {staging_dir}")
    print(f"Review folder: {review_dir}")
