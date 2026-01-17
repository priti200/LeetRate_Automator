import requests

# Test a few usernames from the CSV
test_usernames = ['chaos4peace', 'teja_bulusu', 'U4AIE23061', 'adarshs05']

API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

for username in test_usernames:
    url = f"{API_BASE_URL}/{username}/contest"
    try:
        response = requests.get(url, timeout=10)
        print(f"\n{'='*60}")
        print(f"Username: {username}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Rating: {data.get('contestRating', 'N/A')}")
            print(f"Global Rank: {data.get('contestGlobalRanking', 'N/A')}")
            print(f"Attended: {data.get('contestAttend', 'N/A')}")
            print(f"Top %: {data.get('contestTopPercentage', 'N/A')}")
            print(f"\nAll fields in response:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
