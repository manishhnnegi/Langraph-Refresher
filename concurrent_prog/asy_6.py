

import asyncio
import time
import requests
import aiohttp  # async libraries has to use for it



async def get_url_requests(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
        




#syncronus version

async def main():

    urls = [
            "https://www.google.com/",
            'https://en.wikipedia.org/wiki/Wikipedia:About',
            "https://www.python.org/doc/",
            "https://www.apple.com/",
            "https://www.medium.com/",
            'https://www.w3schools.com/python/',
            'https://en.wikipedia.org/wiki/Wikipedia:About',

           ]
    
#syncronus version
    st = time.time()
    syn_response_list = []
    for url in urls:
        syn_response_list.append(requests.get(url).text)

    print("final syn time", time.time()-st)


#asyncronus version
    st = time.time()
    tasks = []
    for url in urls:
        tasks.append(asyncio.create_task(get_url_requests(url)))

    asy_task_response = await asyncio.gather(*tasks)

    print("final asy  time", time.time()-st)





if __name__ == "__main__":
    asyncio.run(main())