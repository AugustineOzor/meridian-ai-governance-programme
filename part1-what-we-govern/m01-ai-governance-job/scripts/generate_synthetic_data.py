"""Generate synthetic expense and proxy-log data for Meridian Gulf Bank (fictional).

All data is synthetic. Re-running with the same seed reproduces the same files.
Usage:  python scripts/generate_synthetic_data.py
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SEED = 42
random.seed(SEED)
DATA = Path(__file__).resolve().parents[1] / "data"

DEPARTMENTS = ["Retail", "SME Lending", "HR", "Compliance", "Operations", "IT", "Marketing", "Finance"]
EMPLOYEES = [f"E{1000 + i}" for i in range(120)]
EMP_DEPT = {e: random.choice(DEPARTMENTS) for e in EMPLOYEES}
ADOPTERS = random.sample(EMPLOYEES, 45)  # staff who use AI tools at all
START = date(2026, 7, 1)
DAYS = 92  # one quarter

# (merchant, description, typical amount QAR, preferred departments)
AI_EXPENSES = [
    ("OPENAI *CHATGPT SUBSCR", "ChatGPT Plus monthly", 73, ["Marketing", "SME Lending", "HR"]),
    ("OTTER.AI", "Otter Pro subscription", 62, ["HR", "Operations"]),
    ("FIREFLIES.AI", "Fireflies meeting notes", 69, ["Retail", "Compliance"]),
    ("MIDJOURNEY INC", "Midjourney basic plan", 37, ["Marketing"]),
    ("PERPLEXITY AI", "Perplexity Pro", 73, ["Compliance", "Finance"]),
    ("DEEPL SE", "DeepL Pro translation", 33, ["Compliance", "Operations"]),
    ("OPENAI LLC API", "API usage - project credits", 410, ["IT"]),
    ("GAMMA TECH", "Gamma presentation AI", 37, ["Marketing", "SME Lending"]),
]
NOISE_EXPENSES = [
    ("UBER *TRIP", "Client visit taxi", 45), ("TALABAT", "Team lunch", 180),
    ("AMAZON WEB SERVICES", "Dev sandbox", 950), ("ADOBE *ACROPRO", "Acrobat Pro", 60),
    ("LINKEDIN PREMIUM", "Recruiter seat", 290), ("ZOOM.US", "Webinar licence", 55),
    ("QATAR AIRWAYS", "Travel Riyadh", 2100), ("JARIR BOOKSTORE", "Stationery", 85),
]

AI_DOMAINS = [
    ("chatgpt.com", ["Marketing", "SME Lending", "HR", "Retail", "Finance"]),
    ("gemini.google.com", ["Retail", "Operations"]),
    ("claude.ai", ["IT", "Compliance"]),
    ("api.openai.com", ["IT"]),
    ("otter.ai", ["HR", "Operations"]),
    ("huggingface.co", ["IT"]),
    ("www.perplexity.ai", ["Compliance", "Finance"]),
    ("copilot.microsoft.com", DEPARTMENTS),  # approved (AI-005)
    ("www.deepl.com", ["Compliance", "Operations"]),
    ("gamma.app", ["Marketing", "SME Lending"]),
]
NOISE_DOMAINS = ["outlook.office365.com", "www.google.com", "teams.microsoft.com", "www.qcb.gov.qa",
                 "www.bloomberg.com", "github.com", "www.linkedin.com", "sharepoint.com", "www.bbc.com"]


def pick_employee(prefer):
    pool = [e for e in ADOPTERS if EMP_DEPT[e] in prefer] or ADOPTERS
    return random.choice(pool)


def make_expenses():
    rows = []
    for merchant, desc, amt, depts in AI_EXPENSES:
        for _ in range(random.randint(3, 9)):
            emp = pick_employee(depts)
            rows.append([START + timedelta(days=random.randrange(DAYS)), emp, EMP_DEPT[emp],
                         merchant, desc, round(amt * random.uniform(0.9, 1.3), 2)])
    for merchant, desc, amt in NOISE_EXPENSES:
        for _ in range(random.randint(8, 20)):
            emp = random.choice(EMPLOYEES)
            rows.append([START + timedelta(days=random.randrange(DAYS)), emp, EMP_DEPT[emp],
                         merchant, desc, round(amt * random.uniform(0.7, 1.4), 2)])
    df = pd.DataFrame(rows, columns=["date", "employee_id", "department", "merchant", "description", "amount_qar"])
    return df.sort_values("date").reset_index(drop=True)


def make_proxy_logs():
    rows = []
    for domain, depts in AI_DOMAINS:
        for _ in range(random.randint(40, 160)):
            emp = pick_employee(depts)
            rows.append([START + timedelta(days=random.randrange(DAYS)), emp, EMP_DEPT[emp], domain,
                         random.randint(2_000, 900_000), random.randint(1, 60)])
    for domain in NOISE_DOMAINS:
        for _ in range(random.randint(150, 400)):
            emp = random.choice(EMPLOYEES)
            rows.append([START + timedelta(days=random.randrange(DAYS)), emp, EMP_DEPT[emp], domain,
                         random.randint(1_000, 400_000), random.randint(1, 40)])
    df = pd.DataFrame(rows, columns=["date", "user_id", "department", "domain", "bytes_out", "requests"])
    return df.sort_values("date").reset_index(drop=True)


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    make_expenses().to_csv(DATA / "expenses_q3_2026.csv", index=False)
    make_proxy_logs().to_csv(DATA / "proxy_logs_q3_2026.csv", index=False)
    print(f"Wrote synthetic data to {DATA}")
