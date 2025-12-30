from datetime import date, datetime, timedelta

def percentage_calculation(result_attendance):
    total_present = 0
    total_absent = 0

    for row in result_attendance:
        check_date = row['attendance_date']

        # skip weekends
        if check_date.strftime("%A") in ('Saturday', 'Sunday'):
            continue

        if row['status'] == 'Present':
            total_present += 1
        elif row['status'] == 'Absent':
            total_absent += 1

    total_periods = total_present + total_absent

    if total_periods > 0:
        present_percent = round((total_present / total_periods) * 100)
        absent_percent  = round((total_absent / total_periods) * 100)
    else:
        present_percent = 0
        absent_percent  = 0

    return present_percent, absent_percent

def current_status(result_today_status):
    if not result_today_status:
        return "Data Not Updated"

    present = 0
    absent = 0

    for row in result_today_status:
        if row['status'] == 'Present':
            present += 1
        elif row['status'] == 'Absent':
            absent += 1

    return "present" if present >= absent else "absent"

def load_timetable(result_timetable):
    timetable = {}

    for row in result_timetable:
        day = row['day']
        subject = row['subject_name']

        if day not in timetable:
            timetable[day] = []

        timetable[day].append(subject)

    return timetable

from datetime import timedelta

def build_week_attendance(base_date, register_no, timetable, student_day_attendance):
    monday = base_date - timedelta(days=base_date.weekday())
    response = {}

    for i in range(5):  # Monday–Friday
        day_date = monday + timedelta(days=i)
        day_name = day_date.strftime("%A")
        date_str = day_date.strftime("%Y-%m-%d")

        rows = student_day_attendance(register_no, date_str)

        attendance_map = {r['period_no']: r['status'] for r in rows}

        attendance_list = []
        for p in range(1, 8):
            raw_status = attendance_map.get(p)

            if raw_status:
                status = raw_status.lower()
                if status == 'present':
                    attendance_list.append('present')
                elif status == 'absent':
                    attendance_list.append('absent')
                else:
                    attendance_list.append('no-data')
            else:
                attendance_list.append('no-data')

        subjects = timetable.get(day_name, [""] * 7)

        response[day_name] = {}
        for idx in range(7):
            response[day_name][idx+1] = {
                "status": attendance_list[idx],
                "subject": subjects[idx]
            }

    return response


def get_subject_total_periods(register_no, department, semester, class_name, year,
                              get_timetable, load_timetable, dashboard_attendance):

    result_timetable = get_timetable(department, year, class_name, semester)
    timetable = load_timetable(result_timetable)

    rows = dashboard_attendance(register_no)

    subject_total = {}

    for record in rows:
        day_name = record['attendance_date'].strftime('%A')

        if day_name not in timetable:
            continue

        period = record['period_no']
        day_tt = timetable[day_name]

        if period <= len(day_tt):
            subject = day_tt[period - 1]
            if subject:
                subject_total[subject] = subject_total.get(subject, 0) + 1

    return subject_total

def get_subject_present_count(register_no, subject_total, department, semester, class_name, year, get_timetable, dashboard_attendance, load_timetable):

    result_timetable = get_timetable(department, year, class_name, semester)
    timetable = load_timetable(result_timetable)

    subject_present = {sub: 0 for sub in subject_total}

    rows = dashboard_attendance(register_no)

    for record in rows:
        if record['status'].lower() != 'present':
            continue

        day_name = record['attendance_date'].strftime('%A')
        period = record['period_no']

        if day_name not in timetable:
            continue

        day_tt = timetable[day_name]

        if period <= len(day_tt):
            subject = day_tt[period - 1]
            if subject in subject_present:
                subject_present[subject] += 1

    return subject_present

def get_subject_overview(register_no, department, semester, class_name , year, get_timetable, load_timetable, dashboard_attendance, get_subject_total_periods, get_subject_present_count):

    subject_total = get_subject_total_periods(register_no, department, semester, class_name , year, get_timetable, load_timetable, dashboard_attendance)

    subject_present = get_subject_present_count(register_no, subject_total, department, semester, class_name, year, get_timetable, dashboard_attendance, load_timetable)

    overview = []
    for i, subject in enumerate(subject_total, start=1):
        overview.append({
            "sno": i,
            "subject": subject,
            "total_periods": subject_total[subject],
            "total_present": subject_present.get(subject, 0)
        })

    return overview

def batch_calculation(admission_year):
    if admission_year:
        start_year = admission_year
        end_year = admission_year + 4

        batch =f"{start_year} - {end_year}"
    else:
        batch = 'No data'
    return batch
