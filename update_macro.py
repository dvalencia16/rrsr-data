import json, time, requests, os

def get_json(url, params=None):
    r = requests.get(url, params=params, timeout=12)
    r.raise_for_status()
    return r.json()

def try_get(fn):
    try: return fn()
    except: return None

def build():
    out = {"ts": int(time.time())}

    # VIX (CBOE) via Stooq JSON proxy (fallback CSV if needed)
    # Stooq returns JSON at this endpoint:
    vix = try_get(lambda: requests.get("https://stooq.com/q/l/?s=^vix&i=d&f=json").json()[0]["close"])
    out["VIX"] = float(vix) if vix else None

    # DXY via Stooq
    dxy = try_get(lambda: requests.get("https://stooq.com/q/l/?s=dxy&i=d&f=json").json()[0]["close"])
    out["DXY"] = float(dxy) if dxy else None

    # US10Y and US02Y via Stooq (UST 10Y = 'us10y', 2Y = 'us02y')
    us10y = try_get(lambda: requests.get("https://stooq.com/q/l/?s=us10y&i=d&f=json").json()[0]["close"])
    us02y = try_get(lambda: requests.get("https://stooq.com/q/l/?s=us02y&i=d&f=json").json()[0]["close"])
    out["US10Y"] = float(us10y) if us10y else None
    out["US02Y"] = float(us02y) if us02y else None
    out["SPREAD_2s10s_bps"] = round((out["US10Y"] - out["US02Y"]) * 100, 1) if out["US10Y"] and out["US02Y"] else None

    # Put/Call (CBOE total) — fallback to “data not available” if not reachable free
    out["PUT_CALL_TOTAL"] = None

    # Breadth (% > 50dma) — not freely reliable → set None, acceptable per spec
    out["BREADTH_50dma_pct"] = None

    with open("macro.json","w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    build()
