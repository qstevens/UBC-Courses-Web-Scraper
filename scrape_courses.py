import asyncio
import json
import time
import urllib.parse

import requests

import jsonpickle
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from course import (Course, get_courses_description_and_credits_from_soup,
                    get_courses_from_subjects_soup)
from section import Section, get_section_info_from_soup, get_sections_from_soup
from subject import Subject, get_subjects_from_soup


def format_url(session="", subject="", course="", section="", pname="subjarea", tname=""):
    root = "https://courses.students.ubc.ca/cs/courseschedule?"

    if session != "":
        sessyr = session.split()[0]
        sesscd = session.split()[1][0]
    else:
        return root

    if subject != "":
        tname = "subj-department"

    if course != "":
        tname = "subj-course"

    if section != "":
        tname = "subj-section"

    params = {
        "sessyr": sessyr,
        "sesscd": sesscd,
        "pname": pname,
        "tname": tname,
        "dept": subject,
        "course": course,
        "section": section
    }

    return root + urllib.parse.urlencode(params)

def get_url_soup(url):
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    return soup

def get_available_sessions(soup):
    session_dropdown_menu = soup.select('.breadcrumb .btn-group')[1]

    available_sessions = list(map(lambda x: x.get(
        "title"), session_dropdown_menu.select(".dropdown-menu a")))

    return available_sessions

def prompt_session_selection(available_sessions):
    for idx, session in enumerate(available_sessions):
        print(str(idx) + ":", session)

    sid = -1
    while (True):
        try:
            sid = int(input("Enter session to scrape: "))
        except ValueError:
            print("That is not a valid session. Pick a number between 0 and",
                  len(available_sessions)-1)
            continue
        if (0 <= sid < len(available_sessions)):
            print("You have selected", available_sessions[sid])
            break
        print("Enter a valid session between 0 and", len(available_sessions)-1)

    session = available_sessions[sid]
    return session

async def fetch(url, session):
    async with session.get(url) as response:
        assert response.status == 200
        return await response.read()

async def main():
    async with ClientSession() as c_session:
        tasks = []

        start_time = time.time()

        subjects = []
        courses = []
        sections = []

        # Select Session Year and Term
        ubc_courses_url = format_url()
        course_schedule_soup = get_url_soup(ubc_courses_url)
        available_sessions = get_available_sessions(course_schedule_soup)
        session = prompt_session_selection(available_sessions)

        # Get all Subjects for Session
        browser_session_subjects_url = format_url(session)
        subjects_soup = get_url_soup(browser_session_subjects_url)
        subjects = get_subjects_from_soup(subjects_soup)

        end_subjects_time = time.time()

        # Get all Courses for Subjects - Async
        for subject in subjects:
            # print(subject.code)
            subject_url = format_url(session, subject.code)
            task = asyncio.create_task(fetch(subject_url, c_session))
            tasks.append(task)
        requests = await asyncio.gather(*tasks)

        print("Subjects:", len(subjects))

        tasks = []
        for i in range(len(requests)):
            # print(response.url)
            subject = subjects[i]
            subject_courses_soup = BeautifulSoup(requests[i], 'lxml')
            subject.courses = get_courses_from_subjects_soup(
                subject_courses_soup)

            # Save Course hrefs for Async Requests
            for course in subject.courses:
                # print(course.course_name)
                courses.append(course)
                course_url = format_url(
                    session, course.subject_code, course.course_number)
                task = asyncio.create_task(fetch(course_url, c_session))
                tasks.append(task)

        end_courses_time = time.time()

        requests = await asyncio.gather(*tasks)

        print("Courses:", len(courses))

        tasks = []
        for i in range(len(requests)):
            # for response in requests:
            course = courses[i]
            # print(course.course_name)
            courses_soup = BeautifulSoup(requests[i], "lxml")
            course.sections = get_sections_from_soup(courses_soup)

            # Set Course Description and Credits for Course
            course.description, course.course_credits = get_courses_description_and_credits_from_soup(
                courses_soup)

            # Save Section hrefs for Async Requests
            for section in course.sections:
                sections.append(section)
                section_url = format_url(
                    session, section.subject_code, section.course_number, section.section_number)
                task = asyncio.create_task(fetch(section_url, c_session))
                tasks.append(task)
                # print(section.section)
        requests = await asyncio.gather(*tasks)

        end_sections_time = time.time()

        print("Sections:", len(sections))

        for i in range(len(requests)):
            # for response in requests:
            section = sections[i]
            print(section.section)
            soup = BeautifulSoup(requests[i], "lxml")
            section_info = get_section_info_from_soup(soup)

            # Set Section Info for Section
            section.building = section_info.building
            section.room = section_info.room
            section.instructors = section_info.instructors
            section.totalRemaining = section_info.totalRemaining
            section.currentlyRegistered = section_info.currentlyRegistered
            section.generalRemaining = section_info.generalRemaining
            section.restrictedRemaining = section_info.restrictedRemaining

        elapsed_courses_time = end_subjects_time - start_time
        elapsed_sections_time = end_sections_time - end_courses_time
        elapsed_section_info_time = time.time() - end_sections_time
        elapsed_time = time.time() - start_time

        print(session)

        print("Time elapsed Courses:", elapsed_courses_time)
        print("Time elapsed Sections:", elapsed_sections_time)
        print("Time elapsed Section Info:", elapsed_section_info_time)
        print("Time elapsed:", elapsed_time)

        # save data to file
        file_name = "./data/" + session + ".json"
        f = open(file_name, "w")
        f.write(jsonpickle.encode(subjects, unpicklable=False))

if __name__ == "__main__":
    asyncio.run(main())
