import httpx
from typing import Dict, Any, List

class IntegrationClientService:
    @staticmethod
    async def send_slack_message(webhook_url: str, text: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json={"text": text})
            return response.status_code == 200

    @staticmethod
    async def send_telegram_message(bot_token: str, chat_id: str, text: str) -> bool:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"chat_id": chat_id, "text": text})
            return response.status_code == 200

    @staticmethod
    async def append_google_sheets(access_token: str, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}:append"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        params = {"valueInputOption": "USER_ENTERED"}
        payload = {"values": values}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f"Google Sheets Error: {response.text}")
            return response.json()
