import requests
import time
from .config import FETCH_DELAY, FETCH_MAX_RETRIES, FETCH_BACKOFF_BASE

class LeetCodeFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com/"
        })

    def fetch_single(self, username):
        query = """
        query userContestRankingInfo($username: String!) {
            userContestRanking(username: $username) {
                rating
                globalRanking
                attendedContestsCount
                badge {
                    name
                }
            }
        }
        """
        payload = {
            "query": query,
            "variables": {"username": username}
        }

        for attempt in range(FETCH_MAX_RETRIES):
            try:
                resp = self.session.post("https://leetcode.com/graphql", json=payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    ranking = data.get("data", {}).get("userContestRanking")
                    if ranking and ranking.get("rating") is not None:
                        return {
                            "rating": round(float(ranking["rating"]), 2),
                            "global_rank": int(ranking.get("globalRanking", 0)),
                            "contests_attended": int(ranking.get("attendedContestsCount", 0)),
                            "top_pct": 0.0,
                            "badge": (ranking.get("badge") or {}).get("name", ""),
                            "success": True
                        }
                    return {"rating": 0, "global_rank": 0, "contests_attended": 0, "top_pct": 0.0, "badge": "", "success": False}
                elif resp.status_code == 429:
                    wait = FETCH_BACKOFF_BASE * (2 ** attempt)
                    time.sleep(wait)
                else:
                    time.sleep(FETCH_DELAY)
            except Exception:
                time.sleep(FETCH_DELAY)

        return {"rating": 0, "global_rank": 0, "contests_attended": 0, "top_pct": 0.0, "badge": "", "success": False}

    def fetch_all(self, students, progress_callback=None):
        results = []
        total = len(students)
        for idx, student in enumerate(students):
            username = student["leetcode_username"]
            data = self.fetch_single(username)
            data["student_id"] = student["id"]
            data["name"] = student["name"]
            data["roll_number"] = student["roll_number"]
            data["leetcode_username"] = username
            results.append(data)

            if progress_callback and (idx + 1) % 10 == 0 or idx + 1 == total:
                progress_callback(idx + 1, total, data["success"])

            time.sleep(FETCH_DELAY)

        return results
