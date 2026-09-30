# geather tasks

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

    n = max(2,n)
    for i in range(1,n):
        yield i
        await asyncio.sleep(i)
    print("after sleep",n)

async def print_hello():
    print("Hello")


async def main():
    start = time.time()
    async for k in asy_sleep(5):
        print(k)

    print(f"total asy execution time is: {time.time()-start}")
    
    

 

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