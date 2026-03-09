import sqlite3
from collections import Counter
import os
from datetime import datetime


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
            products[product]["themes"].extend([t.strip() for t in r[2].split(",")])
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
        seen = set()
        count = 0
        for a in data["product_actions"]:
            if a not in seen and count < 5:
                report.append(f"- {a}")
                seen.add(a)
                count += 1

        report.append("\n### Marketing Team Action Items\n")
        seen = set()
        count = 0
        for a in data["marketing_actions"]:
            if a not in seen and count < 5:
                report.append(f"- {a}")
                seen.add(a)
                count += 1

        report.append("\n### Support Team Action Items\n")
        seen = set()
        count = 0
        for a in data["support_actions"]:
            if a not in seen and count < 5:
                report.append(f"- {a}")
                seen.add(a)
                count += 1

    os.makedirs("reports", exist_ok=True)
    with open("reports/global_voc_report.md", "w") as f:
        f.write("\n".join(report))

    conn.close()
    print("Global VoC report generated: global_voc_report.md")


def generate_delta_report():
    conn = sqlite3.connect("data/reviews.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT product, review, sentiment, themes, product_action, marketing_action, support_action
    FROM reviews
    WHERE scraped_at >= datetime('now', '-2 hour')
    """)
    rows = cursor.fetchall()

    products = {}
    for r in rows:
        product = r[0]
        if product not in products:
            products[product] = {
                "reviews": [],
                "sentiments": [],
                "themes": [],
                "product_actions": [],
                "marketing_actions": [],
                "support_actions": []
            }
        products[product]["reviews"].append(r[1])
        if r[2]:
            products[product]["sentiments"].append(r[2])
        if r[3]:
            products[product]["themes"].extend([t.strip() for t in r[3].split(",")])
        if r[4]:
            products[product]["product_actions"].append(r[4])
        if r[5]:
            products[product]["marketing_actions"].append(r[5])
        if r[6]:
            products[product]["support_actions"].append(r[6])

    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = []
    report.append(f"# Weekly Review Delta\n")
    report.append(f"Run: {run_timestamp}\n")

    for product, data in products.items():
        sentiment_count = Counter(data["sentiments"])
        theme_count = Counter(data["themes"])

        report.append(f"\n## {product}\n")
        report.append(f"New reviews captured: {len(data['reviews'])}\n")

        report.append("### Sentiment Distribution\n")
        for k, v in sentiment_count.items():
            report.append(f"{k}: {v}")

        report.append("\n### Emerging Themes\n")
        for theme, count in theme_count.most_common(3):
            report.append(f"{theme}: {count}")

        report.append("\n### Sample Reviews\n")
        for r in data["reviews"][:5]:
            if r:
                report.append(f"- {r[:200]}")

        report.append("\n### Product Team Action Items\n")
        seen = set()
        count = 0
        for a in data["product_actions"]:
            if a not in seen and count < 3:
                report.append(f"- {a}")
                seen.add(a)
                count += 1

        report.append("\n### Marketing Team Action Items\n")
        seen = set()
        count = 0
        for a in data["marketing_actions"]:
            if a not in seen and count < 3:
                report.append(f"- {a}")
                seen.add(a)
                count += 1

        report.append("\n### Support Team Action Items\n")
        seen = set()
        count = 0
        for a in data["support_actions"]:
            if a not in seen and count < 3:
                report.append(f"- {a}")
                seen.add(a)
                count += 1

    report.append("\n---\n")

    os.makedirs("reports", exist_ok=True)
    file_path = "reports/weekly_delta_analyse_report.md"

    # Append to existing file so each run is logged
    with open(file_path, "w") as f:
        f.write("\n".join(report))

    conn.close()
    print("Weekly delta report generated: weekly_delta_analyse_report.md")


if __name__ == "__main__":
    generate_global_report()
    generate_delta_report()