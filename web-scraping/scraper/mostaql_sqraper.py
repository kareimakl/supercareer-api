# scraper/mostaql_scraper.py
import os
import csv
import time
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
REQUEST_TIMEOUT = 15  # seconds
SLEEP_BETWEEN_REQUESTS = 1.0  # seconds, polite delay


def fetch_html(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
    """Return the HTML text for given URL or None on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        print(f"[fetch_html] error fetching {url}: {e}")
        return None


def extract_project_links(page_url: str, limit: int = 25) -> List[str]:
    """
    Extract project links from a Mostaql listing page.
    Returns a list of absolute URLs (max `limit`).
    """
    html = fetch_html(page_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    links: List[str] = []

    # Primary selector: table rows with class "project-row" and anchor inside h2
    for row in soup.select("tr.project-row"):
        a = row.select_one("h2 a")
        if not a:
            # fallback: any anchor with '/project/' in href inside the row
            a = row.find("a", href=lambda href: href and "/project/" in href)
        if a and a.get("href"):
            href = a["href"].strip()
            # normalize to absolute
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = "https://mostaql.com" + href
            elif not href.startswith("http"):
                href = "https://mostaql.com/" + href
            links.append(href)
            if len(links) >= limit:
                break

    # If nothing found, try another common anchor pattern
    if not links:
        for a in soup.select("a[href*='/project/']"):
            href = a["href"].strip()
            if href.startswith("/"):
                href = "https://mostaql.com" + href
            elif href.startswith("//"):
                href = "https:" + href
            elif not href.startswith("http"):
                href = "https://mostaql.com/" + href
            if href not in links:
                links.append(href)
            if len(links) >= limit:
                break

    return links[:limit]


def extract_project_details(project_url: str) -> Optional[Dict[str, str]]:
    """
    Visit a project page and extract:
      - project_name
      - project_details (text)
      - project_status
      - publish_date (ISO datetime if available)
      - budget
      - duration
      - skills (comma separated)
      - link
    Returns a dict or None if page couldn't be fetched.
    """
    html = fetch_html(project_url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # 1) project_name
    # try several fallbacks: span[data-type="page-header-title"], h1.heada__title, h1
    title = ""
    title_tag = soup.select_one('span[data-type="page-header-title"]')
    if not title_tag:
        title_tag = soup.select_one('h1.heada__title')
    if not title_tag:
        title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.get_text(" ", strip=True)

    # 2) project_details
    details = ""
    # prefer the details container by id
    details_container = soup.select_one("#projectDetailsTab .carda__content") or soup.select_one("#projectDetailsTab") or soup.select_one("div#projectDetailsTab")
    if details_container:
        details = details_container.get_text(" ", strip=True)
    else:
        # fallback: any big paragraph area under 'تفاصيل المشروع' panel
        possible = soup.select_one("div.panel#project-brief, div#project-brief, div.carda__content")
        if possible:
            details = possible.get_text(" ", strip=True)

    # 3-6) project meta values: status, publish_date, budget, duration
    # The page uses repeated blocks: div.meta-row -> div.meta-label and div.meta-value
    status = ""
    publish_date = ""
    budget = ""
    duration = ""
    skills = ""

    meta_rows = soup.select("div.meta-rows > div.meta-row")
    if not meta_rows:
        # fallback: look for any div.meta-row
        meta_rows = soup.select("div.meta-row")

    # Based on current site structure (from example):
    # meta_rows[0] -> status
    # meta_rows[1] -> publish date (contains <time datetime=...>)
    # meta_rows[2] -> budget
    # meta_rows[3] -> duration
    # meta_rows[4] -> skills container (skills list appears after)
    try:
        if len(meta_rows) >= 1:
            val = meta_rows[0].select_one(".meta-value")
            if val:
                status = val.get_text(" ", strip=True)
        if len(meta_rows) >= 2:
            # try to extract datetime attribute if available
            time_tag = meta_rows[1].select_one("time")
            if time_tag and time_tag.has_attr("datetime"):
                publish_date = time_tag["datetime"].strip()
            else:
                val = meta_rows[1].select_one(".meta-value")
                if val:
                    publish_date = val.get_text(" ", strip=True)
        if len(meta_rows) >= 3:
            val = meta_rows[2].select_one(".meta-value")
            if val:
                budget = val.get_text(" ", strip=True)
        if len(meta_rows) >= 4:
            val = meta_rows[3].select_one(".meta-value")
            if val:
                duration = val.get_text(" ", strip=True)
    except Exception:
        # safe fallback to avoid crashing on unexpected structure
        pass

    # 7) skills: look for ul.skills li a bdi or li a.tag
    skills_elems = soup.select("ul.skills li a bdi, ul.skills li a, ul.skills.list-tags li a bdi, ul.skills.list-tags li a")
    skills_list = []
    for s in skills_elems:
        text = s.get_text(" ", strip=True)
        if text:
            skills_list.append(text)
    if skills_list:
        # remove duplicates while preserving order
        seen = set()
        skills_ordered = []
        for t in skills_list:
            if t not in seen:
                seen.add(t)
                skills_ordered.append(t)
        skills = ", ".join(skills_ordered)

    # Final fallback extraction for any missing fields using direct selectors
    if not budget:
        budget_tag = soup.select_one('[data-type="project-budget_range"], div.meta-value[data-type="project-budget_range"]')
        if budget_tag:
            budget = budget_tag.get_text(" ", strip=True)
    if not duration:
        # look for meta-row label containing "مدة التنفيذ" will be Arabic; cannot use text match per requirement,
        # so try to detect numeric + "يوم" or "أيام" nearby as fallback
        dur_candidate = soup.find(string=lambda t: t and ("يوم" in t or "أيام" in t))
        if dur_candidate:
            duration = dur_candidate.strip()

    result = {
        "project_name": title,
        "project_details": details,
        "project_status": status,
        "publish_date": publish_date,
        "budget": budget,
        "duration": duration,
        "skills": skills,
        "link": project_url
    }

    return result


def save_projects_csv(projects: List[Dict[str, str]], filename: str = None) -> str:
    """
    Save projects list to CSV under sibling 'data' directory.
    Returns the path of the saved file.
    """
    # script is expected to be in project_root/scraper/mostaql_scraper.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    if filename is None:
        filename = "mostaql_projects.csv"
    file_path = os.path.join(data_dir, filename)

    fieldnames = ["project_name", "project_details", "project_status", "publish_date", "budget", "duration", "skills", "link"]
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in projects:
            # ensure all keys exist
            row = {k: item.get(k, "") for k in fieldnames}
            writer.writerow(row)

    return file_path


def main(list_page_url: str = "https://mostaql.com/projects", pages: int = 1, per_page_limit: int = 25):
    """
    Orchestrator:
      - collect links from listing pages (pages count)
      - for each link, visit and extract details
      - save results to ../data/mostaql_projects.csv
    """
    all_links: List[str] = []
    for p in range(1, pages + 1):
        page_url = list_page_url
        if p > 1:
            # if pagination uses ?page=N
            if "?" in list_page_url:
                page_url = f"{list_page_url}&page={p}"
            else:
                page_url = f"{list_page_url}?page={p}"
        print(f"[main] fetching links from: {page_url}")
        links = extract_project_links(page_url, limit=per_page_limit)
        if not links:
            print(f"[main] no links found on page {p}. Stopping link collection.")
            break
        # avoid duplicates
        for L in links:
            if L not in all_links:
                all_links.append(L)
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print(f"[main] total links collected: {len(all_links)}")

    projects: List[Dict[str, str]] = []
    for idx, link in enumerate(all_links, start=1):
        print(f"[main] ({idx}/{len(all_links)}) scraping: {link}")
        data = extract_project_details(link)
        if data:
            projects.append(data)
        else:
            print(f"[main] failed to extract data for {link}")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    saved_path = save_projects_csv(projects)
    print(f"[main] saved {len(projects)} projects to: {saved_path}")


if __name__ == "__main__":
    # default: scrape first listing page and up to 25 projects
    main(list_page_url="https://mostaql.com/projects", pages=1, per_page_limit=25)
