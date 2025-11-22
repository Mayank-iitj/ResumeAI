from resume_screening.utils import extract_years_of_experience

def test_date_range_years():
    text = "Worked at Company A Jan 2019 - Mar 2021; Company B Apr 2021 - Present"
    years = extract_years_of_experience(text)
    assert years >= 2.0 and years <= 10.0
