import os

alt_epg_top_dir = os.path.dirname(__file__)
for entry in os.scandir(alt_epg_top_dir):
    if entry.is_dir() and not entry.is_file() and entry.name[0] != '_':
        print(entry)
        alt_epg_name = entry.name
        alt_epg_dir_contents = [x for x in os.scandir("%s/%s" % (alt_epg_top_dir, alt_epg_name))]
        if "%s_conf.json" % alt_epg_name in alt_epg_dir_contents and "__init__.py" in alt_epg_dir_contents:
            exec("from .%s import *" % alt_epg_name)
