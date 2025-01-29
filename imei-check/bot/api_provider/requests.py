import aiohttp
import os


BASE_URL = 'https://api.imeicheck.net/v1/services/'


async def get_imei_info(imei_number: int):
    headers = {
        'Authorization': os.getenv('API_SANDBOX')
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASE_URL}', headers=headers) as response:
            return await response.json()
