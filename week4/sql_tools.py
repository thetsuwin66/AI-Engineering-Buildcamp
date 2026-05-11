import os
import urllib.request

import duckdb

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
PARQUET_FILE = "yellow_tripdata_2024-01.parquet"

con = duckdb.connect("taxi.db")


def setup_database():
    """Download the parquet file and load it into DuckDB."""
    if not os.path.exists(PARQUET_FILE):
        print(f"Downloading {DATA_URL}...")
        urllib.request.urlretrieve(DATA_URL, PARQUET_FILE)

    con.execute(f"""
        CREATE TABLE IF NOT EXISTS trips AS
        SELECT * FROM '{PARQUET_FILE}'
    """)
    count = con.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
    print(f"Loaded {count} rows")
    return count


class SQLTools:
    def get_schema(self) -> str:
        """Get the schema of the trips table with column names and types."""
        result = con.execute("DESCRIBE trips").fetchall()
        return "\n".join([f"{row[0]}: {row[1]}" for row in result])

    def run_sql(self, query: str) -> str:
        """Execute a SQL query and return results as text (limited to 50 rows)."""
        try:
            cursor = con.execute(query)
            rows = cursor.fetchmany(50)
            if not rows:
                return "No results"
            cols = [desc[0] for desc in cursor.description]
            lines = [" | ".join(cols)]
            lines.extend([" | ".join(str(v) for v in row) for row in rows])
            return "\n".join(lines)
        except Exception as e:
            return f"SQL Error: {e}"


if __name__ == "__main__":
    count = setup_database()
    print(f"Row count: {count}")
