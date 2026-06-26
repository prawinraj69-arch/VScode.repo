"""
Daily software engineering jobs email sender.

Source: The Muse public jobs API (instead of Indeed).
Behavior:
- Sends one email immediately when started
- Continues sending every day at RUN_TIME
"""

from __future__ import annotations

import json
import os
import re
import smtplib
import subprocess
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

try:
    import requests
    import schedule
except ImportError:
    print("Installing missing packages: requests schedule")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "schedule"])
    import requests
    import schedule


# ─────────────────────────────────────────────
#  CONFIGURATION  (edit only these values)
# ─────────────────────────────────────────────
SENDER_EMAIL = "praveen.raj.mohan.learn@gmail.com"
SENDER_PASSWORD = "fcva fbmk triq tyuv"
RECIPIENT_EMAIL = "praveen.raj.mohan.learn@gmail.com"
RUN_TIME = "09:01"
NUM_JOBS = 10
JOB_TITLE = "software engineering"
LOCATION = "Chennai"
TRIGGER_KEYWORDS = ["etl", "sql", "jira"]
# ─────────────────────────────────────────────


class MuseJobScraper:
    """Fetches job listings from The Muse public jobs API."""

    def __init__(self):
        self.base_url = "https://www.themuse.com/api/public/jobs"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.jobs_file = "jobs_cache.json"
        self.max_pages = 8
        self.job_keyword = " ".join(JOB_TITLE.lower().split())
        self.trigger_keywords = [k.strip().lower() for k in TRIGGER_KEYWORDS if k.strip()]
        self.role_keywords = [
            "software engineer",
            "software developer",
            "developer",
            "backend engineer",
            "full stack",
            "fullstack",
            "qa engineer",
            "test engineer",
            "automation engineer",
            "sdet",
            "sde",
            "data engineer",
        ]

    def _is_target_job(self, title: str, contents: str, levels: List[str], categories: List[str]) -> bool:
        merged = f"{title} {contents}".lower()
        normalized = " ".join(merged.split())

        role_match = self.job_keyword in normalized or any(token in normalized for token in self.role_keywords)
        if not role_match:
            return False

        enriched = f"{normalized} {' '.join(levels).lower()} {' '.join(categories).lower()}"
        keyword_hit = any(keyword in enriched for keyword in self.trigger_keywords)
        return keyword_hit

    def _normalize_job(self, item: Dict, idx: int) -> Dict[str, str]:
        company = (item.get("company") or {}).get("name", "N/A")
        title = item.get("name", "N/A")
        locations = item.get("locations") or []
        levels = item.get("levels") or []
        categories = item.get("categories") or []
        refs = item.get("refs") or {}

        location_text = ", ".join(loc.get("name", "") for loc in locations if loc.get("name")) or "Remote / Unspecified"
        level_text = ", ".join(level.get("name", "") for level in levels if level.get("name")) or "Not specified"
        category_text = ", ".join(cat.get("name", "") for cat in categories if cat.get("name")) or "Not specified"
        posted_at = item.get("publication_date") or datetime.now().strftime("%Y-%m-%d")
        link = refs.get("landing_page") or "https://www.themuse.com/jobs"

        raw_contents = item.get("contents", "") or ""
        summary = re.sub(r"<[^>]+>", " ", raw_contents)
        summary = re.sub(r"\s+", " ", summary).strip()

        return {
            "index": str(idx),
            "title": title,
            "company": company,
            "location": location_text,
            "salary": "Not specified",
            "experience": level_text,
            "category": category_text,
            "description": summary[:700] if summary else "No description available",
            "link": link,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "posted_date": posted_at,
        }

    def scrape_jobs(self, num_jobs=NUM_JOBS):
        print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] Fetching jobs from The Muse API...")
        try:
            jobs: List[Dict[str, str]] = []
            running_index = 1

            for page in range(1, self.max_pages + 1):
                params = {
                    "page": page,
                    "location": LOCATION,
                    "descending": "true",
                }
                response = requests.get(self.base_url, params=params, headers=self.headers, timeout=20)
                response.raise_for_status()
                payload = response.json()
                results = payload.get("results", [])

                if not results:
                    break

                for item in results:
                    title = item.get("name", "")
                    contents = item.get("contents", "") or ""
                    levels = [lv.get("name", "") for lv in (item.get("levels") or [])]
                    categories = [cg.get("name", "") for cg in (item.get("categories") or [])]
                    locations = [loc.get("name", "") for loc in (item.get("locations") or [])]
                    location_merged = " ".join(locations).lower()

                    if LOCATION.lower() not in location_merged and "india" not in location_merged:
                        continue
                    if not self._is_target_job(title, contents, levels, categories):
                        continue

                    jobs.append(self._normalize_job(item, running_index))
                    print(f"  [OK] [{running_index:02}] {jobs[-1]['title']} | {jobs[-1]['company']}")
                    running_index += 1

                    if len(jobs) >= num_jobs:
                        break

                if len(jobs) >= num_jobs:
                    break

            if jobs:
                self._save_cache(jobs)
                print(f"\n  [OK] Scraped {len(jobs)} job(s) successfully.")
                return jobs

            print("  [WARN] No matching jobs found from API response.")
            print("  [INFO] Loading cached jobs...")
            return self._load_cache()

        except requests.RequestException as exc:
            print(f"  [WARN] Network error: {exc}")
            print("  [INFO] Loading cached jobs...")
            return self._load_cache()
        except Exception as exc:
            print(f"  [WARN] Unexpected API parsing error: {exc}")
            return self._load_cache()

    # ── cache helpers ──────────────────────────────────────

    def _save_cache(self, jobs):
        try:
            with open(self.jobs_file, "w") as fh:
                json.dump(jobs, fh, indent=2)
            print(f"  [OK] Cache saved -> {self.jobs_file}")
        except Exception as exc:
            print(f"  [WARN] Cache write error: {exc}")

    def _load_cache(self):
        try:
            if os.path.exists(self.jobs_file):
                with open(self.jobs_file, "r") as fh:
                    data = json.load(fh)
                print(f"  [OK] Loaded {len(data)} job(s) from cache.")
                return data
        except Exception as exc:
            print(f"  [WARN] Cache read error: {exc}")
        return []


