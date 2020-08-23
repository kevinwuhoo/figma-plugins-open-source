import json
import re
import requests
from operator import itemgetter
from tabulate import tabulate

FIGMA_PLUGINS_URL = "https://www.figma.com/api/plugins/top?page_size=1000&org_id=null"

GITHUB_URL_REGEX = r"(?:https://github.com/[\w-]+/[\w-]+)"
BITBUCKET_URL_REGEX = r"(?:https://bitbucket.org/[\w-]+/[\w-]+)"
GITLAB_URL_REGEX = r"(?:https://gitlab.com/[\w-]+/[\w-]+)"
URL_REGEXES = "|".join([GITHUB_URL_REGEX, BITBUCKET_URL_REGEX, GITLAB_URL_REGEX])
OPEN_SOURCE_REGEX = re.compile(f"({URL_REGEXES})")

r = requests.get(FIGMA_PLUGINS_URL)

open("./plugins.json", "w").write(r.text)
# r = json.load(open("./plugins.json"))

plugins = []
for plugin in r.json()["meta"]:
    m = OPEN_SOURCE_REGEX.search(str(plugin))
    if not m:
        continue

    author = plugin["publisher"]["name"]
    install_count = int(plugin["install_count"])
    like_count = int(plugin["like_count"])
    open_source_url = m.group()
    figma_plugin_url = f"https://www.figma.com/community/plugin/{plugin['id']}"

    for version_id, version in plugin["versions"].items():
        description = version["description"]
        name = version["name"]
        break  # use the first version for now, seems to be only one anyway

    plugin_data = {
        "author": author,
        "description": description,
        "install_count": install_count,
        "like_count": like_count,
        "name": name,
        "open_source_url": open_source_url,
        "figma_plugin_url": figma_plugin_url,
    }
    plugins.append(plugin_data)

plugins = sorted(plugins, key=itemgetter("install_count"), reverse=True)

table = []
for plugin in plugins:
    name = f"[{plugin['name']}]({plugin['open_source_url']})"
    author_url = plugin["open_source_url"][: plugin["open_source_url"].rindex("/")]
    author = f"[{plugin['author']}]({author_url})"
    installs = f"`{format(plugin['install_count'], ',d')}`"
    likes = f"`{format(plugin['like_count'], ',d')}`"
    # TODO not all hosts are Github
    figma = f"[![Code](images/figma.svg)]({plugin['figma_plugin_url']})"
    row = [
        name,
        author,
        installs,
        likes,
        figma,
    ]
    table.append(row)

headers = ["Name and Link to Code", "Author", "Installs", "Likes", "Plugin"]
colalign = ("left", "left", "right", "right", "center")
markdown_table = tabulate(table, headers, tablefmt="pipe", colalign=colalign)

readme = f"""
# Open Source Figma Plugins

The [documentation](https://www.figma.com/plugin-docs/intro/) for creating Figma
plugins is pretty good but lacks realistic examples. A number of popular plugins
are open source. I find that they provide great inspiration as well as deep
insight into the API.

This project contains a comprehensive list of plugins which have links to their
respective repositories. Published Figma plugins are scanned daily and any new
plugins are added to this list.

## List of Plugins

{markdown_table}
"""

open("README.md", "w").write(readme)
