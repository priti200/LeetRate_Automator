import csv
import os
from config import LEADERBOARD_TOP

def format_leaderboard(results):
    rated = [r for r in results if r["success"] and r["rating"] > 0]
    rated.sort(key=lambda x: x["rating"], reverse=True)

    unrated_count = len(results) - len(rated)
    total = len(results)

    lines = ["🏆 *LeetCode Leaderboard*\n"]

    medals = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(rated[:LEADERBOARD_TOP]):
        name = r["name"] or r["leetcode_username"]
        if i < 3:
            prefix = medals[i]
        else:
            prefix = f"{i + 1}."
        lines.append(f"{prefix} {name} — {r['rating']} | Rank: #{r['global_rank']:,}")

    if len(rated) > LEADERBOARD_TOP:
        lines.append(f"... and {len(rated) - LEADERBOARD_TOP} more")

    successful = len(rated)
    avg_rating = sum(r["rating"] for r in rated) / len(rated) if rated else 0
    top_rating = rated[0]["rating"] if rated else 0

    lines.append("")
    lines.append(f"📊 {successful}/{total} fetched | Avg: {avg_rating:.0f} | Top: {int(top_rating)}")
    if unrated_count > 0:
        lines.append(f"⚠️ {unrated_count} unrated/failed")

    return "\n".join(lines)

def format_stats(stats, last_fetch):
    lines = ["📈 *Fetch Statistics*\n"]
    lines.append(f"✅ Successful: {stats.get('successful', 0)}")
    lines.append(f"❌ Failed: {stats.get('total', 0) - stats.get('successful', 0)}")
    avg = stats.get("avg_rating")
    if avg:
        lines.append(f"📊 Average Rating: {avg:.1f}")
    top = stats.get("top_rating")
    if top:
        lines.append(f"🏅 Top Rating: {int(top)}")
    if last_fetch:
        lines.append(f"\n🕒 Last fetch: {last_fetch}")
    return "\n".join(lines)

def format_student_list(students):
    if not students:
        return "📭 No students registered."
    lines = [f"👥 *Students ({len(students)})*\n"]
    for s in students:
        status = "✅" if s["active"] else "⏸️"
        lines.append(f"{status} {s['name'] or s['leetcode_username']} — `{s['leetcode_username']}`")
    return "\n".join(lines)

def generate_csv_file(results, filepath):
    rated = [r for r in results if r["success"] and r["rating"] > 0]
    rated.sort(key=lambda x: x["rating"], reverse=True)

    unrated = [r for r in results if not r["success"] or r["rating"] == 0]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Name", "Roll Number", "Username", "Rating", "Global Rank", "Contests Attended", "Top %", "Status"])
        rank = 1
        for r in rated:
            writer.writerow([
                rank,
                r.get("name", ""),
                r.get("roll_number", ""),
                r["leetcode_username"],
                r["rating"],
                r["global_rank"],
                r["contests_attended"],
                f"{r['top_pct']:.1f}%",
                "Success"
            ])
            rank += 1
        for r in unrated:
            writer.writerow([
                "-",
                r.get("name", ""),
                r.get("roll_number", ""),
                r["leetcode_username"],
                0,
                0,
                0,
                "0.0%",
                "Unrated/Failed"
            ])

    return filepath
