class Section:
    def __init__(self):
        super().__init__()

def get_sections_from_soup(soup):

    sections = []

    table_rows = soup.find("thead").find_next_siblings("tr")

    for row in table_rows:
        section = Section()

        section.section = row.select("td")[1].get_text()
        if section.section == "":
            continue
        section.subject_code = section.section.split()[0]
        section.course_number = section.section.split()[1]
        section.section_number = section.section.split()[2]
        section.blocked = row.select("td")[0].get_text()
        section.href = row.select("td")[1].find("a").get("href")
        section.activity = row.select("td")[2].get_text()
        section.term = row.select("td")[3].get_text()
        section.interval = row.select("td")[4].get_text()
        section.days = row.select("td")[5].get_text()
        section.start = row.select("td")[6].get_text()
        section.end = row.select("td")[7].get_text()

        comments_data = row.find(".section-comments .accordion-inner")
        section.comments = comments_data.get_text() if comments_data != None else ""
        
        sections.append(section)

    return sections

def get_section_info_from_soup(soup):
    section = Section()

    section_table = soup.select(".table-striped")[0].find("thead")
    section.building = None
    section.room = None
    if section_table != None:
        section_row = section_table.find_next_siblings("td")
        section.building = section_row[4].get_text()
        section.room = section_row[5].get_text()

    seat_summary_header = soup.find("strong", string="Seat Summary")
    section.totalRemaining = None
    section.currentlyRegistered = None
    section.generalRemaining = None
    section.restrictedRemaining = None
    if seat_summary_header != None:
        seat_summary = seat_summary_header.parent.parent.find_next_siblings(
            "tr")
        section.totalRemaining = seat_summary[0].select("td")[1].get_text()
        section.currentlyRegistered = seat_summary[1].select("td")[
            1].get_text()
        section.generalRemaining = seat_summary[2].select("td")[1].get_text()
        section.restrictedRemaining = seat_summary[3].select("td")[
            1].get_text()

    instructors_hook = soup.find("td", text="Instructor:  ")
    section.instructors = []
    if instructors_hook != None:
        instructors_data = instructors_hook.parent.parent
        for instructor in instructors_data:
            section.instructors.append(instructor.get_text())
    else:
        section.instructors.append("TBA")

    return section
