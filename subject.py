class Subject:
    
    def __init__(self):
        super().__init__()

def get_subjects_from_soup(soup):
    subjects = []
    table_rows = soup.select(".table-striped tbody tr")

    for row in table_rows:
        subject = Subject()

        row_cols = row.select("td")

        subject.title = row_cols[1].get_text().strip()
        subject.faculty = row_cols[2].get_text()
        subject.code = None
        subject.link = None

        a_tag = row_cols[0].find("a")
        if (a_tag == None):
            subject.code = row_cols[0].find("b").get_text().split()[0]
            subject.link = None
        else:
            subject.code = a_tag.get_text()
            subject.link = a_tag.get("href")
        subjects.append(subject)

    return subjects
