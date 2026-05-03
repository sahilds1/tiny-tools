#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "stravalib==2.4",
# ]
# ///

# Output Strava activity to analyze in a Chat conversation

import argparse

from stravalib import Client

def main():
    
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("activity_id", type=int, help = "")
    args = parser.parse_args()
    
    activity_id = args.activity_id
    
    # TODO: Check if there is a stored access token and if it has expired
    # TODO: Refresh the access token if the access token has expired and there is a refresh token 
    
    # The resulting access_token is valid until the specified expiration time; for Strava, this time is 6 hours, specified as unix epoch seconds. 
    # You can see the expiration time by looking at the expires_at field of the returned token.
    
    # You can store this token value to access the account data in the future without requiring re-authorization. 
    # However, you must refresh the token after the 6-hour expiration period.
    # # token_response = client.refresh_access_token(
    #     client_id=MY_STRAVA_CLIENT_ID,
    #     client_secret=MY_STRAVA_CLIENT_SECRET,
    #     refresh_token=last_refresh_token,
    # )
    # new_access_token = token_response["access_token"]
    
    
    # TODO: Authenticate if there is not a stored access token or refresh token  
    client = Client()
    # TODO: Read the client_id and client secret from enviornment variables
    url = client.authorization_url(client_id=, redirect_uri="http://127.0.0.1:5000/authorization")
    
    # TODO:  Once you have the URL value, you can display it in your web application to allow athletes
    # to authorize your application to read their data. If you are trying to authenticate locally, 
    # paste the URL into your browser to support exchanging the temporary code Strava provides for a temporary access token.
    # https://stravalib.readthedocs.io/en/v2.2/get-started/authenticate-with-strava.html
    
    # TODO: Read the client_id and client secret from enviornment variables
    # TODO: Print the url and read the code after the user has pasted it into the command line
    token_response = client.exchange_code_for_token(client_id=, client_secret=, code=)

    access_token = token_response["access_token"]
    refresh_token = token_response['refresh_token']
    
    client = Client(access_token=access_token)

    # TODO: Add typing for activity stravalib.model.DetailedActivity 
    activity = client.get_activity(activity_id, include_all_efforts=True)

    print(activity)

if __name__ == "__main__":
    main()
