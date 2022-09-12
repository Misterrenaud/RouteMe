import json
import logging
import os
import time

import requests as requests

with open("conf.json") as fp:
    conf = json.load(fp)


def get_access_token() -> str:
    client_id = conf["client_id"]
    client_secret = conf["client_secret"]

    # to copy from https://www.strava.com/settings/api for the first setup
    access_token = conf["access_token"]
    refresh_token = conf["refresh_token"]

    strava_token_file = "strava_tokens.json"
    expired = True

    if os.path.exists(strava_token_file):
        with open(strava_token_file) as json_file:
            strava_tokens = json.load(json_file)
        refresh_token = strava_tokens['refresh_token']
        expired = strava_tokens['expires_at'] < time.time()
        access_token = strava_tokens["access_token"]

    if expired:
        logging.debug("Renewing Strava access token")
        response = requests.post(
            url='https://www.strava.com/oauth/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        strava_tokens = response.json()
        with open(strava_token_file, 'w') as outfile:
            json.dump(strava_tokens, outfile)
        access_token = strava_tokens["access_token"]

    return access_token
