# create task

import asyncio
import time

def syn_sleep():
    print("before sleep")
    time.sleep(2)
    print("after sleep")

def print_hello_sy():
    print("Hello")


async def asy_sleep():
    print("before sleep")
    await asyncio.sleep(2)
    print("after sleep")

async def print_hello():
    print("Hello")


async def main():
    start = time.time()

    await asy_sleep()
    await asy_sleep()
    await print_hello()
    

    print(f"total asy execution time is: {time.time()-start}")
    
    start = time.time()
    syn_sleep()
    syn_sleep()
    print_hello_sy()
    
    print(f"total syn execution time is: {time.time()-start}")
 

if __name__ == "__main__":
    asyncio.run(main())



# result:
# before sleep
# after sleep
# before sleep
# after sleep
# Hello
# total asy execution time is: 4.0204572677612305
# before sleep
# after sleep
# before sleep
# after sleep
# Hello
# total syn execution time is: 4.0046916007995605

# conclusion till now both the method syn and asynci are behaving the same way.
# need to create some task in async method to see the difference