class JobEmailNotifier:
    """Sends a formatted HTML email with job listings via Gmail SMTP."""

    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self, sender_email, sender_password, recipient_email):
        self.sender_email    = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

    def send(self, jobs):
        """
        Send job notification email.

        Args:
            jobs (list[dict]): Job records to include in the email.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not jobs:
            print("  [WARN] No jobs to send. Email skipped.")
            return False

        subject = (
            f"Software Engineering Jobs in Chennai "
            f"(keywords: {', '.join(TRIGGER_KEYWORDS)}) - {datetime.now():%d %b %Y}"
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = self.sender_email
        msg["To"]      = self.recipient_email
        msg.attach(MIMEText(self._html_body(jobs), "html"))

        try:
            print(f"\n  Sending email to {self.recipient_email}...")
            with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            print(f"  [OK] Email sent with {len(jobs)} job(s).")
            return True

        except smtplib.SMTPAuthenticationError:
            print("  [ERROR] Gmail authentication failed.")
            print("  Use an App Password, not your normal Gmail password.")
            return False
        except Exception as exc:
            print(f"  [ERROR] Email send error: {exc}")
            return False

    def _html_body(self, jobs):
        today = datetime.now().strftime("%A, %d %B %Y")
        cards_html = ""
        for job in jobs:
            cards_html += f"""
            <div class="card">
              <div class="job-title">{job['index']}. {job['title']}</div>
              <div class="meta">🏢 <strong>{job['company']}</strong></div>
              <div class="meta">📍 {job['location']}</div>
                            <div class="salary">Salary: {job['salary']}</div>
                            <div class="meta">Experience Level: {job['experience']}</div>
                            <div class="meta">Category: {job['category']}</div>
              <div class="desc"><strong>Summary:</strong> {job['description']}</div>
              <a href="{job['link']}" class="btn">View &amp; Apply →</a>
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<style>
  body        {{ font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }}
  .wrapper    {{ max-width: 700px; margin: auto; background: white;
                border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,.1); }}
  .header     {{ background: #1a3c5e; color: white; padding: 24px 28px; }}
  .header h1  {{ margin: 0 0 6px; font-size: 22px; }}
  .header p   {{ margin: 0; font-size: 14px; opacity: .85; }}
  .body       {{ padding: 20px 28px; }}
  .card       {{ border: 1px solid #dce3ea; border-radius: 6px; padding: 16px;
                margin-bottom: 16px; background: #fafcfe; }}
  .job-title  {{ font-size: 17px; font-weight: bold; color: #1a3c5e; margin-bottom: 6px; }}
  .meta       {{ font-size: 13px; color: #444; margin: 3px 0; }}
  .salary     {{ font-size: 14px; color: #27ae60; font-weight: bold; margin: 8px 0; }}
  .desc       {{ font-size: 13px; color: #555; line-height: 1.6; margin: 8px 0; }}
  .btn        {{ display: inline-block; background: #1a3c5e; color: white;
                padding: 9px 18px; border-radius: 4px; text-decoration: none;
                font-size: 13px; margin-top: 8px; }}
  .footer     {{ padding: 16px 28px; font-size: 11px; color: #aaa;
                border-top: 1px solid #eee; text-align: center; }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
        <h1>Software Engineering Jobs - Chennai</h1>
    <p>Trigger keywords: {', '.join(TRIGGER_KEYWORDS)}</p>
    <p>Top {len(jobs)} job(s) found &nbsp;·&nbsp; {today}</p>
  </div>
  <div class="body">
    {cards_html}
  </div>
  <div class="footer">
        Automated daily job alert · Source: The Muse public jobs API ·
    Delivered to {self.recipient_email}
  </div>
</div>
</body>
</html>"""


class DailyJobScheduler:
    """Wraps the scraper + notifier into a recurring daily task."""

    def __init__(self, scraper, notifier, run_time=RUN_TIME):
        self.scraper   = scraper
        self.notifier  = notifier
        self.run_time  = run_time

    def _run_task(self):
        sep = "=" * 60
        print(f"\n{sep}")
        print(f"  Daily Job Task | {datetime.now():%Y-%m-%d %H:%M:%S}")
        print(sep)
        jobs = self.scraper.scrape_jobs()
        self.notifier.send(jobs)
        print(sep + "\n")

    def start(self):
        """Schedule daily run and execute once immediately for verification."""
        schedule.every().day.at(self.run_time).do(self._run_task)

        print(f"\n  [OK] Scheduler started. Daily run at {self.run_time}")
        print("  [OK] Running immediately for first-time test...\n")
        self._run_task()

        print(f"  [OK] Waiting for next scheduled run at {self.run_time}.")
        print("  Press Ctrl+C to stop.\n")
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n  [INFO] Scheduler stopped by user.")


# ──────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Software Engineering Job Notifier")
    print(f"  Role   : {JOB_TITLE}")
    print(f"  Trigger: {', '.join(TRIGGER_KEYWORDS)}")
    print(f"  City   : {LOCATION}")
    print(f"  Email  : {RECIPIENT_EMAIL}")
    print(f"  Time   : Every day at {RUN_TIME}")
    print("  Source : The Muse API")
    print("=" * 60)

    scraper   = MuseJobScraper()
    notifier  = JobEmailNotifier(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL)
    scheduler = DailyJobScheduler(scraper, notifier, run_time=RUN_TIME)
    scheduler.start()


if __name__ == "__main__":
    main()