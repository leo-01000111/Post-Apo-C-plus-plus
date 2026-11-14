#!/usr/bin/env python3
"""Download top 5000 [c++] Stack Overflow questions + answers via Stack Exchange API v2.3.
Standard library only. Resumable via raw-response cache. Run from the kit root."""
import gzip, hashlib, html, json, os, sys, time, datetime
import urllib.request, urllib.error

API = "https://api.stackexchange.com/2.3"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "7_stackoverflow")
CACHE = os.path.join(OUT, "cache")
BUDGET = 120
os.makedirs(CACHE, exist_ok=True)

state = {"used": 0, "quota": None, "backoff": 0}

class Stop(Exception):
    pass

def get(path_query):
    url = API + path_query
    key = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ".json")
    if os.path.exists(key):
        with open(key, encoding="utf-8") as f:
            return json.load(f)
    if state["used"] >= BUDGET:
        raise Stop("request budget reached")
    if state["quota"] is not None and state["quota"] < 20:
        raise Stop("quota_remaining < 20")
    if state["backoff"]:
        time.sleep(state["backoff"]); state["backoff"] = 0
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "offline-study-kit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
        print("HTTP error", e.code, raw[:300])
        try:
            d = json.loads(raw)
            print("error_id:", d.get("error_id"), d.get("error_name"), d.get("error_message"))
        except Exception:
            pass
        raise Stop("HTTP %s" % e.code)
    state["used"] += 1
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    d = json.loads(raw.decode("utf-8"))
    if "error_id" in d:
        print("API error_id:", d["error_id"], d.get("error_name"), d.get("error_message"))
        raise Stop("error_id %s" % d["error_id"])
    state["quota"] = d.get("quota_remaining", state["quota"])
    state["backoff"] = d.get("backoff", 0)
    with open(key, "w", encoding="utf-8") as f:
        json.dump(d, f)
    time.sleep(0.2)
    return d

def status(msg):
    print("%s | requests used: %d | quota_remaining: %s" % (msg, state["used"], state["quota"]), flush=True)

def main():
    questions = {}   # qid -> dict (ordered)
    answers = {}     # qid -> best answer dict
    stopped = None
    try:
        # Step 1 (keyless API allows page <= 25, so continue with max=<last score> windows)
        maxq = ""
        seg_page = 0
        total_pages = 0
        while len(questions) < 5000 and total_pages < 56:
            seg_page += 1
            total_pages += 1
            d = get("/questions?order=desc&sort=votes&tagged=c%%2B%%2B&pagesize=100&page=%d%s&filter=withbody&site=stackoverflow" % (seg_page, maxq))
            items = d.get("items", [])
            for q in items:
                questions.setdefault(q["question_id"], q)
            status("questions page %d (%d total)" % (total_pages, len(questions)))
            if items:
                last_score = items[-1]["score"]
            if not d.get("has_more") or not items:
                break
            if seg_page >= 25:
                maxq = "&max=%d" % last_score
                seg_page = 0
        questions = dict(list(questions.items())[:5000])
        # Step 2
        acc = [q for q in questions.values() if q.get("accepted_answer_id")]
        acc_ids = [q["accepted_answer_id"] for q in acc]
        by_aid = {}
        for i in range(0, len(acc_ids), 100):
            batch = acc_ids[i:i+100]
            d = get("/answers/%s?filter=withbody&site=stackoverflow&pagesize=100" % ";".join(map(str, batch)))
            for a in d.get("items", []):
                by_aid[a["answer_id"]] = a
            status("accepted answers batch %d/%d" % (i//100+1, (len(acc_ids)+99)//100))
        for q in acc:
            a = by_aid.get(q["accepted_answer_id"])
            if a:
                answers[q["question_id"]] = (a, True)
        # Step 3
        noacc = [qid for qid, q in questions.items() if not q.get("accepted_answer_id")]
        nb = (len(noacc) + 99) // 100
        if state["used"] + nb * 2 > BUDGET:
            # allow if one page per batch fits, else skip
            pages = 1 if state["used"] + nb <= BUDGET else 0
        else:
            pages = 2
        print("Step 3: %d questions without accepted answer, %d batches, %d page(s)/batch" % (len(noacc), nb, pages))
        best = {}
        for i in range(0, len(noacc) if pages else 0, 100):
            batch = noacc[i:i+100]
            for p in range(1, pages + 1):
                d = get("/questions/%s/answers?order=desc&sort=votes&filter=withbody&site=stackoverflow&pagesize=100&page=%d" % (";".join(map(str, batch)), p))
                for a in d.get("items", []):
                    cur = best.get(a["question_id"])
                    if cur is None or a["score"] > cur["score"]:
                        best[a["question_id"]] = a
                status("top answers batch %d/%d page %d" % (i//100+1, nb, p))
                if not d.get("has_more"):
                    break
        for qid, a in best.items():
            answers[qid] = (a, False)
    except Stop as e:
        stopped = str(e)
        print("STOPPED:", stopped)

    # Output (also on partial progress)
    path = os.path.join(OUT, "qa.jsonl")
    n_ans = 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for qid, q in questions.items():
            a, accepted = answers.get(qid, (None, False))
            if a: n_ans += 1
            rec = {
                "qid": qid,
                "title": html.unescape(q.get("title", "")),
                "tags": q.get("tags", []),
                "score": q.get("score", 0),
                "link": q.get("link", ""),
                "q_author": q.get("owner", {}).get("display_name", ""),
                "q_html": q.get("body", ""),
                "a_id": a["answer_id"] if a else None,
                "a_score": a["score"] if a else None,
                "a_author": a.get("owner", {}).get("display_name") if a else None,
                "a_html": a.get("body") if a else None,
                "accepted": bool(a and accepted),
                "created": q.get("creation_date", 0),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    today = datetime.date.today().isoformat()
    with open(os.path.join(OUT, "ATTRIBUTION.md"), "w", encoding="utf-8") as f:
        f.write("# Attribution\n\nContent from Stack Overflow (https://stackoverflow.com), "
                "licensed CC BY-SA (2.5/3.0/4.0 depending on post date; see https://stackoverflow.com/help/licensing).\n\n"
                "Each entry in `qa.jsonl` keeps its `link` and author names (`q_author`, `a_author`).\n\n"
                "Fetched on %s via the Stack Exchange API (https://api.stackexchange.com/2.3).\n" % today)
    print("\nSUMMARY")
    print("questions:", len(questions), "| with answer:", n_ans)
    print("qa.jsonl size: %d bytes (%.1f MB)" % (os.path.getsize(path), os.path.getsize(path)/1e6))
    print("requests used this run:", state["used"], "| quota_remaining:", state["quota"])
    if stopped:
        print("run was stopped early:", stopped, "(re-run to resume from cache)")

main()
