import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv("/variables.env")

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
    soup = BeautifulSoup(r.text, 'html.parser')
    jobs = []
    for row in soup.select('tr.job'):
        title = row.get('data-position')
        company = row.get('data-company')
        link = "https://remoteok.com" + row.get('data-href')
        jobs.append({"title": title, "company": company, "location": "Remote", "url": link, "source": "RemoteOK"})
    return jobs

def scrape_weworkremotely():
    url = "https://weworkremotely.com/categories/remote-back-end-programming-jobs"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    jobs = []
    for li in soup.select('section.jobs li'):
        a = li.find('a', href=True)
        if not a:
            continue
        title = li.find('span', class_='title')
        company = li.find('span', class_='company')
        if title and company:
            job_url = "https://weworkremotely.com" + a['href']
            jobs.append({"title": title.text, "company": company.text, "location": "Remote", "url": job_url, "source": "WeWorkRemotely"})
    return jobs

def build_email_html(jobs):
    ''' Creates a nice looking email message for me'''
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
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "My Daily Remote Job Alert"
    msg['From'] = SMTP_USERNAME
    msg['To'] = RECIPIENT_EMAIL

    msg.attach(MIMEText(content_html, 'html'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(msg['From'], msg['To'], msg.as_string())

current_day = datetime.now().day
while True:
    if 1:#(now:=datetime.now()).day != current_day:
        if 1:#now.hour == 8:
            jobs = scrape_remoteok() + scrape_weworkremotely()
            if jobs:
                html = build_email_html(jobs)
                send_email(html)
                print("✅ Email sent successfully.")
            else:
                print("⚠️ No jobs scraped.")
        # current_day = now.day
    # Checks every 5 minutes
    time.sleep(3000)
