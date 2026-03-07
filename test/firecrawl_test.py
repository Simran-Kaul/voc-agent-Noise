import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

url = "https://www.flipkart.com/noise-master-buds-sound-bose-49db-anc-6-mic-enc-44-hr-battery-spatial-audio-bluetooth/product-reviews/itm1cb4f0cb9d57a"

result = app.scrape(url)

print(result)