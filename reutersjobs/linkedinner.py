import csv
import os
import random
import string
import webbrowser
from urllib.parse import parse_qs, urlparse

import click
import requests
from rich import print

from . import utils


@click.group()
def cli():
    """Work with the LinkedIn API."""
    pass


@cli.command()
def get_user_info():
    """Get user information from LinkedIn."""
    access_token = auth()
    response = requests.get(
        "https://api.linkedin.com/v2/me", headers=get_headers(access_token)
    )
    user_info = response.json()
    print(user_info)


@cli.command()
def get_access_token():
    """Get access token from LinkedIn."""
    access_token = get_token(force=True)
    print("\nACCESS TOKEN:\n")
    print(access_token)


@cli.command()
def post():
    """Post new jobs to LinkedIn."""
    data = list(csv.DictReader(open(utils.DATA_DIR / "clean" / "additions.csv")))
    print(f"Posting {len(data)} listings")

    # Common config for all posts
    access_token = auth()
    api_url = "https://api.linkedin.com/v2/ugcPosts"
    company_name = "Reuters"
    company_id = "17821482"
    company_urn = f"urn:li:organization:{company_id}"

    # For each listing ...
    for obj in data:
        # Upload the image
        image_path = utils.DATA_DIR / "img" / f"{obj['id']}.png"
        asset_id = upload_image(image_path)

        # Draft the message
        message = f"New job at {company_name}: {obj['title']} in {obj['city']}\n\n Apply now at {obj['url']}"

        # Post the message
        post_data = {
            "author": get_author_urn(),
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "attributes": [
                            {
                                "length": len(company_name),
                                "start": find_position(company_name, message),
                                "value": {
                                    "com.linkedin.common.CompanyAttributedEntity": {
                                        "company": company_urn
                                    }
                                },
                            }
                        ],
                        "text": message,
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": message},
                            "media": asset_id,
                            "originalUrl": obj["url"],
                            "title": {
                                "text": f"New job at {company_name}: {obj['title']} in {obj['city']}"
                            },
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        print(f"Posting {obj['title']}")
        requests.post(api_url, headers=get_headers(access_token), json=post_data)


#
# Utilities
#


def get_creds():
    """Get credentials from environment."""
    creds = {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
        "redirect_uri": "http://localhost:8080/",
        "user_id": os.getenv("LINKEDIN_USER_ID"),
    }
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if access_token:
        creds["access_token"] = access_token
    return creds


def auth():
    """Authenticate with the LinkedIn API."""
    return get_token()


def create_csrf_token():
    """Generate a random string of letters."""
    letters = string.ascii_lowercase
    token = "".join(random.choice(letters) for i in range(20))
    return token


def find_position(mention_name, message):
    """Find position of mentioned name in the message."""
    index = 0
    if mention_name in message:
        c = mention_name[0]
        for ch in message:
            if ch == c:
                if message[index : index + len(mention_name)] == mention_name:
                    return index
            index += 1
    return -1


def get_author_urn():
    """Get the LinkedIn urn for the user that will post."""
    creds = get_creds()
    return f'urn:li:person:{creds["user_id"]}'


def upload_image(path):
    """Upload the provided image."""
    # Register image
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": get_author_urn(),
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    access_token = auth()
    headers = get_headers(access_token)
    print("Registering image upload")
    register_r = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=headers,
        json=register_payload,
    )
    assert register_r.ok
    register_data = register_r.json()
    upload_url = register_data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset_id = register_data["value"]["asset"]

    # Upload image
    print(f"Uploading {path} to {asset_id}")
    with open(path, "rb") as img_file:
        upload_r = requests.post(upload_url, data=img_file, headers=headers)
    assert upload_r.ok

    # Return the asset id
    return asset_id


def get_auth_code(api_url, client_id, client_secret, redirect_uri):
    """
    Make a HTTP request to the authorization URL and return token.

    It will open the authentication URL. Once authorized, it'll redirect to
    the redirect URI given. The page will look like an error. but it is not.
    You'll need to copy the redirected URL.
    """
    api_url = "https://www.linkedin.com/oauth/v2"
    # Request authentication URL
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": create_csrf_token(),
        "scope": "r_liteprofile,r_emailaddress,w_member_social",
    }
    r = requests.get(f"{api_url}/authorization", params=params)
    webbrowser.open(r.url)

    # Get the authorization verifier code from the callback url
    redirect_response = input("Paste the full redirect URL here:")
    url = urlparse(redirect_response)
    url = parse_qs(url.query)
    return url["code"][0]


def get_headers(access_token):
    """Make the headers to attach to the API call."""
    return {
        "Authorization": f"Bearer {access_token}",
        "cache-control": "no-cache",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def refresh_token(auth_code, client_id, client_secret, redirect_uri):
    """Exchange a Refresh Token for a New Access Token."""
    access_token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    r = requests.post(access_token_url, data=data, timeout=30)
    assert r.ok
    return r.json()["access_token"]


def get_token(force=False):
    """Run the authentication routine.

    If the access token exists, it will use it to skip browser auth.

    If not, it will open the browser for you to authenticate. You will have to manually paste the redirect URI in the prompt.
    """
    creds = get_creds()
    if "access_token" not in creds.keys() or force:
        args = creds["client_id"], creds["client_secret"], creds["redirect_uri"]
        api_url = "https://www.linkedin.com/oauth/v2"
        auth_code = get_auth_code(api_url, *args)
        access_token = refresh_token(auth_code, *args)
        creds.update({"access_token": access_token})
    else:
        access_token = creds["access_token"]
    return access_token


if __name__ == "__main__":
    cli()
