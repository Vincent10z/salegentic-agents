from fastapi import APIRouter, Depends
from typing import List

from . import endpoints

router = APIRouter(
    prefix="/hubspot",
    tags=["HubSpot Integration"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    }
)

# OAuth Routes
# router.add_api_route(
#     path="/connect",
#     endpoint=endpoints.initiate_oauth,
#     methods=["GET"],
#     summary="Initiate HubSpot OAuth Flow",
#     description="Starts the OAuth flow for connecting a HubSpot account",
#     response_model=dict
# )
#
# router.add_api_route(
#     path="/callback",
#     endpoint=endpoints.oauth_callback,
#     methods=["GET"],
#     summary="Handle HubSpot OAuth Callback",
#     description="Handles the OAuth callback from HubSpot and stores credentials",
#     response_model=dict
# )
#
# # Account Management Routes
# router.add_api_route(
#     path="/accounts",
#     endpoint=endpoints.list_connected_accounts,
#     methods=["GET"],
#     summary="List Connected HubSpot Accounts",
#     description="Returns all HubSpot accounts connected to the current user",
#     response_model=List[dict],
#     dependencies=[Depends(get_current_user)]
# )
#
# router.add_api_route(
#     path="/accounts/{account_id}",
#     endpoint=endpoints.get_account_details,
#     methods=["GET"],
#     summary="Get HubSpot Account Details",
#     description="Returns details for a specific connected HubSpot account",
#     response_model=dict,
#     dependencies=[Depends(get_current_user)]
# )
#
# # Contact Routes
# router.add_api_route(
#     path="/contacts",
#     endpoint=endpoints.get_contacts,
#     methods=["GET"],
#     summary="Get HubSpot Contacts",
#     description="Returns contacts from connected HubSpot account",
#     response_model=List[dict],
#     dependencies=[Depends(get_current_user)]
# )
#
# router.add_api_route(
#     path="/contacts/search",
#     endpoint=endpoints.search_contacts,
#     methods=["POST"],
#     summary="Search HubSpot Contacts",
#     description="Search contacts with specific criteria",
#     response_model=List[dict],
#     dependencies=[Depends(get_current_user)]
# )
#
# # Deal Routes
# router.add_api_route(
#     path="/deals",
#     endpoint=endpoints.get_deals,
#     methods=["GET"],
#     summary="Get HubSpot Deals",
#     description="Returns deals from connected HubSpot account",
#     response_model=List[dict],
#     dependencies=[Depends(get_current_user)]
# )
#
# router.add_api_route(
#     path="/deals/{deal_id}",
#     endpoint=endpoints.get_deal_details,
#     methods=["GET"],
#     summary="Get Deal Details",
#     description="Returns detailed information about a specific deal",
#     response_model=dict,
#     dependencies=[Depends(get_current_user)]
# )
#
# # Pipeline Routes
# router.add_api_route(
#     path="/pipelines",
#     endpoint=endpoints.get_pipelines,
#     methods=["GET"],
#     summary="Get Sales Pipelines",
#     description="Returns all sales pipelines from HubSpot",
#     response_model=List[dict],
#     dependencies=[Depends(get_current_user)]
# )
#
# # Analytics Routes
# router.add_api_route(
#     path="/analytics/deals",
#     endpoint=endpoints.get_deal_analytics,
#     methods=["GET"],
#     summary="Get Deal Analytics",
#     description="Returns analytics data for deals",
#     response_model=dict,
#     dependencies=[Depends(get_current_user)]
# )
#
# # Engagement Routes
# router.add_api_route(
#     path="/engagements",
#     endpoint=endpoints.get_engagements,
#     methods=["GET"],
#     summary="Get Engagements",
#     description="Returns engagement data (calls, emails, meetings, etc.)",
#     response_model=List[dict],
#     dependencies=[Depends(get_current_user)]
# )
#
# # Webhook Routes
# router.add_api_route(
#     path="/webhooks/configure",
#     endpoint=endpoints.configure_webhooks,
#     methods=["POST"],
#     summary="Configure HubSpot Webhooks",
#     description="Sets up webhooks for HubSpot events",
#     response_model=dict,
#     dependencies=[Depends(get_current_user)]
# )
#
# router.add_api_route(
#     path="/webhooks/callback",
#     endpoint=endpoints.webhook_callback,
#     methods=["POST"],
#     summary="Webhook Callback Handler",
#     description="Handles incoming webhooks from HubSpot",
#     response_model=dict
# )
#
# # Settings Routes
# router.add_api_route(
#     path="/settings",
#     endpoint=endpoints.update_settings,
#     methods=["PUT"],
#     summary="Update HubSpot Integration Settings",
#     description="Updates settings for the HubSpot integration",
#     response_model=dict,
#     dependencies=[Depends(get_current_user)]
# )