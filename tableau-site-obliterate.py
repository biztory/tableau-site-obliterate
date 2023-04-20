# Be careful!

# Assumes the following environment variables are set, or prompts to set them first: TABLEAU_REST_API_PAT_SECRET.

import re, argparse, os
from getpass import getpass
import tableauserverclient as TSC

print(f"tableau-site-obliterate v1.0.0\nhttps://github.com/biztory/tableau-site-obliterate\n\nBiztory cannot be held accountable for data lost through the use of this tool.\n")

parser = argparse.ArgumentParser(prog="tableau-site-obliterate.py", description="Completely erases the contents and metadata on a Tableau Server or Cloud Site. Use with care! Loss of data will occur! The default project, Admin Insights project, and External Assets Default Project project are preserved.")
# Operational arguments
parser.add_argument("--tableau-server-url", "-s", dest="tableau_server_url", required=True, type=str, help="The URL of the Tableau Server (or Cloud pod) we're connecting to.")
parser.add_argument("--tableau-server-site", "-t", dest="tableau_server_site", required=True, type=str, help="The ContentURL of the Tableau Site we're connecting to. Use an empty string (\"\") or \"Default\" for the Default Site. This site will be completely erased!")
parser.add_argument("--tableau-server-api-version", "-v", dest="tableau_server_api_version", required=False, type=str, help="Defaults to 3.15 which is usually recent enough. See: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_versions.htm")
parser.add_argument("--tableau-server-pat-name", "-p", dest="tableau_server_pat_name", required=True, type=str, help="The name of the Personal Access Token we're using to authenticate to Tableau.")
parser.add_argument("--no-confirmation", "-y", dest="no_confirmation", action="store_true", help="Dismiss the confirmation message before taking action, and perform the cleaning immediately. If you specify this option, there is no way to stop all the damage to be done!")

args = parser.parse_args()

# Housekeeping for Tableau Server URL and Site ContentURL
try:
    tableau_server = re.match(r"(https?://.+)/?$", args.tableau_server_url).group(0) # Drop trailing slash here, if present
except Exception as e:
    print("Error trying to parse Tableau Server URL. It should start with \"http://\" or \"https://\".")
tableau_site = "" if args.tableau_server_site == "Default" else args.tableau_server_site
tableau_api_version = "3.15" if args.tableau_server_api_version is None else args.tableau_server_api_version
tableau_pat_name = args.tableau_server_pat_name
tableau_api_base_url = f"{ tableau_server }/api/{ tableau_api_version }"

# Obtaining PAT Secret
if os.environ.get("TABLEAU_REST_API_PAT_SECRET") is None:
    print("The OS environment variable TABLEAU_REST_API_PAT_SECRET has not been set. It's used to retrieve the Personal Access Token secret we use to connect. You can enter it now and have this script save it to a \"temporary\" environment variable, or exit with CTRL+C.")
    tableau_pat_secret = getpass()
else:
    tableau_pat_secret = os.environ["TABLEAU_REST_API_PAT_SECRET"]
print(f"Using Personal Access Token { tableau_pat_name }, with secret starting with: { tableau_pat_secret[0:3] }")

print(f"Signing in to \"{ tableau_server }\", site \"{ tableau_site }\", with PAT \"{ tableau_pat_name }\"")
tableau_server_tsc = TSC.Server(tableau_server, use_server_version=True)
ts_auth = TSC.PersonalAccessTokenAuth(token_name=tableau_pat_name, personal_access_token=tableau_pat_secret, site_id=tableau_site)
tableau_server_tsc.auth.sign_in_with_personal_access_token(ts_auth)

# The fastest way to delete everything is by wiping projects first, which takes care of all the content and their dependencies, and then the users and groups.
all_projects = tableau_server_tsc.projects.all()
all_projects = [p for p in all_projects if p.name.lower() not in ["default", "admin insights", "external assets default project"]] # Some exceptions.
all_projects_total = len(all_projects) # Keeping count just to print later.
all_projects = [p for p in all_projects if p.parent_id is None] # And, we only need top-level projects, the rest disappears automatically.
all_users = tableau_server_tsc.users.all()
all_users = [u for u in all_users if u.id != tableau_server_tsc.user_id]
all_groups = tableau_server_tsc.groups.all()
all_groups = [g for g in all_groups if g.name.lower() != "all users"]

# Summary
print("We're about to delete the following contents from the Tableau Site:")
print(f"\t{ all_projects_total } projects.\n\t\tDeleting projects will delete their contents automatically, i.e. Data Sources, Workbooks, and Flows. In turn, anything that depends on _that_ content will be deleted, e.g. all subscriptions for a workbook, favorites for a data source, etc.")
print(f"\t{ len(all_users) } users.\n\t\tOnly the user running this script will be preserved. Deletion of Collections is not implemented yet, so users owning Collections will also remain.")
print(f"\t{ len(all_groups) } groups.\n\t\tOnly the \"All Users\" group will be preserved.")

# One more chance (?)
if not args.no_confirmation:
    input(f"THIS TABLEAU SITE WILL BE WIPED CLEAN: { tableau_site } on { tableau_server }\n\nPress enter to confirm. Press CTRL+C to abort.")

# Total devastation
for project in all_projects:
    try:
        print(f"Deleting project { project.id }: { project.name }")
        tableau_server_tsc.projects.delete(project_id=project.id)
    except Exception as e:
        print(f"Something went wrong deleting this project:\n{ e }")
for user in all_users:
    try:
        print(f"Deleting user { user.id }: { user.name }")
        tableau_server_tsc.users.remove(user_id=user.id)
    except Exception as e:
        print(f"Something went wrong deleting this user:\n{ e }")
for group in all_groups:
    try:
        print(f"Deleting group { group.id }: { group.name }")
        tableau_server_tsc.groups.delete(group_id=group.id)
    except Exception as e:
        print(f"Something went wrong deleting this group:\n{ e }")

# We're done.
print("Done, everything is GONE (unless the above output said otherwise).")
tableau_server_tsc.auth.sign_out()