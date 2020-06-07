import re

from bs4 import BeautifulSoup


def clean(text):
    text = ' '.join(text.strip().split())
    if text == "":
        return None

    return text


def get_and_clean_text(element):
    return clean(element.text)


def link_to_id(text):
    # "...id.php?id=12540" -> 12540
    return int(re.findall(r'id=(\d+)', text)[0])


def parse(mgp_id, raw_html):
    '''
        Parse a raw html string fetched from the web, e.g.
        https://genealogy.math.ndsu.nodak.edu/id.php?id=216676

        return a dict

        {
            'id': int,
            'name': str,
            'thesis': str,
            'school': str,
            'country': str,
            'year': str,
            'subject': str,
            'advisors': [str],
            'students': [str],
        }

        The string values are None if not found,
        while advisors and students are the empty list if not found
    '''
    parsed_html = BeautifulSoup(raw_html, "html.parser")
    main_content = parsed_html.find(attrs={'id': 'mainContent'})

    def try_find(*args, **kwargs):
        if_found = kwargs.pop('if_found', lambda x: x)
        result = main_content.find(*args, **kwargs)
        if result:
            return if_found(result)
        else:
            return None

    name = try_find('h2', if_found=get_and_clean_text)
    thesis_title = try_find(attrs={'id': 'thesisTitle'},
                            if_found=get_and_clean_text)
    country = try_find('img',
                       attrs={'src': re.compile('flag')},
                       if_found=lambda x: x['title'])
    subject = try_find(text=re.compile('Mathematics Subject Classification:'),
                       if_found=lambda x: clean(x.split(': ')[1]))
    phd = try_find(text=re.compile('Ph.D.'), if_found=lambda x: x.parent)

    year = None
    school = None
    if phd:
        try:
            school = phd.text[5:-4].strip()
            year = int(phd.text.split()[-1])
        except Exception as e:
            pass

    advisors = set()
    advisor_text_markers = main_content.find_all(
        text=re.compile('Advisor( [0-9]*)?:'))
    for advisor_text_marker in advisor_text_markers:
        advisor_links = advisor_text_marker.parent.find_all(
            'a', attrs={'href': re.compile('id=[0-9]+')})
        advisors |=  set([link_to_id(a['href']) for a in advisor_links])

    students = []
    student_table = try_find('table')
    if student_table:
        rows = student_table.find_all('tr')
        rows = [x for x in rows if not x.find('th')]  # remove header
        student_links = [tr.find('td').find('a')['href'] for tr in rows]
        students = [link_to_id(s) for s in student_links]

    return {
        'id': mgp_id,
        'name': name,
        'thesis': thesis_title,
        'school': school,
        'country': country,
        'year': year,
        'subject': subject,
        'advisors': advisors,
        'students': students,
    }
