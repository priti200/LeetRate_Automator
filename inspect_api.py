
import requests
import json

def fetch_user_data(username):
    url = 'https://leetcode.com/graphql'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/json',
        'Referer': 'https://leetcode.com/'
    }
    
    # Query to inspect available data
    query = """
    query userContestRankingInfo($username: String!) {
        userContestRanking(username: $username) {
            rating
            globalRanking
            badge {
                name
            }
        }
        userProfileUserQuestionProgressV2(userSlug: $username) {
            numAcceptedQuestions {
                count
                difficulty
            }
        }
    } 
    """
    
    payload = {
        'query': query,
        'variables': {'username': username}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

# Test with a user likely to have a badge or at least data
fetch_user_data('neal_wu') 
