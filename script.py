import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from database import *

load_dotenv("./variables.env")

# Email configuration for this script. In testing, this loads variables declared in a .env file. In production, however, they are stored in environment variables provided by the hosting site or by whichever platform I decide to run this script.

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def scrape_remoteok():
    url = "https://remoteok.com/remote-dev-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    jobs = []
    for row in soup.select("tr.job"):
        # title = row.get('data-position')
        title = (
            row.select_one(
                'td.company.position.company_and_position h2[itemprop="title"]'
            )
            .text.lstrip()
            .rstrip()
        )
        company = row.get("data-company")
        link = "https://remoteok.com" + row.get("data-href")
        if link_exists(link):
            continue
        save_link(link)
        jobs.append(
            {
                "title": title,
                "company": company,
                "location": "Remote",
                "url": link,
                "source": "RemoteOK",
            }
        )
    return jobs


def build_email_html(jobs):
    """Creates a nice looking email message for me"""
    df = pd.DataFrame(jobs)
    html_table = df.to_html(index=False, escape=False)
    email_html = f"""
    <h2>My Daily Remote Job Alert</h2>
    <p>Date: {datetime.today().strftime('%Y-%m-%d')}</p>
    {html_table}
    <p style='font-size:smaller'>Generated automatically by a Python script</p>
    """
    return email_html


def send_email(content_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "My Daily Remote Job Alert"
    msg["From"] = SMTP_USERNAME
    msg["To"] = RECIPIENT_EMAIL

    msg.attach(MIMEText(content_html, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(msg["From"], msg["To"], msg.as_string())


current_day = datetime.now().day - 1 
while True:
    # Checks for new jobs by 9 AM every day
    if (now := datetime.now()).day != current_day:
        if now.hour == 9:
            jobs = scrape_remoteok()
            if jobs:
                html = build_email_html(jobs)
                send_email(html)
                print("✅ Email sent successfully.")
            else:
                print("⚠️ No jobs scraped.")
            current_day = now.day
    # Checks every 5 minutes
    time.sleep(300)
