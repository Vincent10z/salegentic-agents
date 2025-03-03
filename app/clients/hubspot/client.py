import json
from asyncio.log import logger
from fastapi import HTTPException
from typing import Dict, List, Optional
import aiohttp
from datetime import datetime, timezone, timedelta

from app.api.routes.v1.integrations.hubspot.response import GetHubspotListsResponse
from app.clients.hubspot.client_helpers import parse_date
from app.models.hubspot import HubspotEngagement, HubspotContact, HubspotAnalyticsResult, HubspotPipelineStage, \
    HubspotPipeline, HubspotDeal, HubspotData, HubspotDateField


class HubspotClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.hubapi.com"

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                            params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to HubSpot API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method,
                    f"{self.base_url}/{endpoint}",
                    headers=headers,
                    json=data,
                    params=params
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"HubSpot API error: {error_text}"
                    )
                return await response.json()

    async def get_lists(self, limit: int = 100) -> dict:
        """Get HubSpot lists."""
        try:
            params = {
                "limit": limit,
                "includeFilters": "false"
            }
            response = await self._make_request(
                "GET",
                "crm/v3/lists",
                params=params
            )

            lists_data = []
            for list_item in response.get("lists", []):
                lists_data.append({
                    "listId": list_item["listId"],
                    "name": list_item["name"],
                    "size": list_item["size"]
                })

            return {
                "lists": lists_data,
                "total": len(lists_data)
            }

        except Exception as e:
            logger.error(f"Error in HubSpot API call: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch HubSpot lists: {str(e)}"
            )

    async def get_deals_with_pipelines(self) -> HubspotData:
        """
        Fetch deals and pipeline data from HubSpot API
        Returns a HubspotData object containing deals and pipeline information
        """
        # Fetch all pipelines first
        thirty_days_ago = datetime.now() - timedelta(days=5)
        pipelines = await self._get_pipelines(start_date=thirty_days_ago)

        # Fetch deals
        deals = await self._get_deals(start_date=thirty_days_ago)

        # Return combined data
        return HubspotData(
            deals=deals,
            pipelines=pipelines,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )

    async def _get_deals(
            self,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            date_field: HubspotDateField = HubspotDateField.CREATED_DATE
    ) -> List[HubspotDeal]:
        """
        Fetch deals from HubSpot API with optional date filtering

        Args:
            start_date: Optional start date for filtering deals
            end_date: Optional end date for filtering deals
            date_field: Which date field to filter on (from HubspotDateField enum)

        Returns:
            List of HubspotDeal objects
        """
        deals = []
        endpoint = "crm/v3/objects/deals"
        params = {
            "limit": 100,
            "properties": "dealname,amount,pipeline,dealstage,closedate,createdate,hubspot_owner_id,hs_lastmodifieddate,industry"
        }

        date_field_value = date_field.value
        if start_date or end_date:
            filter_groups = []
            filters = []

            if start_date:
                start_timestamp = int(start_date.timestamp() * 1000)
                filters.append({
                    "propertyName": date_field_value,
                    "operator": "GTE",
                    "value": str(start_timestamp)
                })
            if end_date:
                end_timestamp = int(end_date.timestamp() * 1000)
                filters.append({
                    "propertyName": date_field_value,
                    "operator": "LTE",
                    "value": str(end_timestamp)
                })

            if filters:
                filter_groups.append({"filters": filters})
                params["filterGroups"] = json.dumps(filter_groups)

        has_more = True
        after = None
        while has_more:
            if after:
                params["after"] = after

            data = await self._make_request("GET", endpoint, params=params)

            # Process deals
            for result in data.get("results", []):
                properties = result.get("properties", {})

                # Convert date strings to datetime objects
                create_date = parse_date(properties.get("createdate"))
                close_date = parse_date(properties.get("closedate"))
                last_modified = parse_date(properties.get("hs_lastmodifieddate"))

                # Create deal object
                deal = HubspotDeal(
                    id=result.get("id"),
                    name=properties.get("dealname"),
                    amount=float(properties.get("amount", 0)) if properties.get("amount") else None,
                    pipeline=properties.get("pipeline"),
                    deal_stage=properties.get("dealstage"),
                    close_date=close_date,
                    create_date=create_date,
                    last_modified_date=last_modified,
                    hubspot_owner_id=properties.get("hubspot_owner_id"),
                    industry=properties.get("industry"),
                    contact_ids=[],
                    company_ids=[]
                )

                # Get associated contacts and companies
                deal.contact_ids = await self._get_deal_associations(deal.id, "contacts")
                deal.company_ids = await self._get_deal_associations(deal.id, "companies")

                deals.append(deal)

            # Check if there are more pages
            paging = data.get("paging")
            if paging and "next" in paging and paging["next"] and "after" in paging["next"]:
                after = paging["next"]["after"]
                has_more = True
            else:
                has_more = False

        return deals

    async def _get_pipelines(
            self,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            date_field: HubspotDateField = HubspotDateField.CREATED_DATE
    ) -> List[HubspotPipeline]:
        """
        Fetch all pipelines and their stages with optional date filtering

        Args:
            start_date: Optional start date for filtering pipelines
            end_date: Optional end date for filtering pipelines

        Returns:
            List of HubspotPipeline objects
        """
        pipelines = []
        endpoint = "crm/v3/pipelines/deals"
        params = {}

        date_field_value = date_field.value

        if start_date or end_date:
            filter_groups = []
            filters = []

            if start_date:
                start_timestamp = int(start_date.timestamp() * 1000)  # HubSpot uses milliseconds
                filters.append({
                    "propertyName": date_field_value,
                    "operator": "GTE",
                    "value": str(start_timestamp)
                })
            if end_date:
                end_timestamp = int(end_date.timestamp() * 1000)  # HubSpot uses milliseconds
                filters.append({
                    "propertyName": date_field_value,
                    "operator": "LTE",
                    "value": str(end_timestamp)
                })

            if filters:
                filter_groups.append({"filters": filters})
                params["filterGroups"] = json.dumps(filter_groups)


        has_more = True
        after = None
        while has_more:
            if after:
                params["after"] = after

            data = await self._make_request("GET", endpoint, params=params)

            # Process pipelines
            for result in data.get("results", []):
                stages = []

                # Process stages
                for stage in result.get("stages", []):
                    stages.append(HubspotPipelineStage(
                        id=stage.get("id"),
                        label=stage.get("label"),
                        display_order=stage.get("displayOrder", 0),
                        probability=float(stage.get("metadata", {}).get("probability", 0)),
                        closed_won=stage.get("metadata", {}).get("isClosed") == "true" and
                                   float(stage.get("metadata", {}).get("probability", 0)) == 1.0,
                        closed_lost=stage.get("metadata", {}).get("isClosed") == "true" and
                                    float(stage.get("metadata", {}).get("probability", 0)) == 0.0
                    ))

                # Create pipeline object
                pipeline = HubspotPipeline(
                    id=result.get("id"),
                    label=result.get("label"),
                    display_order=result.get("displayOrder", 0),
                    stages=sorted(stages, key=lambda s: s.display_order)
                )

                pipelines.append(pipeline)

            # Check if there are more pages
            paging = data.get("paging")
            if paging and "next" in paging and paging["next"] and "after" in paging["next"]:
                after = paging["next"]["after"]
                has_more = True
            else:
                has_more = False

        return pipelines

    async def _get_deal_associations(self, deal_id: str, to_object_type: str) -> List[str]:
        """Get IDs of objects associated with a deal"""
        endpoint = f"crm/v3/objects/deals/{deal_id}/associations/{to_object_type}"

        try:
            data = await self._make_request("GET", endpoint)
            return [result.get("id") for result in data.get("results", [])]
        except Exception:
            # Just return empty list on error rather than failing the entire sync
            return []

    async def get_deals_raw(self, limit: int = 100, properties: Optional[List[str]] = None,
                            after: Optional[str] = None, associations: Optional[List[str]] = None) -> Dict:
        """
        Get deals with raw response from HubSpot API

        Args:
            limit: Number of deals to fetch per request
            properties: List of deal properties to include
            after: Pagination token
            associations: List of objects to associate (contacts, companies, etc.)

        Returns:
            Raw API response as dictionary
        """
        endpoint = "crm/v3/objects/deals"
        params = {"limit": limit}

        if properties:
            params["properties"] = ",".join(properties)

        if after:
            params["after"] = after

        if associations:
            params["associations"] = ",".join(associations)

        return await self._make_request("GET", endpoint, params=params)

    async def get_all_deals(self, properties: Optional[List[str]] = None,
                            associations: Optional[List[str]] = None, batch_size: int = 100) -> List[HubspotDeal]:
        """
        Get all deals with optional properties and associations, handling pagination.

        Args:
            properties: List of deal properties to include
            associations: List of objects to associate (contacts, companies, etc.)
            batch_size: Number of deals to fetch per request

        Returns:
            List of HubspotDeal objects
        """
        all_deals = []
        after = None

        while True:
            response = await self.get_deals_raw(
                limit=batch_size,
                properties=properties,
                after=after,
                associations=associations
            )

            deals_data = response.get('results', [])
            if not deals_data:
                break

            # Parse deals into dataclass objects
            for deal_data in deals_data:
                try:
                    properties_data = deal_data.get("properties", {})
                    associations_data = deal_data.get("associations", {})

                    deal = HubspotDeal(
                        id=deal_data.get("id", ""),
                        amount=float(properties_data.get("amount")) if properties_data.get("amount") else None,
                        deal_stage=properties_data.get("dealstage"),
                        close_date=datetime.fromisoformat(properties_data.get("closedate")) if properties_data.get(
                            "closedate") else None,
                        pipeline=properties_data.get("pipeline"),
                        create_date=datetime.fromisoformat(properties_data.get("createdate")) if properties_data.get(
                            "createdate") else None,
                        hubspot_owner_id=properties_data.get("hubspot_owner_id"),
                        industry=properties_data.get("industry"),
                        contact_ids=[contact.get("id") for contact in
                                     associations_data.get("contacts", {}).get("results", [])],
                        company_ids=[company.get("id") for company in
                                     associations_data.get("companies", {}).get("results", [])]
                    )
                    all_deals.append(deal)
                except Exception as e:
                    logger.error(f"Error parsing deal {deal_data.get('id')}: {str(e)}")

            # Check if there are more pages
            next_page = response.get('paging', {}).get('next', {}).get('after')
            if not next_page:
                break

            after = next_page
            logger.info(f"Fetched {len(all_deals)} deals, getting next batch...")

        logger.info(f"Fetched a total of {len(all_deals)} deals")
        return all_deals

    async def get_all_deals(
            self,
            properties: Optional[List[str]] = None,
            associations: Optional[List[str]] = None,
            batch_size: int = 100
    ) -> List[HubspotDeal]:
        """
        Get all deals with optional properties and associations, handling pagination.

        Args:
            properties: List of deal properties to include
            associations: List of objects to associate (contacts, companies, etc.)
            batch_size: Number of deals to fetch per request

        Returns:
            List of HubspotDeal objects
        """
        all_deals = []
        after = None

        while True:
            response = await self.get_deals_raw(
                limit=batch_size,
                properties=properties,
                after=after,
                associations=associations
            )

            deals_data = response.get('results', [])
            if not deals_data:
                break

            # Parse deals into dataclass objects
            for deal_data in deals_data:
                try:
                    properties_data = deal_data.get("properties", {})
                    associations_data = deal_data.get("associations", {})

                    deal = HubspotDeal(
                        id=deal_data.get("id", ""),
                        amount=float(properties_data.get("amount")) if properties_data.get("amount") else None,
                        deal_stage=properties_data.get("dealstage"),
                        close_date=datetime.fromisoformat(properties_data.get("closedate")) if properties_data.get(
                            "closedate") else None,
                        pipeline=properties_data.get("pipeline"),
                        create_date=datetime.fromisoformat(properties_data.get("createdate")) if properties_data.get(
                            "createdate") else None,
                        hubspot_owner_id=properties_data.get("hubspot_owner_id"),
                        industry=properties_data.get("industry"),
                        contact_ids=[contact.get("id") for contact in
                                     associations_data.get("contacts", {}).get("results", [])],
                        company_ids=[company.get("id") for company in
                                     associations_data.get("companies", {}).get("results", [])]
                    )
                    all_deals.append(deal)
                except Exception as e:
                    logger.error(f"Error parsing deal {deal_data.get('id')}: {str(e)}")

            # Check if there are more pages
            next_page = response.get('paging', {}).get('next', {}).get('after')
            if not next_page:
                break

            after = next_page
            logger.info(f"Fetched {len(all_deals)} deals, getting next batch...")

        logger.info(f"Fetched a total of {len(all_deals)} deals")
        return all_deals
