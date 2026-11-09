"""
GITHUB FOLLOWER MANAGER SCRIPT
==============================
This script helps you manage your GitHub following list manually.
It will automatically follow back anyone who follows you, and unfollow 
anyone who doesn't follow you back (excluding Organizations).

HOW TO GET YOUR GITHUB TOKEN (Step-by-Step):
1. Go to GitHub.com and log in to your account.
2. Click on your profile picture in the top-right corner and select 'Settings'.
3. Scroll down the left sidebar and click on 'Developer settings'.
4. Click on 'Personal access tokens', then select 'Tokens (classic)'.
5. Click on the 'Generate new token' button -> 'Generate new token (classic)'.
6. In the 'Note' field, give it a name (e.g., 'ManualFollowerBot').
7. Set an expiration date (or choose 'No expiration').
8. Under 'Select scopes', check ONLY the box named 'user' 
   (this will automatically include 'read:user', 'user:email', and 'user:follow').
9. Scroll to the bottom and click 'Generate token'.
10. COPY the generated token immediately (it usually starts with 'ghp_'). 
    You will not be able to see it again!
11. Paste the copied token inside the quotes for the TOKEN variable below.
"""

import requests
import time

# PASTE YOUR GITHUB TOKEN HERE INSIDE THE QUOTES
TOKEN = "PASTE_YOUR_TOKEN_HERE"

# Set up the headers for GitHub API authentication
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

BASE_URL = "https://api.github.com"

def get_paginated_list(endpoint):
    """
    Fetches all results from a GitHub API endpoint, handling pagination 
    if you have a lot of followers/following.
    """
    results = []
    url = f"{BASE_URL}{endpoint}"
    
    while url:
        response = requests.get(url, headers=HEADERS)
        
        # Check if the token is invalid or expired
        if response.status_code == 401:
            print("ERROR: Invalid or expired token. Please check your TOKEN variable.")
            exit()
            
        response.raise_for_status()
        results.extend(response.json())
        
        # Get the URL for the next page, if it exists
        url = response.links.get("next", {}).get("url")
        
    return results

def main():
    print("Fetching your followers and following lists. Please wait...")
    
    # Get the list of people who follow you and people you follow
    followers = get_paginated_list("/user/followers")
    following = get_paginated_list("/user/following")

    # Extract usernames for faster lookups
    follower_logins = {user['login'] for user in followers}
    
    # Create a dictionary for following to access user type (User vs Organization)
    following_dict = {user['login']: user for user in following}

    print("\n--- PHASE 1: FOLLOWING USERS WHO FOLLOW YOU ---")
    for follower in followers:
        username = follower['login']
        
        # If they follow us, but we don't follow them yet
        if username not in following_dict:
            print(f"Following: {username}...")
            res = requests.put(f"{BASE_URL}/user/following/{username}", headers=HEADERS)
            
            if res.status_code == 204:
                print(f"  -> Successfully followed {username}!")
            else:
                print(f"  -> Failed to follow {username} (Status code: {res.status_code})")
                
            # Short pause to prevent hitting GitHub API rate limits
            time.sleep(1)

    print("\n--- PHASE 2: UNFOLLOWING USERS WHO DON'T FOLLOW BACK ---")
    for username, user_data in following_dict.items():
        
        # If we follow them, but they don't follow us AND they are not an Organization
        is_not_follower = username not in follower_logins
        is_not_organization = user_data.get('type') != 'Organization'
        
        if is_not_follower and is_not_organization:
            print(f"Unfollowing: {username}...")
            res = requests.delete(f"{BASE_URL}/user/following/{username}", headers=HEADERS)
            
            if res.status_code == 204:
                print(f"  -> Successfully unfollowed {username}!")
            else:
                print(f"  -> Failed to unfollow {username} (Status code: {res.status_code})")
                
            # Short pause to prevent hitting GitHub API rate limits
            time.sleep(1)

    print("\nAll done! Your GitHub followers are now synchronized.")

if __name__ == "__main__":
    # Prevent the script from running if the token is missing or hasn't been changed
    if TOKEN == "PASTE_YOUR_TOKEN_HERE" or not TOKEN:
        print("ERROR: You forgot to paste your GitHub token!")
        print("Please read the instructions at the top of the file and paste your token in the TOKEN variable.")
    else:
        main()