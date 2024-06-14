import sys
import datetime
import tomllib
from pathlib import Path
from collections import defaultdict

exitcode = 0

seen_pid = defaultdict(int)
seen_eid = defaultdict(int)


schema_podcast = {
  "ID": lambda s: isinstance(s, str) and len(s) > 0,
  "Title": lambda s: isinstance(s, str) and len(s) > 0 and len(s) < 100,
  "Subtitle": lambda s: isinstance(s, str) and len(s) < 100,
  "Author": lambda s: isinstance(s, str) and len(s) > 0 and len(s) < 50,
  "Description": lambda s: isinstance(s, str) and len(s) < 3000,
  "Copyright": lambda s: isinstance(s, str) and len(s) < 100,
  "CoverURI": lambda s: isinstance(s, str),
  "Language": lambda s: isinstance(s, str) and s in ("en", "fr"),
}
schema_episode = {
  "ID": lambda s: isinstance(s, str) and len(s) > 0,
  "Title": lambda s: isinstance(s, str) and len(s) > 0 and len(s) < 100,
  "Subtitle": lambda s: isinstance(s, str) and len(s) < 100,
  "Author": lambda s: isinstance(s, str) and len(s) > 0 and len(s) < 100,
  "PubDate": lambda dt: isinstance(dt, datetime.datetime),
  "Description": lambda s: isinstance(s, str) and len(s) < 3000,
  "MediaURI": lambda s: isinstance(s, str) and len(s) > 0,
  "CoverURI": lambda s: isinstance(s, str),
  "Explicit": lambda s: isinstance(s, bool),
}


for tfile in Path('./podcasts/').glob('**/*.toml'):
    print("Check", tfile)
    with open(tfile, "rb") as fd:
        try:
            content = tomllib.load(fd)
        except tomllib.TOMLDecodeError as e:
            exitcode = 1
            print("ERR:NOT-TOML.", tfile)
            continue

    if "podcast" not in content or "episodes" not in content:
        exitcode = 1
        print("ERR:MISSING-FIELD-T.", tfile)
        continue

    podcast_content = content["podcast"]
    for key, validator in schema_podcast.items():
        if key not in podcast_content:
            exitcode = 1
            print("ERR:MISSING-FIELD-P.", tfile, key)
            continue
        if not validator(podcast_content[key]):
            exitcode = 1
            print("ERR:INVALID-FIELD-P.", tfile, key, podcast_content[key])
    seen_pid[podcast_content["ID"]] += 1

    for episode_content in content["episodes"]:
        for key, validator in schema_episode.items():
            if key not in episode_content:
                exitcode = 1
                print("ERR:MISSING-FIELD-E.", tfile, key)
                continue
            if not validator(episode_content[key]):
                exitcode = 1
                print("ERR:INVALID-FIELD-E.", tfile, key, episode_content[key])
        seen_eid[episode_content["ID"]] += 1

    print()


for identifier, count in seen_pid.items():
    if count > 1:
        exitcode = 1
        print("ERR:NOT-UNIQUE-ID-P.", identifier)

for identifier, count in seen_eid.items():
    if count > 1:
        exitcode = 1
        print("ERR:NOT-UNIQUE-ID-E.", identifier)


sys.exit(exitcode)
