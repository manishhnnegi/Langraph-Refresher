# create task

import asyncio
import time

def syn_sleep(n):
    print("before sleep",n)
    time.sleep(2)
    print("after sleep",n)

def print_hello_sy():
    print("Hello")


async def asy_sleep(n):
    print("before sleep",n)
    await asyncio.sleep(2)
    print("after sleep",n)

async def print_hello():
    print("Hello")


async def main():
    start = time.time()

    task = asyncio.create_task(asy_sleep(1))
    await asy_sleep(2)
    await task
    await print_hello()
    

    print(f"total asy execution time is: {time.time()-start}")
    
    start = time.time()
    syn_sleep(1)
    syn_sleep(2)
    print_hello_sy()
    
    print(f"total syn execution time is: {time.time()-start}")
 

if __name__ == "__main__":
    asyncio.run(main())


# result:
# before sleep
# before sleep
# after sleep
# after sleep
# Hello      
# total asy execution time is: 2.002340316772461
# before sleep
# after sleep
# before sleep
# after sleep
# Hello
# total syn execution time is: 4.0018861293792725