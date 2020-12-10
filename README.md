# NordChecker

> This is no longer maintained. Please fork it and add your own features or patch bugs

**NordChecker** is an advanced version of [NordChecker](https://github.com/Alvixeon/NordVPN-checker) and also influenced by it. It is a seleium driven application used to bypass almost all the security checks nordvpn is using to block bots


## Requirements

- [Chromium WebDriver](http://chromedriver.chromium.org/downloads)
- [Python 3.x](https://python.org)

## Dependencies

- proxybroker
- colorama
- argparse
- selenium
- psutil

## How to Use

1. Clone the repository `git clone https://github.com/tbhaxor/nordchecker.git`
2. Change the directory `cd nordchecker`
3. Get the [requirements](#Requirements) and add the Chrome Driver to your `PATH` variable
4. Install the dependencies `pip install --user -U -r requirements.txt`
5. Run the script `python app.py --file [filename] --separator [username - password separator]`

   For example,

   - FileName: `lists.txt`
   - Username Password Separator: `:`

   ```sh
    $ python app.py --file lists.txt --separator :
   ```

## Help

```
usage: app.py [-h] --file PATH --separator SEPARATOR [--workers]

A damn easy nordvpn account validator

optional arguments:
  -h, --help            show this help message and exit
  --file PATH           The file name containing all username password
  --separator SEPARATOR
                        Username and password separator
  --workers             Set the number of workers. default: 3

```

## Contribution

### Rules

- Pull requests must be made from another branch, not the **master** branch
- Add valid commit message
- Describe the change in pull request

### Scope

- Adding bypass of `NULL` response from https://ucp.nordvpn.com/login/
- Getting valid proxies everytime
- Adding some troubleshooting to the readme
