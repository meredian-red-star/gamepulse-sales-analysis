"""Create five sales charts from MySQL without changing database data.

Requires pandas, sqlalchemy, pymysql[rsa], and matplotlib.
Set MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE
as for load_to_mysql.py, then run: python scripts/analyze_from_mysql.py
The database must already contain the video_game_sales table and data.
"""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def save_chart(fig, output_folder, filename):
    fig.savefig(output_folder / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def bar_chart(data, category, title, output_folder, filename):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(data[category], data["total_global_sales"], color="#2878A5")
    ax.invert_yaxis()
    ax.set(title=title, xlabel="Global sales (millions of units)", ylabel=category)
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_chart(fig, output_folder, filename)


def main():
    url = URL.create(
        "mysql+pymysql",
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        username=os.getenv("MYSQL_USER", "gamepulse_user"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "gamepulse"),
        query={"charset": "utf8mb4"},
    )
    engine = create_engine(url, connect_args={"connect_timeout": 10})
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("START TRANSACTION READ ONLY")
            genres = pd.read_sql(text("""
                SELECT `Genre`, SUM(`Global_Sales`) AS total_global_sales
                FROM `video_game_sales` GROUP BY `Genre`
                ORDER BY total_global_sales DESC, `Genre`
            """), connection)
            platforms = pd.read_sql(text("""
                SELECT `Platform`, SUM(`Global_Sales`) AS total_global_sales
                FROM `video_game_sales` GROUP BY `Platform`
                ORDER BY total_global_sales DESC, `Platform` LIMIT 10
            """), connection)
            publishers = pd.read_sql(text("""
                SELECT `Publisher`, SUM(`Global_Sales`) AS total_global_sales
                FROM `video_game_sales` GROUP BY `Publisher`
                ORDER BY total_global_sales DESC, `Publisher` LIMIT 10
            """), connection)
            years = pd.read_sql(text("""
                SELECT `Year`, SUM(`Global_Sales`) AS total_global_sales
                FROM `video_game_sales` GROUP BY `Year` ORDER BY `Year`
            """), connection)
            regions = pd.read_sql(text("""
                SELECT `Genre`, SUM(`NA_Sales`) AS NA,
                       SUM(`EU_Sales`) AS EU, SUM(`JP_Sales`) AS JP
                FROM `video_game_sales` GROUP BY `Genre`
                ORDER BY SUM(`NA_Sales` + `EU_Sales` + `JP_Sales`) DESC, `Genre`
            """), connection)
    finally:
        engine.dispose()

    if genres.empty:
        raise ValueError("No sales rows found. Load the cleaned dataset first.")

    output_folder = Path(__file__).resolve().parent.parent / "images"
    output_folder.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False})

    charts = [
        (genres, "Genre", "Total Global Sales by Genre", "global_sales_by_genre.png"),
        (platforms, "Platform", "Top 10 Platforms by Global Sales", "top_platforms.png"),
        (publishers, "Publisher", "Top 10 Publishers by Global Sales", "top_publishers.png"),
    ]
    for data, category, title, filename in charts:
        bar_chart(data, category, title, output_folder, filename)
        leader = data.iloc[0]
        print(f"{category}: {leader[category]} leads with "
              f"{leader['total_global_sales']:,.2f} million units globally.")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years["Year"], years["total_global_sales"], color="#2878A5", marker="o")
    ax.set(title="Global Sales by Release Year", xlabel="Release year",
           ylabel="Global sales (millions of units)", ylim=(0, None))
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
    ax.grid(alpha=0.2)
    fig.tight_layout()
    save_chart(fig, output_folder, "global_sales_by_year.png")
    peak = years.loc[years["total_global_sales"].idxmax()]
    print(f"Year: {int(peak['Year'])} has the highest global sales total at "
          f"{peak['total_global_sales']:,.2f} million units (grouped by release year).")

    fig, ax = plt.subplots(figsize=(12, 7))
    positions = list(range(len(regions)))
    for offset, region, color in [(-0.25, "NA", "#2878A5"),
                                  (0, "EU", "#E69F00"),
                                  (0.25, "JP", "#31966F")]:
        ax.bar([p + offset for p in positions], regions[region],
               width=0.25, label=region, color=color)
    ax.set_xticks(positions, regions["Genre"], rotation=45, ha="right")
    ax.set(title="Genre Sales Comparison: NA, EU, and JP", xlabel="Genre",
           ylabel="Sales (millions of units)")
    ax.legend(title="Region")
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_chart(fig, output_folder, "genre_sales_by_region.png")
    leaders = []
    for region in ["NA", "EU", "JP"]:
        leader = regions.loc[regions[region].idxmax()]
        leaders.append(f"{region}: {leader['Genre']} ({leader[region]:,.2f} million)")
    print("Leading genres by region: " + "; ".join(leaders) + ".")
    print(f"Saved 5 PNG charts to {output_folder}")


if __name__ == "__main__":
    main()
