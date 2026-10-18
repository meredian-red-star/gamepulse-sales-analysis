# gamepulse-sales-analysis
Video game sales and market analysis using Python, Pandas, MySQL, and data visualization.

Install dependencies from the project root:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` in the project root and enter your local MySQL
connection settings. Both database scripts load this optional file automatically,
even when run from another directory. Existing environment variables take priority.
Keep passwords in your local `.env` file, which Git ignores; never commit it.

With MySQL running and your account configured:

```bash
python scripts/load_to_mysql.py
python scripts/analyze_from_mysql.py
```

The loader creates the database/table and imports the cleaned CSV. It refuses to
overwrite existing rows unless you explicitly pass `--replace`. The analysis script
only reads the database and saves five charts in `images/`.
