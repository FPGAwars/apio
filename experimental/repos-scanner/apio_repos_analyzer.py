"""
Experimental code to analyzer repos crawling results.
"""

import pickle
import json
from pathlib import Path
from typing import List, Dict
from apio_repos_crawler import CrawlResults, crawl, GithubReleaseRef


def main():
    """Main function."""

    cache_file = Path("_crawl_cache.pkl")

    if not cache_file.exists():
        crawl_results: CrawlResults = crawl()
        # pickle.dump(crawl_results, open(cache_file, "wb"))
        with open(cache_file, "wb") as f:
            pickle.dump(crawl_results, f)

    # crawl_results = pickle.load(open(cache_file, "rb"))

    with open(cache_file, "rb") as f:
        crawl_results = pickle.load(f)

    # print("\nxCrawl results:")
    # print(json.dumps(asdict(crawl_results), indent=2, default=str))
    # print()

    # used_releases: Set[GithubReleaseRef] = set()

    used_releases: Dict[str, List[str]] = {}

    def append(r: GithubReleaseRef):
        tags = used_releases.get(r.repo, [])
        if r.tag not in tags:
            tags.append(r.tag)
            tags.sort(reverse=True)
        used_releases[r.repo] = tags

    for _, c in crawl_results.vscode_marketplace_crawl.releases.items():
        append(c.apio_vscode_release)
        append(c.apio_cli_release)
        # used_releases.add(c.apio_vscode_release)
        # used_releases.add(c.apio_cli_release)

    for _, c in crawl_results.remote_configs_crawl.remote_configs.items():
        for _, p in c.packages.items():
            # used_releases.add(p.package_release)
            append(p.package_release)

    # print(len(used_releases))
    # print(len(used_releases.keys()))

    used_releases = dict(sorted(used_releases.items()))

    print(json.dumps(used_releases, indent=2, default=str))

    # for repo in list(used_releases.keys()).sort():
    # for repo, tags in sorted(used_releases.items()):
    #     print(repo)
    #     for tag in tags:
    #       print(f"  {tag}")
    # used_releases = list(used_releases)
    # used_releases.sort()

    # for rel in used_releases:
    #     print(rel)


if __name__ == "__main__":
    main()
