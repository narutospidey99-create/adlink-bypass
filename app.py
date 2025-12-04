import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.diudemy.com/"
}

def parse_hidden(html, name):
    try:
        soup = BeautifulSoup(html, "html.parser")
        el = soup.find("input", {"name": name})
        return el["value"] if el else ""
    except:
        return ""

def bypass_adlink(original_url):
    if "link.adlink.click" not in original_url:
        return {"success": False, "error": "Invalid Adlink URL"}

    mapped = original_url.replace("link.adlink.click", "blog.adlink.click")

    session = requests.Session()

    try:
        r1 = session.get(mapped, headers=HEADERS, timeout=15)
    except Exception as e:
        return {"success": False, "error": str(e)}

    html = r1.text

    if 'name="ad_form_data"' not in html:
        return {"success": False, "error": "ad_form_data not found (layout changed)"}

    ad_form_data = parse_hidden(html, "ad_form_data")
    _csrfToken = parse_hidden(html, "_csrfToken")
    token_fields = parse_hidden(html, "_Token[fields]")
    token_unlocked = parse_hidden(html, "_Token[unlocked]")

    time.sleep(5)

    post_data = {
        "_method": "POST",
        "_csrfToken": _csrfToken,
        "ad_form_data": ad_form_data,
        "_Token[fields]": token_fields,
        "_Token[unlocked]": token_unlocked
    }

    r2 = session.post(
        "https://blog.adlink.click/links/go",
        data=post_data,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": mapped,
            "Accept": "application/json,text/javascript,*/*;q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    )

    try:
        json_data = r2.json()
    except:
        return {"success": False, "error": "Invalid JSON"}

    if "url" not in json_data:
        return {"success": False, "error": "URL not found in response"}

    if "limit.php" in json_data["url"]:
        return {"success": False, "error": "Shortlink limit reached"}

    return {"success": True, "url": json_data["url"]}


@app.route("/")
def home():
    return "Adlink Bypass API Working!"

@app.route("/bypass")
def bypass():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"success": False, "error": "URL parameter missing"}), 400

    result = bypass_adlink(url)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
