import sqlite3
from collections import Counter


def generate_global_report():

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT product, sentiment, themes, product_action, marketing_action, support_action
    FROM reviews
    WHERE scraped_at >= datetime('now', '-2 hours')
    """)

    rows = cursor.fetchall()

    sentiments = []
    themes = []
    product_actions = []
    marketing_actions = []
    support_actions = []

    for r in rows:

        sentiments.append(r[0])

        if r[1]:
            themes.extend(r[1].split(","))

        if r[2]:
            product_actions.append(r[2])

        if r[3]:
            marketing_actions.append(r[3])

        if r[4]:
            support_actions.append(r[4])

    sentiment_count = Counter(sentiments)
    theme_count = Counter(themes)

    report = []

    report.append("# Voice of Customer Global Report\n")
    report.append("# VoC Delta Report (Last 2 Hours)\n")

    report.append("## Sentiment Summary\n")
    for k, v in sentiment_count.items():
        report.append(f"{k}: {v}")

    report.append("\n## Top Mentioned Themes\n")
    for theme, count in theme_count.most_common(5):
        report.append(f"{theme}: {count}")

    report.append("\n## Product Team Action Items\n")
    for a in product_actions[:5]:
        report.append(f"- {a}")

    report.append("\n## Marketing Team Action Items\n")
    for a in marketing_actions[:5]:
        report.append(f"- {a}")

    report.append("\n## Support Team Action Items\n")
    for a in support_actions[:5]:
        report.append(f"- {a}")

    with open("global_voc_report.md", "w") as f:
        f.write("\n".join(report))

    conn.close()

    print("Global VoC report generated: global_voc_report.md")

def generate_delta_report():

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT review, sentiment, themes
    FROM reviews
    WHERE scraped_at >= datetime('now', '-7 days')
    """)

    rows = cursor.fetchall()

    report = []

    report.append("# Weekly Review Delta\n")

    report.append(f"Total new reviews captured: {len(rows)}\n")

    for r in rows[:10]:
        report.append(f"- {r[0][:200]}")

    with open("weekly_delta_report.md", "w") as f:
        f.write("\n".join(report))
    
    report.append("\n## Key Insight\n")

    if theme_count:
        top_theme = theme_count.most_common(1)[0][0]
        report.append(f"Most discussed issue this week: {top_theme}")

    conn.close()

    print("Weekly delta report generated: weekly_delta_report.md")


if __name__ == "__main__":
    generate_global_report()
    generate_delta_report()
    