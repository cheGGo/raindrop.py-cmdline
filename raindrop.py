#!/usr/bin/env python3

import argparse
import asyncio
import aiohttp
import datetime
import json
from pprint import pprint 
import config as cfg

def load_token():
    """ Load the current token from a file. """
    with open(cfg.TOKEN_FILE, 'r') as file:
        return json.load(file)

def save_token(token_data):
    """ Save the token data to a file. """
    with open(cfg.TOKEN_FILE, 'w') as file:
        json.dump(token_data, file)

async def refresh_access_token(refresh_token):
    """ Refresh the access token using the refresh token. """
    async with aiohttp.ClientSession() as session:
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': cfg.CLIENT_ID,
            'client_secret': cfg.CLIENT_SECRET
        }
        async with session.post(cfg.TOKEN_URL, data=payload) as response:
            if response.status == 200:
                data = await response.json()
                # Calculate the new expiration time
                expires_at = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'])
                data['expires_at'] = expires_at.timestamp()  # Convert to Unix timestamp
                save_token(data)
                return data
            else:
                raise Exception("Could not refresh access-token. please re-generate access-token")

async def get_bookmarks(search):
    """ Get bookmarks from Raindrop.io based on the search query. """
    token_data = load_token()
    access_token = token_data['access_token']
    expires_at = datetime.datetime.fromtimestamp(token_data['expires'])  # Convert from Unix timestamp

    # Check if the token needs to be refreshed
    if datetime.datetime.now() >= expires_at:
        token_data = await refresh_access_token(token_data['refresh_token'])
        access_token = token_data['access_token']

    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"search": search, "perpage": 50}
        async with session.get("https://api.raindrop.io/rest/v1/raindrops/0", headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return f"Error: {response.status}"

async def main():
    """ Main function to handle command line arguments and call the get_bookmarks function. """
    parser = argparse.ArgumentParser(description="Search bookmarks on Raindrop.io.")
    parser.add_argument("--search", type=str, required=True, help="Search pattern for bookmarks.")
    args = parser.parse_args()

    bookmarks = await get_bookmarks(args.search)
    pprint(bookmarks)

if __name__ == "__main__":
    asyncio.run(main())
