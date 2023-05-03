from fastapi import APIRouter, Request, HTTPException


from ..main import config

router = APIRouter(tags=["integrations"])


@router.post("/integrations/slack/events")
async def handle_slack_event(request: Request):
    if config.slack_client is None:
        raise HTTPException(status_code=404, detail="Slack Integration not enabled")
    return await config.slack_client.handler.handle(request)
