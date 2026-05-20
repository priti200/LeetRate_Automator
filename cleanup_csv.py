
import os

INPUT_CSV = 'final_leetcode_results.csv'
OUTPUT_CSV = 'final_leetcode_results_cleaned.csv'
HEADER = 'Student Name,Student Roll Number,Student LeetCode Username,Fetched LeetCode Rating,Fetched LeetCode Level\n'

unique_usernames = set()
valid_lines = []

if os.path.exists(INPUT_CSV):
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                parts = line.split(',')
                # Expect at least 5 parts. 
                # Note: Name might have commas? The original script used pandas default which quotes fields if needed.
                # But my data doesn't seem to have commas in names based on inspection.
                # If name has comma, this split might fail. 
                # Let's assume standard format for now or just check if it looks like a data row.
                
                # Check if it's a header
                if 'Student LeetCode Username' in line:
                    continue
                
                # Check minimum length (username is 3rd, rating 4th, level 5th)
                if len(parts) < 5:
                    continue
                
                # Extract username (3rd column usually, but if name has comma it shifts)
                # However, LeetCode username is unique.
                # Let's try to be smart. Level is last column. Rating is 2nd last.
                # Username is 3rd last?
                # No, "Student Name, Roll, Username, Rating, Level"
                # If name has comma: "Name, Surname", Roll, Username, Rating, Level
                
                # Let's assume the script generated standard CSV without quoting unless needed.
                # Inspecting previous output: "BULUSU VENKATA SAI TEJA,AM.SC.U4CSE23312,teja_bulusu,1423.16,None"
                # No quotes.
                
                # username is index 2.
                username = parts[2]
                
                # If duplicate, skip
                if username in unique_usernames:
                    continue
                
                unique_usernames.add(username)
                valid_lines.append(line + '\n')
        
        with open(OUTPUT_CSV, 'w', encoding='utf-8') as f:
            f.write(HEADER)
            f.writelines(valid_lines)
            
        print(f"Recovered {len(valid_lines)} records.")
        
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Input file not found.")
