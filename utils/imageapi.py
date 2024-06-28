import requests
import base64
import os
import aiohttp
import asyncio

key = "6d207e02198a847aa98d0a2a901485a5"
async def image_url(url):
    urlx = f"https://wg7.pinpon.cool/media/resize?inputFilename={url}&outputFilename=upload{url}&stretch=true&scale=0.6"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://wg7.pinpon.cool/media/resize?inputFilename={url}&outputFilename=upload{url}&stretch=true&scale=0.6") as response:
            data = {
                'key':key,
                'source':response.url,
                }
            r = requests.post("https://freeimage.host/api/1/upload",data=data).json()
            if r['status_code']==200:
                image = r['image']['file']['resource']['chain']['image']
                image = str(image)
                return image


#asyncio.run(image_url("upload/8948e7c17f78c49405eddfdeb8d1fe52.png"))