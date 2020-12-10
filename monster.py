#!/usr/bin/env python3
import click
from bs4 import BeautifulSoup
import requests
import db_jobs
import os


conn = db_jobs.connect()
cur = conn.cursor()
db_jobs.create_table(conn)


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


def get_description(n):
    try:
        html_url = db_jobs.get_link(cur, n)[0][0]
        html_text = requests.get(html_url).text
        soup = BeautifulSoup(html_text, 'html.parser')
        description = soup.find("div", {"name": "sanitizedHtml"}).text
        return description
    except IndexError:
        return "There are no jobs in the database right now. Search for a job before looking for a description."

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


@click.command(help="Look for jobs in America from monster.com.")
@click.option("-j", "--job", type=str,
              help="The job that you are looking for")
@click.option("-l", "--location", type=str,
              help="The location that you are looking at")
@click.option("-d", "--description", type=int,
              help="Print out a description of a job in the database")
@click.option("-g", "--go", type=int,
              help="Go to job listing on default web browser")
@click.option("-s", "--show", is_flag=True,
              help="Show table with jobs")
@click.option("-c", "--clear", is_flag=True,
              help="Clear database containing jobs")
def main(job, location, go, description, show, clear):
    if show:
        click.echo(db_jobs.display_jobs(cur))
    elif clear:
        db_jobs.clear_all(conn, cur)
        click.echo("The jobs in the database have been cleared.")
    elif go:
        open_link(go)
    elif description:
        click.echo(get_description(description))
    elif job or location:
        html_text = requests.get("https://www.monster.com/jobs/search", params={'q': job, 'where': location}).text
        soup = BeautifulSoup(html_text, "html.parser")
        if check(soup):
            get_jobs(soup)
            print(db_jobs.display_jobs(cur))
        else:
            click.echo("Sorry, there are no jobs matching your criteria")
    else:
        click.echo("Welcome to the job searcher. Please enter a command. Type --help to learn more.")


if __name__ == "__main__":
    main()
