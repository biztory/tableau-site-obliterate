# tableau-site-obliterate
Careful! This will erase an entire site on Tableau Server or Tableau Cloud.

## Introduction

You may be familiar with the ominous `tableau-server-obliterate` script, provided with Tableau Server installations and designed to [completely remove Tableau Server from a computer](https://help.tableau.com/current/server/en-us/remove_tableau.htm). This script is the equivalent for Tableau **sites**. It will attempt to clear the site from all of its content, bar the user running the script.

**Biztory cannot be held accountable for data lost through the use of this tool.** As you would expect.

## Installation

Follow these steps:

* Ensure you have Python installed.
* Clone this GitHub repository.
* It's recommended to create a [virtual environment](https://docs.python.org/3/library/venv.html) to install requirements:  
  `python -m venv .venv`
* Activate virtual environment:
  * Windows: `.venv\Scripts\activate.bat` or `.venv\Scripts\activate.ps1`
  * Linux: `source .venv/bin/activate`
* Install requirements:  
  `python -m pip install -r requirements.txt`

The tool authenticates to the Tableau Site with a [Personal Access Token](https://help.tableau.com/current/server/en-us/security_personal_access_tokens.htm) for Tableau's REST API.

## Usage

With the virtual environment activated:


```
python tableau-site-obliterate.py [-h] --tableau-server-url TABLEAU_SERVER_URL --tableau-server-site TABLEAU_SERVER_SITE
                                  [--tableau-server-api-version TABLEAU_SERVER_API_VERSION] --tableau-server-pat-name TABLEAU_SERVER_PAT_NAME

options:
  -h, --help            show this help message and exit
  --tableau-server-url TABLEAU_SERVER_URL, -s TABLEAU_SERVER_URL
                        The URL of the Tableau Server (or Cloud pod) we're connecting to.
  --tableau-server-site TABLEAU_SERVER_SITE, -t TABLEAU_SERVER_SITE
                        The ContentURL of the Tableau Site we're connecting to. Use an empty string ("") or "Default" for the Default Site. This site will
                        be completely erased!
  --tableau-server-api-version TABLEAU_SERVER_API_VERSION, -v TABLEAU_SERVER_API_VERSION
                        Defaults to 3.15 which is usually recent enough. See: https://help.tableau.com/current/api/rest_api/en-
                        us/REST/rest_api_concepts_versions.htm
  --tableau-server-pat-name TABLEAU_SERVER_PAT_NAME, -p TABLEAU_SERVER_PAT_NAME
                        The name of the Personal Access Token we're using to authenticate to Tableau.
```

For example:

`python tableau-site-obliterate.py --tableau-server-url https://10ax.online.tableau.com/ --tableau-server-site timothysdatadevsitedev518337 --tableau-server-pat-name my_pat`

To retrieve the Personal Access Token's secret, the tool will prompt you. Alternatively, it can be set as an OS environment variable with the name `TABLEAU_REST_API_PAT_SECRET`, which the script picks up automatically.

## Notes

Not yet implemented:

* Collections. Users owning Collections will remain on the Site.
* External Assets.
* Site Settings.