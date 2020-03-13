class Course():

    def __init__(self):
        super().__init__()

def get_courses_from_subjects_soup(soup):
    table_rows = soup.select(".table-striped tbody tr")
    courses = []

    for row in table_rows:
        course = Course()    
        course.course_name = row.find("a").get_text()
        course.subject_code = course.course_name.split()[0]
        course.course_number = course.course_name.split()[1]
        course.course_link = row.find("a").get("href")
        course.course_title = row.select("td")[1].get_text()

        courses.append(course)

    return courses

def get_courses_description_and_credits_from_soup(soup):
    description = soup.select(".content p")[0].get_text()
    course_credits = soup.select(".content p")[1].get_text()

    return description, course_credits
    