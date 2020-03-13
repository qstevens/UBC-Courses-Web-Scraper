import grequests
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
import requests
import urllib.parse
from bs4 import BeautifulSoup
from subject import Subject, get_subjects_from_soup
from course import Course, get_courses_from_subjects_soup, get_courses_description_and_credits_from_soup
from section import Section, get_sections_from_soup, get_section_info_from_soup
    

def format_url(session = "", subject = "", course = "", section = "", pname = "subjarea", tname = ""):
    root = "https://courses.students.ubc.ca/cs/courseschedule?"

    if session == "":
        return root

    sessyr = session.split()[0]
    sesscd = session.split()[1][0]

    params = {
        "sessyr": sessyr,
        "sesscd": sesscd,
        "pname": pname,
        "tname": tname,
        "dept": subject,
        "course": course,
        "section": section
    }

    if subject != "":
        params["tname"] = "subj-department"
        params["dept"] = subject
    
    if course != "":
        params["tname"] = "subj-course"
        params["course"] = course
        
    if section != "":
        params["tname"] = "subj-section"
        params["section"] = section

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

def main():

    subjects_map = {}
    courses_map = {}
    sections_map = {}

    # Select Session Year and Term
    ubc_courses_url = format_url()
    course_schedule_soup = get_url_soup(ubc_courses_url)
    available_sessions = get_available_sessions(course_schedule_soup)
    session = prompt_session_selection(available_sessions)

    # Get all Subjects for Session
    browser_session_subjects_url = format_url(session)
    subjects_soup = get_url_soup(browser_session_subjects_url)
    subjects = get_subjects_from_soup(subjects_soup)

    # Get all Courses for Subjects - Async
    for subject in subjects:
        print(subject.code)
        subjects_map[format_url(session, subject.code)] = subject
    
    rs = (grequests.get(u) for u in subjects_map.keys())
    requests = grequests.map(rs)

    for response in requests:
        # print(response.url)
        subject = subjects_map[response.url]
        subject_courses_soup = BeautifulSoup(response.content, 'lxml')
        subject.courses = get_courses_from_subjects_soup(subject_courses_soup)

        # Save Course hrefs for Async Requests
        for course in subject.courses:
            print(course.course_name)
            courses_map[format_url(session, course.subject_code, course.course_number)] = course

    # Get all Sections for Courses - Async
    rs = (grequests.get(u) for u in courses_map.keys())
    
    requests = grequests.map(rs)

    for response in requests:
        print(response.url)
        course = courses_map[response.url]
        courses_soup = BeautifulSoup(response.content, "lxml")
        course.sections = get_sections_from_soup(courses_soup)

        # Set Course Description and Credits for Course
        course.description, course.course_credits = get_courses_description_and_credits_from_soup(courses_soup)
        
        # Save Section hrefs for Async Requests
        for section in course.sections:
            sections_map[format_url(session, section.subject_code, section.course_number, section.section_number)] = section
            print(section.section)

    # Get Section Info for Sections - Async
    rs = (grequests.get(u) for u in sections_map.keys())
    requests = grequests.map(rs)

    for response in requests:
        section = sections_map[response.url]
        soup = BeautifulSoup(response.content, "lxml")
        section_info = get_section_info_from_soup(soup)

        # Set Section Info for Section
        section.building = section_info.building
        section.room = section_info.room
        section.instructors = section_info.instructors
        section.totalRemaining = section_info.totalRemaining
        section.currentlyRegistered = section_info.currentlyRegistered
        section.generalRemaining = section_info.generalRemaining
        section.restrictedRemaining = section_info.restrictedRemaining

        print(section.instructors)

    print(len("Subjects:", subjects_map.keys()))
    print(len("Courses:", subjects_map.keys()))
    print(len("Sections:", subjects_map.keys()))

    return

if __name__ == "__main__":
    main()