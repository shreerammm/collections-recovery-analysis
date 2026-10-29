
import duckdb
from pathlib import Path
import re

project_root = Path(__file__).resolve().parent.parent
sql_file = project_root / "sql" / "recovery_analysis.sql"
output_folder = project_root / "quality_reports"
output_folder.mkdir(exist_ok=True)

connection = duckdb.connect()
sql_text = sql_file.read_text(encoding="utf-8")

# Remove SQL comments
sql_text = re.sub(r"--.*", "", sql_text)

queries = [
    query.strip()
    for query in sql_text.split(";")
    if query.strip()
]

for i, query in enumerate(queries, start=1):
    print(f"\n{'=' * 12} QUERY {i} {'=' * 12}")

    try:
        result = connection.execute(query).df()

        output_file = output_folder / f"query_{i}_results.csv"
        result.to_csv(output_file, index=False)

        print(f"Saved to: {output_file}")
        print(result.to_string(index=False))

    except Exception as error:
        print(f"Error: {error}")

connection.close()
