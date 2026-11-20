import os

import requests
from dotenv import load_dotenv


def main():
    load_dotenv()

    token = os.getenv("HUBSPOT_ACCESS_TOKEN")

    if not token:
        raise RuntimeError(
            "HUBSPOT_ACCESS_TOKEN is missing from your .env file."
        )

    url = "https://api.hubapi.com/crm/v3/objects/deals"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    params = {
        "limit": 100,
        "properties": "dealname,amount,dealstage,closedate",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

    except requests.exceptions.HTTPError:
        print(f"HubSpot API returned HTTP {response.status_code}")

        if response.status_code == 401:
            print("Authentication failed. Check your app access token.")

        elif response.status_code == 403:
            print("Permission denied. Check the app's CRM read scopes.")

        else:
            print("The request failed. Check the HubSpot app configuration.")

        raise

    data = response.json()

    deals = data.get("results", [])

    print("\nHubSpot connection successful!")
    print(f"Deals retrieved: {len(deals)}")

    for deal in deals:
        properties = deal.get("properties", {})

        print("\n------------------------------")
        print(f"Deal ID: {deal.get('id')}")
        print(f"Name: {properties.get('dealname')}")
        print(f"Amount: {properties.get('amount')}")
        print(f"Stage: {properties.get('dealstage')}")
        print(f"Close date: {properties.get('closedate')}")


if __name__ == "__main__":
    main()