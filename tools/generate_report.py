
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
91    conn = sqlite3.connect("data/reviews.db")
92    cursor = conn.cursor()
93    cursor.execute("""
94    SELECT product, review, sentiment, themes, product_action, marketing_action, support_action
95    FROM reviews
96    WHERE scraped_at >= datetime('now', '-1 minute')
97    """)
98    rows = cursor.fetchall()
99
100    products = {}
101    for r in rows:
102        product = r[0]
103        if product not in products:
104            products[product] = {
105                "reviews": [],
106                "sentiments": [],
107                "themes": [],
108                "product_actions": [],
109                "marketing_actions": [],
110                "support_actions": []
111            }
112        products[product]["reviews"].append(r[1])
113        if r[2]:
114            products[product]["sentiments"].append(r[2])
115        if r[3]:
116            products[product]["themes"].extend([t.strip() for t in r[3].split(",")])
117        if r[4]:
118            products[product]["product_actions"].append(r[4])
119        if r[5]:
120            products[product]["marketing_actions"].append(r[5])
121        if r[6]:
122            products[product]["support_actions"].append(r[6])
123
124    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
125
126    report = []
127    report.append(f"# Weekly Review Delta\n")
128    report.append(f"Run: {run_timestamp}\n")
129
130    for product, data in products.items():
131        sentiment_count = Counter(data["sentiments"])
132        theme_count = Counter(data["themes"])
133
134        report.append(f"\n## {product}\n")
135        report.append(f"New reviews captured: {len(data['reviews'])}\n")
136
137        report.append("### Sentiment Distribution\n")
138        for k, v in sentiment_count.items():
139            report.append(f"{k}: {v}")
140
141        report.append("\n### Emerging Themes\n")
142        for theme, count in theme_count.most_common(3):
143            report.append(f"{theme}: {count}")
144
145        report.append("\n### Sample Reviews\n")
146        for r in data["reviews"][:5]:
147            if r:
148                report.append(f"- {r[:200]}")
149
150        report.append("\n### Product Team Action Items\n")
151        seen = set()
152        count = 0
153        for a in data["product_actions"]:
154            if a not in seen and count < 3:
155                report.append(f"- {a}")
156                seen.add(a)
157                count += 1
158
159        report.append("\n### Marketing Team Action Items\n")
160        seen = set()
161        count = 0
162        for a in data["marketing_actions"]:
163            if a not in seen and count < 3:
164                report.append(f"- {a}")
165                seen.add(a)
166                count += 1
167
168        report.append("\n### Support Team Action Items\n")
169        seen = set()
170        count = 0
171        for a in data["support_actions"]:
172            if a not in seen and count < 3:
173                report.append(f"- {a}")
174                seen.add(a)
175                count += 1
176
177    report.append("\n---\n")
178
179    os.makedirs("reports", exist_ok=True)
180    file_path = "reports/weekly_delta_analyse_report.md"
181
182    # Append to existing file so each run is logged
183    with open(file_path, "a") as f:
184        f.write("\n".join(report))
185
186    conn.close()
187    print("Weekly delta report generated: weekly_delta_analyse_report.md")
188

if __name__ == "__main__":
    generate_global_report()
    generate_delta_report()