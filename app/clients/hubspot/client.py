from asyncio.log import logger
from fastapi import HTTPException
from typing import Dict, List, Optional
import aiohttp
from datetime import datetime, timezone, timedelta

from app.api.routes.v1.integrations.hubspot.response import GetHubspotListsResponse
from app.models.hubspot import HubspotEngagement, HubspotContact, HubspotAnalyticsResult, HubspotPipelineStage, \
    HubspotPipeline, HubspotDeal


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

    async def get_deals_raw(
            self,
            limit: int = 100,
            properties: Optional[List[str]] = None,
            after: Optional[str] = None,
            associations: Optional[List[str]] = None
    ) -> Dict:
        """
        Get raw deal data with optional properties and associations for a single page.

        This is a private method used internally by get_all_deals.
        """
        params = {"limit": limit}
        if properties:
            params["properties"] = properties
        if after:
            params["after"] = after
        if associations:
            params["associations"] = associations

        return await self._make_request(
            "GET",
            "crm/v3/objects/deals",
            params=params
        )

    async def get_all_pipelines(self) -> List[HubspotPipeline]:
        """
        Get all deal pipelines and their stages.

        Returns:
            List of HubspotPipeline objects
        """
        response = await self.get_pipelines_raw()
        pipelines_data = response.get('results', [])

        pipelines = []
        for pipeline_data in pipelines_data:
            try:
                stages = []
                for stage_data in pipeline_data.get("stages", []):
                    # Extract metadata
                    metadata = stage_data.get("metadata", {})
                    # Convert string "true"/"false" to boolean
                    is_closed = metadata.get("isClosed", "false").lower() == "true"
                    # Convert probability string to float
                    probability = float(metadata.get("probability", "0.0"))

                    stages.append(HubspotPipelineStage(
                        id=stage_data.get("id", ""),
                        label=stage_data.get("label", ""),
                        display_order=stage_data.get("displayOrder", 0),
                        probability=probability,
                        closed_won=is_closed and probability == 1.0,
                        closed_lost=is_closed and probability == 0.0
                    ))

                pipelines.append(HubspotPipeline(
                    id=pipeline_data.get("id", ""),
                    label=pipeline_data.get("label", ""),
                    display_order=pipeline_data.get("displayOrder", 0),
                    stages=stages
                ))
            except Exception as e:
                logger.error(f"Error parsing pipeline {pipeline_data.get('id')}: {str(e)}")

        return pipelines

    async def get_pipelines_raw(self) -> Dict:
        """
        Get raw pipeline data.

        This is a private method used internally by get_all_pipelines.
        """
        return await self._make_request("GET", "crm/v3/pipelines/deals")

    # async def get_deal_analytics(
    #         self,
    #         start_date: datetime,
    #         end_date: datetime,
    #         interval: str = "MONTHLY"
    # ) -> HubspotAnalyticsResult:
    #     """
    #     Get analytics data for deals.
    #
    #     Args:
    #         start_date: Start date for analytics
    #         end_date: End date for analytics
    #         interval: Time interval (DAILY, WEEKLY, MONTHLY)
    #
    #     Returns:
    #         HubspotAnalyticsResult object
    #     """
    # # Validate input dates
    #     if start_date is None or end_date is None:
    #         print(f"WARNING: Invalid dates - start_date: {start_date}, end_date: {end_date}")
    #         # Use default dates if either is None
    #         default_start = datetime.now() - timedelta(days=30)
    #         default_end = datetime.now()
    #         start_date = default_start if start_date is None else start_date
    #         end_date = default_end if end_date is None else end_date
    #         print(f"INFO: Using default dates - start_date: {start_date}, end_date: {end_date}")
    #
    #     try:
    #         # Format params for API request
    #         params = {
    #             "startDate": start_date.isoformat(),
    #             "endDate": end_date.isoformat(),
    #             "interval": interval
    #         }
    #         print(f"DEBUG: Request params: {params}")
    #
    #         # Make API request
    #         print(f"DEBUG: Making request to analytics/v3/reports/deals")
    #         response = await self._make_request(
    #             "GET",
    #             "analytics/v3/reports/deals",
    #             params=params
    #         )
    #         print(f"DEBUG: Response received: {response}")
    #
    #         # Extract results from response
    #         results = response.get("results", [])
    #         print(f"DEBUG: Results count: {len(results)}")
    #
    #         # Initialize values
    #         deals_created = 0
    #         deals_closed_won = 0
    #         deals_closed_lost = 0
    #         revenue_generated = 0
    #
    #         # Parse the results
    #         for result in results:
    #             data_type = result.get("dataType")
    #             value = result.get("value", 0)
    #             print(f"DEBUG: Processing result - dataType: {data_type}, value: {value}")
    #
    #             if data_type == "DEALS_CREATED":
    #                 deals_created = value
    #             elif data_type == "DEALS_CLOSED_WON":
    #                 deals_closed_won = value
    #             elif data_type == "DEALS_CLOSED_LOST":
    #                 deals_closed_lost = value
    #             elif data_type == "REVENUE_GENERATED":
    #                 revenue_generated = value
    #
    #         # Create and return result
    #         analytics_result = HubspotAnalyticsResult(
    #             start_date=start_date,
    #             end_date=end_date,
    #             deals_created=deals_created,
    #             deals_closed_won=deals_closed_won,
    #             deals_closed_lost=deals_closed_lost,
    #             revenue_generated=revenue_generated
    #         )
    #         print(f"DEBUG: Returning analytics result: {analytics_result}")
    #         return analytics_result
    #
    #     except Exception as e:
    #         print(f"ERROR: Exception during get_deal_analytics: {type(e).__name__}: {str(e)}")
    #         # You can either re-raise the exception or return a default result
    #         # Re-raise: raise
    #         # Or return default:
    #         return HubspotAnalyticsResult(
    #             start_date=start_date,
    #             end_date=end_date
    #         )

    async def get_all_contacts(
            self,
            properties: Optional[List[str]] = None,
            batch_size: int = 100
    ) -> List[HubspotContact]:
        """
        Get all contacts with optional properties, handling pagination.

        Args:
            properties: List of contact properties to include
            batch_size: Number of contacts to fetch per request

        Returns:
            List of HubspotContact objects
        """
        all_contacts = []
        after = None

        while True:
            response = await self.get_contacts_raw(
                limit=batch_size,
                properties=properties,
                after=after
            )

            contacts_data = response.get('results', [])
            if not contacts_data:
                break

            # Parse contacts into dataclass objects
            for contact_data in contacts_data:
                try:
                    properties_data = contact_data.get("properties", {})

                    contact = HubspotContact(
                        id=contact_data.get("id", ""),
                        create_date=datetime.fromisoformat(properties_data.get("createdate")) if properties_data.get(
                            "createdate") else None,
                        last_modified_date=datetime.fromisoformat(
                            properties_data.get("lastmodifieddate")) if properties_data.get(
                            "lastmodifieddate") else None,
                        lifecycle_stage=properties_data.get("lifecyclestage"),
                        email=properties_data.get("email"),
                        company_size=properties_data.get("company_size"),
                        industry=properties_data.get("industry")
                    )
                    all_contacts.append(contact)
                except Exception as e:
                    logger.error(f"Error parsing contact {contact_data.get('id')}: {str(e)}")

            # Check if there are more pages
            next_page = response.get('paging', {}).get('next', {}).get('after')
            if not next_page:
                break

            after = next_page
            logger.info(f"Fetched {len(all_contacts)} contacts, getting next batch...")

        logger.info(f"Fetched a total of {len(all_contacts)} contacts")
        return all_contacts

    async def get_contacts_raw(
            self,
            limit: int = 100,
            properties: Optional[List[str]] = None,
            after: Optional[str] = None
    ) -> Dict:
        """
        Get raw contact data with optional properties for a single page.

        This is a private method used internally by get_all_contacts.
        """
        params = {"limit": limit}
        if properties:
            params["properties"] = properties
        if after:
            params["after"] = after

        return await self._make_request(
            "GET",
            "crm/v3/objects/contacts",
            params=params
        )

    async def get_all_engagements(
            self,
            engagement_types: Optional[List[str]] = None,
            batch_size: int = 100
    ) -> List[HubspotEngagement]:
        """
        Get all engagements (calls, emails, meetings, etc.), handling pagination.

        Args:
            engagement_types: List of types to include (CONVERSATION_SESSION, etc.)
            batch_size: Number of engagements to fetch per request

        Returns:
            List of HubspotEngagement objects
        """
        all_engagements = []
        after = None

        while True:
            response = await self.get_engagements_raw(
                limit=batch_size,
                after=after,
                engagement_types=engagement_types
            )

            engagements_data = response.get('results', [])
            if not engagements_data:
                break

            # Parse engagements into dataclass objects
            for engagement_data in engagements_data:
                try:
                    # Extract data from the new format
                    engagement_id = engagement_data.get("id", "")
                    properties = engagement_data.get("properties", {})
                    engagement_type = properties.get("hs_engagement_type", "")

                    # Parse timestamp from createDate
                    create_date_str = properties.get("hs_createdate")
                    timestamp = None
                    if create_date_str:
                        try:
                            # Parse ISO format timestamp
                            create_date = datetime.fromisoformat(create_date_str.replace('Z', '+00:00'))
                            timestamp = create_date
                        except ValueError:
                            # Try alternative parsing method if standard ISO parsing fails
                            try:
                                create_date = datetime.strptime(create_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                                timestamp = create_date.replace(tzinfo=timezone.utc)
                            except ValueError:
                                logger.error(f"Failed to parse timestamp: {create_date_str}")

                    # Check createdAt and updatedAt fields if they exist
                    created_at = engagement_data.get("createdAt")
                    if timestamp is None and created_at:
                        try:
                            timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except ValueError:
                            pass


                    engagement_obj = HubspotEngagement(
                        id=engagement_id,
                        type=engagement_type,
                        timestamp=timestamp,
                    )
                    all_engagements.append(engagement_obj)
                except Exception as e:
                    logger.error(f"Error parsing engagement {engagement_data.get('id')}: {str(e)}")

            # Check if there are more pages
            paging = response.get('paging', {})
            next_page = paging.get('next', {}).get('after') if paging else None
            if not next_page:
                break

            after = next_page
            logger.info(f"Fetched {len(all_engagements)} engagements, getting next batch...")

        logger.info(f"Fetched a total of {len(all_engagements)} engagements")
        return all_engagements

    async def get_engagements_raw(
            self,
            limit: int = 100,
            after: Optional[str] = None,
            engagement_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Get raw engagement data for a single page.

        This is a private method used internally by get_all_engagements.
        """
        params = {"limit": limit}
        if after:
            params["after"] = after
        if engagement_types:
            params["types"] = engagement_types

        return await self._make_request(
            "GET",
            "crm/v3/objects/engagements",
            params=params
        )

    async def get_deal(self, deal_id: str, properties: Optional[List[str]] = None) -> Dict:
        """Get detailed information about a specific deal."""
        params = {}
        if properties:
            params["properties"] = properties

        return await self._make_request(
            "GET",
            f"crm/v3/objects/deals/{deal_id}",
            params=params
        )

    # Pipeline Methods
    async def get_pipelines(self) -> Dict:
        """Get all deal pipelines and their stages."""
        return await self._make_request("GET", "crm/v3/pipelines/deals")

    async def get_pipeline_stages(self, pipeline_id: str) -> Dict:
        """Get stages for a specific pipeline."""
        return await self._make_request(
            "GET",
            f"crm/v3/pipelines/deals/{pipeline_id}/stages"
        )

    # Contact Methods
    async def get_contacts(
            self,
            limit: int = 100,
            properties: Optional[List[str]] = None,
            after: Optional[str] = None
    ) -> Dict:
        """Get contacts with optional properties."""
        params = {"limit": limit}
        if properties:
            params["properties"] = properties
        if after:
            params["after"] = after

        return await self._make_request(
            "GET",
            "crm/v3/objects/contacts",
            params=params
        )

    async def get_contact(
            self,
            contact_id: str,
            properties: Optional[List[str]] = None
    ) -> Dict:
        """Get detailed information about a specific contact."""
        params = {}
        if properties:
            params["properties"] = properties

        return await self._make_request(
            "GET",
            f"crm/v3/objects/contacts/{contact_id}",
            params=params
        )

    # Company Methods
    async def get_companies(
            self,
            limit: int = 100,
            properties: Optional[List[str]] = None,
            after: Optional[str] = None
    ) -> Dict:
        """Get companies with optional properties."""
        params = {"limit": limit}
        if properties:
            params["properties"] = properties
        if after:
            params["after"] = after

        return await self._make_request(
            "GET",
            "crm/v3/objects/companies",
            params=params
        )

    # Engagement Methods
    async def get_engagements(
            self,
            limit: int = 100,
            after: Optional[str] = None,
            engagement_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Get engagement data (calls, emails, meetings, etc.).

        Args:
            limit: Number of engagements to return
            after: Continuation token for pagination
            engagement_types: List of types to include (CALL, EMAIL, MEETING, etc.)
        """
        params = {"limit": limit}
        if after:
            params["after"] = after
        if engagement_types:
            params["types"] = engagement_types

        return await self._make_request(
            "GET",
            "crm/v3/objects/engagements",
            params=params
        )

    async def get_engagement_activity(self, engagement_id: str) -> Dict:
        """Get detailed information about a specific engagement."""
        return await self._make_request(
            "GET",
            f"crm/v3/objects/engagements/{engagement_id}"
        )

    # Property Methods
    async def get_properties(self, object_type: str) -> Dict:
        """
        Get all properties for a specific object type.

        Args:
            object_type: The object type (contacts, companies, deals, etc.)
        """
        return await self._make_request(
            "GET",
            f"crm/v3/properties/{object_type}"
        )

    # Association Methods
    async def get_associations(
            self,
            object_type: str,
            object_id: str,
            to_object_type: str
    ) -> Dict:
        """
        Get associations between objects.

        Args:
            object_type: Source object type (deals, contacts, etc.)
            object_id: Source object ID
            to_object_type: Target object type to find associations with
        """
        return await self._make_request(
            "GET",
            f"crm/v3/objects/{object_type}/{object_id}/associations/{to_object_type}"
        )

    # Batch Methods
    async def batch_get_deals(self, deal_ids: List[str]) -> Dict:
        """Get multiple deals in a single request."""
        data = {"inputs": [{"id": id} for id in deal_ids]}
        return await self._make_request(
            "POST",
            "crm/v3/objects/deals/batch/read",
            data=data
        )

    async def batch_get_contacts(self, contact_ids: List[str]) -> Dict:
        """Get multiple contacts in a single request."""
        data = {"inputs": [{"id": id} for id in contact_ids]}
        return await self._make_request(
            "POST",
            "crm/v3/objects/contacts/batch/read",
            data=data
        )
