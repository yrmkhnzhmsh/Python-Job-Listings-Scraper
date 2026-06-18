"""
Job scraper for https://realpython.github.io/fake-jobs/
Extracts: job title, company name, location, and detail page URL.
Results are saved to jobs.csv in the same directory as this script.
"""

import csv
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://realpython.github.io/fake-jobs"
OUTPUT_FILE = "jobs.csv"
CSV_HEADERS = ["title", "company", "location", "url"]


def fetch_page(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return None


def extract_jobs(soup: BeautifulSoup) -> list[dict]:
    """Parse all job cards from the page and return a list of job dicts."""
    jobs = []

    job_cards = soup.select("div.card")
    if not job_cards:
        print("[WARNING] No job cards found on the page.")
        return jobs

    for card in job_cards:
        title   = card.select_one("h2.title")
        company = card.select_one("h3.company")
        location = card.select_one("p.location")
        apply_link = card.select_one("a[href*='jobs']")

        # Build the absolute URL (links on this page are relative)
        raw_href = apply_link["href"].strip() if apply_link and apply_link.get("href") else ""
        job_url = raw_href if raw_href.startswith("http") else f"{BASE_URL}/{raw_href}"

        jobs.append({
            "title":    title.get_text(strip=True)    if title    else "N/A",
            "company":  company.get_text(strip=True)  if company  else "N/A",
            "location": location.get_text(strip=True) if location else "N/A",
            "url":      job_url or "N/A",
        })

    return jobs


def save_to_csv(jobs: list[dict], filepath: str) -> None:
    """Write a list of job dicts to a CSV file."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(jobs)
    print(f"[OK] Saved {len(jobs)} jobs to '{filepath}'")


def main() -> None:
    print(f"Fetching jobs from {BASE_URL} ...")
    soup = fetch_page(BASE_URL)
    if soup is None:
        return

    jobs = extract_jobs(soup)
    if not jobs:
        print("No jobs extracted — nothing to save.")
        return

    print(f"Found {len(jobs)} job listings.")
    save_to_csv(jobs, OUTPUT_FILE)


if __name__ == "__main__":
    main()
