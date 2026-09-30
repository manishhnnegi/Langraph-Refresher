# asyncio runs at single core and single thread


import asyncio

#corutine
async def asy_sleep():
    print("before sleep")
    await asyncio.sleep(2)
    print("after sleep")
   


# asy_sleep()  # will give  RuntimeWarning: coroutine 'asy_sleep' was never awaited
# await asy_sleep()   will also thow error

async def print_hello():
    print("hello")

async def asy_retrun_hello():
    return "asy Hello as retrun"

def return_hello():
    return "Hello as retrun"


# event loop
async def main():
    await asy_sleep()
    await print_hello()
    ans = await asy_retrun_hello()
    ans2 = return_hello()

    print(f"in main ---{ans} & {ans2}")



if __name__ == "__main__":
    # start event loop
    asyncio.run(main())
