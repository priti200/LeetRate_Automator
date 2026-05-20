
import pandas as pd
import requests
import time
import os
import sys

# Configuration
INPUT_EXCEL_FILE = 'CP handles(1-468).xlsx'
INTERMEDIATE_CSV = 'students_input.csv'
OUTPUT_CSV = 'final_complete_results.csv'
BATCH_SIZE = 5
BATCH_DELAY_SECONDS = 10  # Increased for rate limit safety
MAX_RETRIES = 3

class LeetCodePipeline:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
            'Referer': 'https://leetcode.com/'
        }

    def convert_excel_to_csv(self):
        """Converts the input Excel file to a standardized CSV."""
        print(f"Reading {INPUT_EXCEL_FILE}...")
        try:
            df = pd.read_excel(INPUT_EXCEL_FILE)
            
            # Map columns based on inspection
            # Found from previous inspection:
            # 4: Name
            # 6: Roll number
            # 9: Leetcode handle
            
            # Create a clean DataFrame
            clean_df = pd.DataFrame()
            clean_df['Student Name'] = df.iloc[:, 4]
            clean_df['Student Roll Number'] = df.iloc[:, 6]
            
            # Clean usernames (remove URL prefixes if present)
            def clean_username(u):
                u = str(u).strip()
                if 'leetcode.com/u/' in u:
                    return u.split('leetcode.com/u/')[-1].strip('/').split('/')[0]
                if 'leetcode.com/' in u:
                    return u.split('leetcode.com/')[-1].strip('/').split('/')[0]
                return u

            clean_df['Student LeetCode Username'] = df.iloc[:, 9].apply(clean_username)
            
            # Remove rows with empty usernames
            clean_df = clean_df.dropna(subset=['Student LeetCode Username'])
            clean_df['Student LeetCode Username'] = clean_df['Student LeetCode Username'].astype(str).str.strip()
            # Filter out placeholder text if any (simple check)
            clean_df = clean_df[clean_df['Student LeetCode Username'] != 'nan']
            
            clean_df.to_csv(INTERMEDIATE_CSV, index=False)
            print(f"Converted to {INTERMEDIATE_CSV}. Total records: {len(clean_df)}")
            return clean_df
        except Exception as e:
            print(f"Error converting Excel: {e}")
            sys.exit(1)

    def fetch_leetcode_data(self, username):
        """Fetches rating and badge level for a given username."""
        query = """
        query userContestRankingInfo($username: String!) {
            userContestRanking(username: $username) {
                rating
                globalRanking
                badge {
                    name
                }
            }
        } 
        """
        
        url = 'https://leetcode.com/graphql'
        payload = {
            'query': query,
            'variables': {'username': username}
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'errors' in data:
                        return None, None, None
                        
                    ranking = data.get('data', {}).get('userContestRanking')
                    
                    rating = 0.0
                    level = "Unrated"
                    
                    if ranking:
                        rating = round(ranking.get('rating', 0), 2)
                        global_rank = ranking.get('globalRanking', 0)
                        
                        # Get official badge if available
                        badge = ranking.get('badge')
                        if badge and badge.get('name'):
                            level = badge.get('name')
                        else:
                            # Fallback if no badge but has rating
                            if rating > 0:
                                level = "Participant"
                            else:
                                level = "Unrated"
                    else:
                        global_rank = 0
                    
                    return rating, global_rank, level
                elif response.status_code == 429:
                    print(f"Rate limited (429). Sleeping for 30s...")
                    time.sleep(30)
                else:
                    pass
            except Exception as e:
                print(f"Exception fetching {username}: {e}")
                time.sleep(2)
        
        return None, None, None

    def run(self):
        # 1. Prepare Data
        if not os.path.exists(INTERMEDIATE_CSV):
            df = self.convert_excel_to_csv()
        else:
            print(f"Found existing {INTERMEDIATE_CSV}, using it.")
            df = pd.read_csv(INTERMEDIATE_CSV)
        
        # 2. Load Existing Progress
        processed_users = set()
        if os.path.exists(OUTPUT_CSV):
            try:
                existing_df = pd.read_csv(OUTPUT_CSV)
                processed_users = set(existing_df['Student LeetCode Username'].astype(str))
                print(f"Resuming... {len(processed_users)} students already processed.")
            except Exception:
                print("Could not read existing output file. Starting fresh.")
        else:
            # Create header
            pd.DataFrame(columns=['Student Name', 'Student Roll Number', 'Student LeetCode Username', 'Fetched LeetCode Rating', 'Fetched LeetCode Global Rank', 'Fetched LeetCode Level']).to_csv(OUTPUT_CSV, index=False)
        
        # 3. Process Loop
        batch = []
        students_to_process = df[~df['Student LeetCode Username'].astype(str).isin(processed_users)]
        
        total_to_process = len(students_to_process)
        print(f"Total students remaining to process: {total_to_process}")
        
        count = 0
        for index, row in students_to_process.iterrows():
            name = row['Student Name']
            roll = row['Student Roll Number']
            username = str(row['Student LeetCode Username']).strip()
            
            print(f"Processing ({count+1}/{total_to_process}): {username}")
            
            # Fetch Data
            rating, global_rank, level = self.fetch_leetcode_data(username)
            
            # Handle result
            result_row = {
                'Student Name': name,
                'Student Roll Number': roll,
                'Student LeetCode Username': username,
                'Fetched LeetCode Rating': rating if rating is not None else "Not Found/Error",
                'Fetched LeetCode Global Rank': global_rank if global_rank is not None else "N/A",
                'Fetched LeetCode Level': level if level is not None else "N/A"
            }
            batch.append(result_row)
            count += 1
            
            # Batch Save
            if len(batch) >= BATCH_SIZE:
                self.save_batch(batch)
                batch = []
                print(f"Batch saved. Sleeping for {BATCH_DELAY_SECONDS}s...")
                time.sleep(BATCH_DELAY_SECONDS)
        
        # Save remaining
        if batch:
            self.save_batch(batch)
            print("Final batch saved.")
            
        print("Processing Complete!")

    def save_batch(self, batch_data):
        """Append batch to the CSV file."""
        df = pd.DataFrame(batch_data)
        df.to_csv(OUTPUT_CSV, mode='a', header=False, index=False)

if __name__ == "__main__":
    pipeline = LeetCodePipeline()
    pipeline.run()
