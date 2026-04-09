def get_hod(rows, start_year, end_year):
    if not rows:
        return 0, 0

    dept_count = len(set(rows))
    year_count = end_year - start_year + 1

    total_classes = dept_count * year_count
    return dept_count, total_classes

def dept_overall_percentage(rows):
    present = 0
    absent = 0

    for row in rows:
        if row['status'] == 'Present':
            present += 1
        elif row['status'] == 'Absent':
            absent += 1

    total = present + absent
    if total == 0:
        return 0

    return round((present / total) * 100)

def each_dept_std_claculation(rows, start_year, end_year):
    total_lis = {}

    year_count = end_year - start_year + 1

    for r in rows:
        dept = r['department']

        if dept not in total_lis:
            total_lis[dept] = {
                'total_class': year_count,
                'total_student': 0
            }

        total_lis[dept]['total_student'] += 1

    return total_lis

def count_teacher(teacher):
    total_teacher = 0
    teachers_list = {}
    for t in teacher:
        total_teacher += 1
        teacher_id = t['teacher_id']
        name = t['name']
        department = t['department']

        if teacher_id not in teachers_list:
            teachers_list[teacher_id]={
               'name':name,
               'department':department
            }
        
        teachers_list[teacher_id]['name'] = name
        teachers_list[teacher_id]['department'] = department

    return total_teacher , teachers_list

def teacher_timetable_for_profile(rows):
    subject = set()
    year = set()

    for r in rows:
        subject.add(r['subject_name'])
        year.add(r['year'])
        
    return list(subject), list(year)
        
def count_incharge(incharge):
    total_incharge = 0
    incharge_list = {}
    for t in incharge:
        total_incharge += 1
        incharge_id = t['incharge_id']
        name = t['name']
        department = t['department']

        if incharge_id not in incharge_list:
            incharge_list[incharge_id]={
               'name':name,
               'department':department
            }
        
        incharge_list[incharge_id]['name'] = name
        incharge_list[incharge_id]['department'] = department

    return total_incharge , incharge_list

def std_count_for_year(std):
    students_count =0

    for s in std:
        students_count += 1

    return students_count

def calcul_atend_for_year(attend):
    total_present = 0
    total_periods = 0

    for a in attend:
        status = a['status'].strip().lower()

        if status in ['present', 'absent']:
            total_periods += 1

            if status == 'present':
                total_present += 1

    if total_periods > 0:
        present_percent = round((total_present / total_periods) * 100)
    else:
        present_percent = 0

    return present_percent

def absent_std(attend):
    students = {}
    total_absent = 0
    for a in attend:
        reg_no = a['register_no']
        name = a['name']
        status = a['status'].strip().lower()

        if reg_no not in students:
            students[reg_no] = {
                "name": name,
                "present": 0,
                "absent": 0
            }

        if status == "present":
            students[reg_no]['present'] += 1
        else:
            students[reg_no]['absent'] += 1

    absent_list = {}

    for reg_no, data in students.items():
        if data['absent'] > data['present']:
            absent_list[reg_no] = data['name']
            total_absent += 1

    return absent_list, total_absent

def timetable_inst(timetable, insert_timetable, department, semester, year):
    for day, periods in timetable.items():
            for period_no, value in periods.items():
                if value:
                    subject_code, teacher_id = value.split('|')

                    if period_no == 1:
                        start_time = '09:30'
                        end_time = '10:19'

                    elif period_no == 2:
                        start_time = '10:20'
                        end_time = '11:10'

                    elif period_no == 3:
                        start_time = '11:20'
                        end_time = '12:10'

                    elif period_no == 4:
                        start_time = '12:11'
                        end_time = '13:00'

                    elif period_no == 5:
                        start_time = '13:45'
                        end_time = '14:34'

                    elif period_no == 6:
                        start_time = '14:36'
                        end_time = '15:20'

                    elif period_no == 7:
                        start_time = '15:30'
                        end_time = '16:20'

                    insert_timetable(day, department, period_no, semester, subject_code, teacher_id, year, start_time, end_time)

def sub_assign_to_tech(raw, subjects_data, insert_subject_assign, department, year, semester):

    for key, value in raw.items():

        if not key.startswith("subjects["):
            continue  
 
        _, idx, field = key.replace("]", "").split("[")

        subjects_data[int(idx)][field] = value

    # insert into DB
    for s in subjects_data.values():
        subject_code = s.get("code").strip().lower()
        subject_name = s.get("name").strip().lower()
        teacher_id = s.get("teacher").strip().lower()

        if subject_code and subject_name and teacher_id:
            insert_subject_assign(
                subject_code,
                subject_name,
                teacher_id,
                department,
                year,
                semester
            )
