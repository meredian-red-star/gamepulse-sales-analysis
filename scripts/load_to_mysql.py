"""Load the cleaned CSV into MySQL. The CSV files are never changed.

Install dependencies: python -m pip install pandas sqlalchemy 'pymysql[rsa]'
Start a local MySQL server before running this script.
Set MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE
in your environment. Defaults below are local examples, not real credentials.
The account needs permission to create the database/table and read/write rows.

Run: python scripts/load_to_mysql.py
To deliberately replace existing table data: python scripts/load_to_mysql.py --replace
"""

import argparse
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace", action="store_true",
        help="Replace all existing video_game_sales rows with the cleaned CSV.",
    )
    args = parser.parse_args()

    project_folder = Path(__file__).resolve().parent.parent
    sales = pd.read_csv(
        project_folder / "data" / "vgsales_clean.csv",
        dtype={"Rank": "int64", "Year": "int64"},
    )

    database = os.getenv("MYSQL_DATABASE", "gamepulse")
    # URL.create safely handles special characters in usernames and passwords.
    server_url = URL.create(
        "mysql+pymysql",
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        username=os.getenv("MYSQL_USER", "gamepulse_user"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        query={"charset": "utf8mb4"},
    )

    # Reuse the SQL file so the script and manual setup create the same schema.
    server = create_engine(server_url, connect_args={"connect_timeout": 10})
    try:
        quoted_database = server.dialect.identifier_preparer.quote_identifier(database)
        schema = (project_folder / "sql" / "create_table.sql").read_text()
        schema = schema.replace("`gamepulse`", quoted_database)
        with server.connect() as connection:
            for statement in schema.split(";"):
                if statement.strip():
                    connection.exec_driver_sql(statement)
    finally:
        server.dispose()

    engine = create_engine(
        server_url.set(database=database), connect_args={"connect_timeout": 10}
    )
    try:
        # A transaction restores the previous rows if an insert fails.
        with engine.begin() as connection:
            existing_rows = connection.execute(
                text("SELECT COUNT(*) FROM `video_game_sales`")
            ).scalar_one()
            if existing_rows and not args.replace:
                raise ValueError(
                    "The table already contains data. Use --replace only if you "
                    "want to replace all existing rows with this CSV."
                )
            if args.replace:
                connection.execute(text("DELETE FROM `video_game_sales`"))

            # Append preserves the SQL-defined primary key and column types.
            sales.to_sql(
                "video_game_sales", connection, if_exists="append",
                index=False, chunksize=1000, method="multi",
            )
            loaded_rows = connection.execute(
                text("SELECT COUNT(*) FROM `video_game_sales`")
            ).scalar_one()
            if loaded_rows != len(sales):
                raise ValueError("Loaded row count does not match the cleaned CSV.")
        print(f"Loaded {loaded_rows:,} rows into {database}.video_game_sales.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
