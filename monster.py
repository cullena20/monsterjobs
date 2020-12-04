#!/usr/bin/env python3
import click
from bs4 import BeautifulSoup
import requests
import db_jobs
import os


conn = db_jobs.connect()
cur = conn.cursor()
db_jobs.create_table(conn)


def get_jobs(soup):
    results = soup.find(id="SearchResults")
    job_elems = results.find_all("section", class_="card-content")
    for job_elem in job_elems:
        if job_elem.find("h2", class_="title") is None:
            continue
        else:
            title = job_elem.find("h2", class_="title").text.strip()
            company = job_elem.find("div", class_="company").text.strip()
            location = job_elem.find("div", class_="location").text.strip()
            link = job_elem.find("a")["href"]
            db_jobs.insert_job(conn, cur, title, company, location, link)


# title only exists when there are no jobs matching the criteria
# this code takes advantage of that and checks if the job yields any results
def check(soup):
    title = soup.find("h1", class_="pivot block")
    if title is None:
        return True
    else:
        return False


def open_link(n):
    link = db_jobs.get_link(cur, n)[0][0]
    os.system(f"open {link}")


@click.command(help="Look for jobs in America from monster.com.")
@click.option("-j", "--job", type=str,
              help="The job that you are looking for")
@click.option("-l", "--location", type=str,
              help="The location that you are looking at")
@click.option("-g", "--go", type=int,
              help="Go to job listing on default web browser")
@click.option("-s", "--show", is_flag=True,
              help="Show table with jobs")
@click.option("-c", "--clear", is_flag=True,
              help="Clear database containing jobs")
def main(job, location, go, show, clear):
    if show:
        print(db_jobs.display_jobs(cur))
    elif clear:
        db_jobs.clear_all(conn, cur)
    elif go:
        open_link(go)
    elif job or location:
        if job and location:
            location = location.replace(' ', '-')
            html_url = f"https://www.monster.com/jobs/search/?q={job}&where={location}"
        elif location and not job:
            location = location.replace(' ', '-')
            html_url = f"https://www.monster.com/jobs/search/?where={location}"
        elif job and not location:
            html_url = f"https://www.monster.com/jobs/search/?q={job}"
        else:
            html_url = "https://www.monster.com/jobs/search"
        html_text = requests.get(html_url).text
        soup = BeautifulSoup(html_text, "html.parser")
        if check(soup):
            get_jobs(soup)
            print(db_jobs.display_jobs(cur))
        else:
            print("Sorry, there are no jobs matching your criteria")
    else:
        print("Welcome to the job searcher. Please enter a command. Type --help to learn more.")


if __name__ == "__main__":
    main()


# learn to work with click better for mutually exclusive commands