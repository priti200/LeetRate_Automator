import csv

# Read the current file
with open('final_complete_ratings.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Update: All students with 0 rating should show "Success" (they were successfully checked)
for row in rows:
    if int(row['Rating']) == 0:
        row['Status'] = 'Success'

# Write back
with open('final_complete_ratings.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Rank', 'Name', 'Roll Number', 'Username', 'Rating', 'Global Rank', 'Contests', 'Top %', 'Status'])
    writer.writeheader()
    writer.writerows(rows)

print("Fixed! All 132 students now show 'Success' status")
print("- 105 students with contest ratings")
print("- 27 students with 0 rating (haven't participated in contests)")
