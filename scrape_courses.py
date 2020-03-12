import requests
from bs4 import BeautifulSoup
from models.subject import Subject
from models.course import Course
from models.section import Section

root = "https://courses.students.ubc.ca"

def get_url_soup(url):
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    return soup

def get_courses_from_soup(soup):
    table_rows = soup.select(".table-striped tbody tr")
    courses = []

    for row in table_rows:
        course_name = row.find("a").get_text()
        course_link = row.find("a").get("href")
        course_title = row.select("td")[1].get_text()

        soup = get_url_soup(root + course_link)
        print(course_name)
        description, course_credits, sections = get_description_credits_and_sections_from_soup(soup)
        course = Course(course_name, course_title, course_link, description, course_credits)
        course.sections = sections
        courses.append(course)
    return courses

def get_description_credits_and_sections_from_soup(soup):
    description = soup.select(".content p")[0].get_text()
    course_credits = soup.select(".content p")[1].get_text()

    sections = []

    table_rows = soup.find("thead").find_next_siblings("tr")
    # print(table_rows)
    for row in table_rows:
        section = Section()
        section.blocked = row.select("td")[0].get_text()
        section.section = row.select("td")[1].get_text()
        section.href = row.select("td")[1].find("a").get("href")
        section.activity = row.select("td")[2].get_text()
        section.term = row.select("td")[3].get_text()
        section.interval = row.select("td")[4].get_text()
        section.days = row.select("td")[5].get_text()
        section.start = row.select("td")[6].get_text()
        section.end = row.select("td")[7].get_text()
        comments_data = row.find(".section-comments .accordion-inner")
        section.comments = comments_data.get_text() if comments_data != None else ""
        print(section.section)
        soup = get_url_soup(root + section.href)
        section_info = get_section_info_from_soup(soup)
        section.building = section_info.building
        section.room = section_info.room
        section.instructors = section_info.instructors
        section.totalRemaining = section_info.totalRemaining
        section.currentlyRegistered = section_info.currentlyRegistered
        section.generalRemaining = section_info.generalRemaining
        section.restrictedRemaining = section_info.restrictedRemaining
        sections.append(section)

    return description, course_credits, sections

def get_section_info_from_soup(soup):
    section = Section()

    row = soup.select(".table-striped")[0].find("thead").find_next_siblings("td")
    section.building = row[4].get_text()
    section.room = row[5].get_text()

    seat_summary = soup.select("thead")[2].parent.select("tr")
    print(seat_summary)
    section.totalRemaining = seat_summary[0].select("td")[1].get_text()
    section.currentlyRegistered = seat_summary[1].select("td")[1].get_text()
    section.generalRemaining = seat_summary[2].select("td")[1].get_text()
    section.restrictedRemaining = seat_summary[3].select("td")[1].get_text()

    instructors_data = soup.select("table")[2].select("td")[1:]
    section.instructors = []
    for instructor in instructors_data:
        section.instructors.append(instructor.get_text())
    print(section.instructors)
    return section

browse_courses_url = root+"/cs/courseschedule?pname=subjarea&tname=subj-all-departments"

soup = get_url_soup(browse_courses_url)

session_dropdown_menu = soup.select('.breadcrumb .btn-group')[1]

available_sessions = list(map(lambda x: x.get("title"), session_dropdown_menu.select(".dropdown-menu a")))

for idx, session in enumerate(available_sessions):
    print(str(idx) + ":", session)

sid = -1
while (True):    
    try:
        sid = int(input("Enter session to scrape: "))
    except ValueError:
        print("That is not a valid session. Pick a number between 0 and", len(available_sessions)-1)
        continue
    if (0 <= sid < len(available_sessions)):
        print("You have selected", available_sessions[sid])
        break
    print("Enter a valid session between 0 and", len(available_sessions)-1)

session = available_sessions[sid]
sessyr = session.split()[0]
sesscd = session.split()[1][0]

browser_session_url = root+"/cs/courseschedule?tname=subj-all-departments&sessyr="+sessyr+"&sesscd="+sesscd+"&pname=subjarea"

soup = get_url_soup(browser_session_url)

table_rows = soup.select(".table-striped tbody tr")

subjects = []

for row in table_rows:
    row_cols = row.select("td")
    

    title = row_cols[1].get_text()
    faculty = row_cols[2].get_text()
    code = None
    link = None
    
    a_tag = row_cols[0].find("a")
    if (a_tag == None):
        code = row_cols[0].find("b").get_text().split()[0]
        link = None
    else:
        code = row_cols[0].find("a").get_text()
        link = row_cols[0].find("a").get("href")

    subject = Subject(code, faculty, title, link)
    subjects.append(subject)
    print(code)

    subject_url = root + link
    soup = get_url_soup(subject_url)
    subject.courses = get_courses_from_soup(soup)


