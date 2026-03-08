
import sqlite3
from collections import Counter
import os


def generate_global_report():

    conn = sqlite3.connect("data/reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT product, sentiment, themes, product_action, marketing_action, support_action
    FROM reviews
    """)

    rows = cursor.fetchall()

    products = {}

    for r in rows:

        product = r[0]

        if product not in products:
            products[product] = {
                "sentiments": [],
                "themes": [],
                "product_actions": [],
                "marketing_actions": [],
                "support_actions": []
            }

        if r[1]:
            products[product]["sentiments"].append(r[1])

        if r[2]:
            products[product]["themes"].extend(r[2].split(","))

        if r[3]:
            products[product]["product_actions"].append(r[3])

        if r[4]:
            products[product]["marketing_actions"].append(r[4])

        if r[5]:
            products[product]["support_actions"].append(r[5])

    report = []

    report.append("# Voice of Customer Global Report\n")

    for product, data in products.items():

        sentiment_count = Counter(data["sentiments"])
        theme_count = Counter(data["themes"])

        report.append(f"\n## {product}\n")

        report.append("### Sentiment Summary\n")
        for k, v in sentiment_count.items():
            report.append(f"{k}: {v}")

        report.append("\n### Top Mentioned Themes\n")
        for theme, count in theme_count.most_common(5):
            report.append(f"{theme}: {count}")

        report.append("\n### Product Team Action Items\n")
        for a in data["product_actions"][:5]:
            report.append(f"- {a}")

        report.append("\n### Marketing Team Action Items\n")
        for a in data["marketing_actions"][:5]:
            report.append(f"- {a}")

        report.append("\n### Support Team Action Items\n")
        for a in data["support_actions"][:5]:
            report.append(f"- {a}")

    with open("reports/global_voc_report.md", "w") as f:
        f.write("\n".join(report))

    conn.close()

    print("Global VoC report generated: global_voc_report.md")


def generate_delta_report():

    conn = sqlite3.connect("data/reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT product, review, sentiment, themes
    FROM reviews
    WHERE scraped_at >= datetime('now', '-1 minute')
    """)

    rows = cursor.fetchall()

    products = {}

    for r in rows:

        product = r[0]

        if product not in products:
            products[product] = {
                "reviews": [],
                "sentiments": [],
                "themes": []
            }

        products[product]["reviews"].append(r[1])

        if r[2]:
            products[product]["sentiments"].append(r[2])

        if r[3]:
            products[product]["themes"].extend(r[3].split(","))

    report = []

    report.append("# Weekly Review Delta\n")

    for product, data in products.items():

        report.append(f"\n## {product}\n")

        report.append(f"New reviews captured: {len(data['reviews'])}\n")

        sentiment_count = Counter(data["sentiments"])
        theme_count = Counter(data["themes"])

        report.append("### Sentiment Distribution\n")
        for k, v in sentiment_count.items():
            report.append(f"{k}: {v}")

        report.append("\n### Emerging Themes\n")
        for theme, count in theme_count.most_common(3):
            report.append(f"{theme}: {count}")

        report.append("\n### Sample Reviews\n")
        for r in data["reviews"][:5]:
            report.append(f"- {r[:200]}")
    
    file_path = "reports/weekly_delta_analyse_report.md"

    os.path.exists(file_path)
    with open("reports/weekly_delta_analyse_report.md", "w") as f:
        f.write("\n".join(report))

    conn.close()

    print("Weekly delta report generated: weekly_delta_report.md")

if __name__ == "__main__":
    generate_global_report()
    generate_delta_report()