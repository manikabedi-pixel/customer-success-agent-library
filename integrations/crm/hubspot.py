import os

import requests
from dotenv import load_dotenv


class HubSpotCRMAdapter:
    """
    Read-only adapter for retrieving HubSpot CRM records.

    This adapter does not create, update, or delete CRM data.
    """

    BASE_URL = "https://api.hubapi.com"

    def __init__(self, access_token=None):
        load_dotenv()

        self.access_token = access_token or os.getenv(
            "HUBSPOT_ACCESS_TOKEN"
        )

        if not self.access_token:
            raise ValueError(
                "HUBSPOT_ACCESS_TOKEN is missing."
            )

        self.session = requests.Session()

        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        })

    def _get(self, endpoint, params=None):
        """Make an authenticated, read-only GET request."""

        response = self.session.get(
            f"{self.BASE_URL}{endpoint}",
            params=params,
            timeout=20,
        )

        response.raise_for_status()

        return response.json()

    def get_deal(self, deal_id):
        """Retrieve one HubSpot deal by ID."""

        return self._get(
            f"/crm/v3/objects/deals/{deal_id}",
            params={
                "properties": (
                    "dealname,amount,dealstage,"
                    "closedate,description"
                )
            },
        )

    def get_associated_contacts(self, deal_id):
        """Retrieve contacts associated with a deal."""

        associations = self._get(
            f"/crm/v4/objects/deals/{deal_id}/associations/contacts"
        )

        contacts = []

        for association in associations.get("results", []):
            contact_id = association["toObjectId"]

            contact = self._get(
                f"/crm/v3/objects/contacts/{contact_id}",
                params={
                    "properties": (
                        "firstname,lastname,email,jobtitle"
                    )
                },
            )

            contacts.append(contact)

        return contacts

    def get_associated_note_ids(self, deal_id):
        """Retrieve IDs of notes associated with a deal."""

        data = self._get(
            f"/crm/v4/objects/deals/{deal_id}/associations/notes"
        )

        return [
            str(item["toObjectId"])
            for item in data.get("results", [])
        ]

    def get_note(self, note_id):
        """Retrieve a HubSpot note using the existing app permissions."""

        return self._get(
            f"/crm/v3/objects/notes/{note_id}",
            params={
                "properties": "hs_note_body,hs_timestamp"
            },
        )

    def get_associated_company(self, deal_id):
        """Retrieve the first company associated with a deal."""

        associations = self._get(
            f"/crm/v4/objects/deals/{deal_id}/associations/companies"
        )

        results = associations.get("results", [])

        if not results:
            return None

        company_id = results[0]["toObjectId"]

        return self._get(
            f"/crm/v3/objects/companies/{company_id}",
            params={
                "properties": "name,domain,industry"
            },
        )