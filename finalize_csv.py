import csv

FILENAME = 'new_batch_ratings.csv'

def main():
    print(f"Finalizing {FILENAME}...")
    rows = []
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except FileNotFoundError:
        print("File not found")
        return

    # Helper to get rating safely
    def get_rating_val(r):
        try:
            val = r.get('Rating', 0)
            if val == '-' or val == '': return 0
            return int(val)
        except:
            return 0

    # Sort: Rating (Desc), then Name (Asc)
    rows.sort(key=lambda x: (get_rating_val(x), x['Name']), reverse=True)
    
    # Assign Ranks
    rank = 1
    # Since we sorted desc, valid ratings are at top. 
    # But reverse=True puts Z names first? No, tuple sort: (Rating DESC, Name ASC) is tricky with single reverse.
    # Let's simple sort by Rating Desc first. Stable sort helps.
    
    rows.sort(key=lambda x: get_rating_val(x), reverse=True)

    success_count = 0
    for row in rows:
        rating = get_rating_val(row)
        if rating > 0:
            row['Rank'] = rank
            row['Status'] = 'Success' # Ensure status is correct
            rank += 1
            success_count += 1
        else:
            row['Rank'] = '-'
            # If status isn't set, set it
            if not row.get('Status'):
                row['Status'] = 'Failed'

    # Save
    with open(FILENAME, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done! File sorted and ranked.")
    print(f"Final Count: {success_count} successful students.")

if __name__ == "__main__":
    main()
