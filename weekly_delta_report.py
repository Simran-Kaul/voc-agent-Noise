import sqlite3
from collections import Counter


def generate_weekly_delta_report():

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    # get recently analyzed reviews
    cursor.execute("""
        SELECT sentiment, themes
        FROM reviews
        WHERE sentiment IS NOT NULL
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    sentiments = []
    themes = []

    for r in rows:

        sentiments.append(r[0])

        if r[1]:
            themes.extend(r[1].split(","))

    sentiment_count = Counter(sentiments)
    theme_count = Counter(themes)

    report = []

    report.append("# Weekly VoC Delta Report\n")

    report.append("## Recent Sentiment Distribution\n")

    for k, v in sentiment_count.items():
        report.append(f"{k}: {v}")

    report.append("\n## Emerging Themes\n")

    for theme, count in theme_count.most_common(5):
        report.append(f"{theme}: {count}")

    report.append("\n## Potential Product Issues\n")

    negative_themes = [t for t in themes]

    negative_counts = Counter(negative_themes)

    for theme, count in negative_counts.most_common(3):

        report.append(f"- Investigate {theme} related complaints")

    with open("weekly_delta_report.md", "w") as f:
        f.write("\n".join(report))

    conn.close()

    print("Weekly delta report generated: weekly_delta_report.md")


if __name__ == "__main__":
    generate_weekly_delta_report()