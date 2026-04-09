import pandas as pd
import os

def merge_dept_and_students(departments, dept_counts):

    count_map = {
        row['department'].strip().lower(): row['total_students']
        for row in dept_counts
    }

    merged_data = []

    for dept in departments:
        dept_name = dept['department_name'].strip().lower()

        merged_data.append({
            'dept_name': dept_name,
            'dept_code': dept['department_code'].strip().lower(),
            'total_students': count_map.get(dept_name, 0)
        })

    return merged_data

def inst_excel_data_for_hod(inst_hod, file, check_hod):

    msg = ("No file uploaded") 
    catagory = ("error")
    if file and file.filename != "":
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            hod_id = str(row['hod_id']).strip().lower()
            department = str(row['department']).strip().lower()
            email = row['email'].strip().lower()
            name = row['name'].strip().lower()
            password = (str(row['password']))
            phone = str(row['phone'])
            gender = row['gender'].strip().lower()
            experience = int(row['experience'])
            start_year = int(row['start_year'])
            end_year = int(row['end_year'])
            
            if all([hod_id, name, email, phone, experience, password, gender, department,start_year, end_year]):
                if not check_hod(department,hod_id):
                    inst_hod(hod_id, name, email, phone, experience, password, gender, department, start_year,end_year)
                    msg = ("HOD Excel uploaded successfully") 
                    catagory = ("success")

                else:
                    msg = ("HOD Already Assigned to this Department")
                    catagory = ("error")
            else:
                msg = ("Some Input are Null")
                catagory = ("error")

        return msg , catagory
    
def inst_excel_data_for_incharge(check_class_assigned, inst_to_incharge, file, check_incharge):

    msg = ("No file uploaded") 
    catagory = ("error")
    if file and file.filename != "":
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            incharge_id = str(row['incharge_id']).strip().lower()
            department = str(row['department']).strip().lower()
            email = row['email'].strip().lower()
            name = row['name'].strip().lower()
            password = (str(row['password']))
            phone = str(row['phone'])
            gender = row['gender'].strip().lower()
            experience = int(row['experience'])
            year = int(row['year'])
            semester = int(row['semester'])
            incharge_year = int(row["incharge_year"])
            
            if all([incharge_id, email, name, phone, department, gender, password, experience, year, semester,incharge_year]):
                if check_incharge(incharge_id, email, phone, department):
                    msg = ("Incharge already exists (ID / Email / Phone)")
                    catagory = ("error")

                elif check_class_assigned(department, year, semester):
                    msg = ("Class already assigned to another incharge")
                    catagory = ("error")
                else:
                    inst_to_incharge(incharge_id, email, name, phone,department, gender, password, experience, year, semester,incharge_year)
                    msg = ('incharge Added Successfully!')
                    catagory = ('success')
            else:
                msg = ('All fields are required!')
                catagory = ("error")
                
        return msg , catagory
    
def inst_excel_data_for_teacher(inst_to_teachers, file, check_teachers):
    msg = ("No file uploaded") 
    catagory = ("error")
    if file and file.filename != "":
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            teacher_id = str(row['teacher_id']).strip().lower()
            department = str(row['department']).strip().lower()
            email = row['email'].strip().lower()
            name = row['name'].strip().lower()
            password = (str(row['password']))
            phone = str(row['phone'])
            gender = row['gender'].strip().lower()
            experience = int(row['experience'])
            teacher_year = int(row['teacher_year'])
            
            if all([teacher_id, email, name, phone, department, gender, password, experience,teacher_year]):
                if not check_teachers(teacher_id, email, phone, department):
                    inst_to_teachers(
                        teacher_id, email, name, phone,
                        department, gender, password, experience,teacher_year
                    )
                    msg = ('Teacher Added Successfully!')
                    catagory = ('success')
                else:
                    msg = ('Teacher Already Exists!')
                    catagory = ("error")
            else:
                msg = ('All fields are required!')
                catagory = ("error")
                
        return msg , catagory
    
def inst_excel_data_for_student(inst_to_students, file, check_students):
    msg = ("No file uploaded") 
    catagory = ("error")
    if file and file.filename != "":
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            register_no = str(row['register_no']).strip().lower()
            department = str(row['department']).strip().lower()
            email = row['email'].strip().lower()
            name = row['name'].strip().lower()
            password = (str(row['password']))
            phone = str(row['phone'])
            gender = row['gender'].strip().lower()
            year = int(row['year'])
            semester = int(row['semester'])
            dob = row['dob']
            admission_year = int(row['admission_year'])
            academic_year = str(row['academic_year']).strip()

            
            if all([register_no, email, name, phone, department, gender, password, year, semester, dob, admission_year, academic_year]):
                if not check_students(register_no, phone, email):
                    inst_to_students(
                        register_no, email, name, phone, department, gender, password,
                        year, semester, dob, admission_year, academic_year
                    )
                    msg = ('Students Added Successfully!')
                    catagory = ('success')
                else:
                    msg = ('Student Already Exists!')
                    catagory = ("error")
            else:
                msg = ('All fields are required!')
                catagory = ("error")
                
        return msg , catagory
    
def promote_std_sem_year(students, update_std_year_sem):

    passout_std_lis = []
    for s in students:
        register_no = s['register_no']
        name = s['name']
        department = s['department']
        academic_year = s['academic_year']
        semester = s['semester']
        email = s['email']
        phone = s['phone']
        year = s['year']

        if semester % 2 == 0: 
            year += 1
        semester += 1

        update_std_year_sem(register_no, year, semester)

        if year > 4:
            passout_std_lis.append({
                'register_no':register_no,
                'name':name,
                'department':department,
                'email':email,
                'phone':phone,
                'academic_year':academic_year
            })

    return passout_std_lis

def promote_semester_master(sem_date, current_year, update_sem_mast_year):

    for d in sem_date:
        start_date = d['start_date']   # datetime.date
        end_date = d['end_date']

        if start_date.year != current_year:
            new_start_date = start_date.replace(year=current_year)
            new_end_date = end_date.replace(year=current_year)

            update_sem_mast_year(
                new_start_date,
                new_end_date,
                start_date,
                end_date
            )


def visualize_active_sem(rows, get_semester_date):
    active_sem_data = {}

    for r in rows:
        department = r['department']
        year = r['year']
        semester = r['semester']

        active = get_semester_date(semester, department, year)

        if department not in active_sem_data:
            active_sem_data[department] = []

        if active:
            active_sem_data[department].append(semester)

    return active_sem_data
