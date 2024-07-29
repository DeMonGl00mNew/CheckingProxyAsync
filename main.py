import httpx
import asyncio
import aiofile
from fake_useragent import UserAgent
from collections import namedtuple

'''
This script is useful for checking the validity of a large number of HTTP proxies asynchronously.
'''

# List proxy for checking.
proxies = list()
# Class generating fake user-agent header.
user_agent = UserAgent()
# Endpoint for checking list of proxies.
URL = "https://httpbin.org/ip"
# tuple store the proxy status result and its validation status.
Result_proxy = namedtuple('Result_proxy', 'proxy validation type')

# function generates a random user-agent header using the UserAgent libary.
def random_hearder():
    return {'user-agent': user_agent.random}

# function takes and sends a request to a test URL using the proxy asynchronously.
async def check_proxy(cur_proxy: str,proxy_type:str):
    async with httpx.AsyncClient(
            proxies={"http://": f"{proxy_type}://{cur_proxy}", "https://": f"{proxy_type}://{cur_proxy}"}) as client:
        try:
            response = await client.get(URL, headers=random_hearder(), timeout=10)

            if response.status_code == 200:
                return cur_proxy, True ,proxy_type
        except:
            pass
        return cur_proxy, False, proxy_type

# function take a list of proxies, check each proxy asynchronously and writel valid proxies to a file.
async def check_proxies(proxy_type,proxies):
    tasks = [check_proxy(proxy,proxy_type) for proxy in proxies]
    for result in asyncio.as_completed(tasks):
        check_res = await result
        checked_proxy = Result_proxy(*check_res)

        if checked_proxy.validation == True:
            print(checked_proxy.proxy, checked_proxy.validation, checked_proxy.type)
            await write_file("valid_proxy_list.txt", f"{checked_proxy.proxy}")
        else:
            print(checked_proxy.proxy, checked_proxy.validation, checked_proxy.type)

# funcion asynchrounsly write text to a file.
async def write_file(file_name: str, text):
    async  with aiofile.async_open(file_name, 'a') as file:
        await  file.write(text + "\n")

# function reads a list of proxies from a file and returns it as a list.
def get_http_proxy_list(file_name):
    with open(file_name, 'r') as file:
        list_proxy = [f"{line.strip()}" for line in file.readlines()]
        return list_proxy

# function iterates over the list of proxies in batches of j and calls check_proxies func.
async def repeat_checker(len_list,proxy_type):
    for i in range(0, len_list, j := 20):
        try:
            await check_proxies(proxy_type,proxies=proxies[i:i + j])
        except:
            continue

# In the main block, it read the list of proxie from file and then runs the repeat_cheker function using asyncio.
if __name__ == "__main__":
    try:
        proxies = get_http_proxy_list("proxy_http.txt")
    except FileNotFoundError:
        print("proxy_http.txt ")
    if len(proxies) == 0:
        raise ValueError("no proxy_http.txt")
    asyncio.run(repeat_checker(len(proxies),"http"))
    
    
    try:
        proxies = get_http_proxy_list("proxy_socks5.txt")
    except FileNotFoundError:
        print("proxy_socks5.txt ")
    if len(proxies) == 0:
        raise ValueError("no proxy_socks5.txt")
    asyncio.run(repeat_checker(len(proxies),"socks5"))
