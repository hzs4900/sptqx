import os, re, html, urllib.request, urllib.parse

CHANNEL = "hezu2"
STATE = "last_id.txt"

def match(text):
    t = text.lower()
    return "#spotify" in t and ("尼日利亚" in text or "🇳🇬" in text)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

def posts(page):
    out = {}
    parts = re.split(r'data-post="%s/(\d+)"' % CHANNEL, page)
    for i in range(1, len(parts), 2):
        pid = int(parts[i]); body = parts[i + 1]
        m = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', body, re.S)
        raw = m.group(1) if m else ""
        raw = re.sub(r"<br\s*/?>", "\n", raw)
        out[pid] = html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()
    return out

def push(pid, text):
    key = os.environ["BARK_KEY"].strip()
    title = "hezu2：Spotify 尼日利亚"
    body = text[:300]
    url = "https://api.day.app/%s/%s/%s?%s" % (
        key, urllib.parse.quote(title, safe=""), urllib.parse.quote(body, safe=""),
        urllib.parse.urlencode({"url": "https://t.me/%s/%d" % (CHANNEL, pid),
                                "level": "timeSensitive", "group": "hezu2"}))
    print(urllib.request.urlopen(url, timeout=30).read().decode())

test = os.environ.get("TEST_POST", "").strip()
if test:
    p = posts(fetch("https://t.me/s/%s/%s" % (CHANNEL, test)))
    t = p.get(int(test), "")
    print("TEST", test, "match =", match(t)); print(t)
    if match(t): push(int(test), t)
    raise SystemExit

p = posts(fetch("https://t.me/s/%s" % CHANNEL))
if not p: raise SystemExit("页面没解析到帖子")
last = int(open(STATE).read()) if os.path.exists(STATE) else max(p)
for pid in sorted(x for x in p if x > last):
    if match(p[pid]):
        print("HIT", pid); push(pid, p[pid])
open(STATE, "w").write(str(max(max(p), last)))
print("last =", max(max(p), last))
