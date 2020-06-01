import cx_Oracle
import json
from pprint import pprint
import pymongo
from bson.objectid import ObjectId

connection = pymongo.MongoClient("127.0.0.1", 27017)

#한글 지원 방법
import os
os.putenv('NLS_LANG', '.UTF8')

oconnection = cx_Oracle.connect('mongo','mongo','localhost:1521')

cursor = oconnection.cursor()

db = connection.DATABASE

instructordb = db['INSTRUCTOR']
studentdb = db['STUDENT']
takesdb = db['TAKES']
sectiondb = db['SECTION']
teachesdb = db['TEACHES']

# collection 초기화
instructordb.delete_many({})
studentdb.delete_many({})
takesdb.delete_many({})
sectiondb.delete_many({})
teachesdb.delete_many({})

# embedding 하기 위한 dictionary
department = {

}

classroom = {

}

ctmp = {

}

time_slot = {

}

course = {

}

# collectio 저장 배열
instructor = []
student = []
section = []
takes = []
teaches = []

cursor.execute("""
    select * from DEPARTMENT
""")

for token in cursor:
    dept_name = token[0]
    building = token[1]
    budget = float(token[2])
    # dictionry에 key(dept_name) - value(dept_name, building, budget) 쌍으로 저장
    department[dept_name] = {
        'dept_name': dept_name,
        'building' : building,
        'budget': budget
    }

cursor.execute("""
    select * from CLASSROOM
""")

for token in cursor:
    building = token[0]
    roomnumber = token[1]
    capacity = int(token[2])
    # dictionry에 key(buliding) - key(roomnumber) - value(dept_name, building, budget) 쌍으로 저장

    if building in classroom.keys():
        classroom[building][roomnumber] = {
            'building': building,
            'room_number' : roomnumber,
            'capacity': capacity
        }
    else:
        classroom[building] = dict()
        classroom[building][roomnumber] = {
            'building': building,
            'room_number' : roomnumber,
            'capacity': capacity
        }

cursor.execute("""
    select * from TIME_SLOT
""")

for token in cursor:
    time_slot_id = token[0]
    day = token[1]
    start_hour = token[2]
    start_min = token[3]
    end_hour = token[4]
    end_min = token[5]
    # dictionry에 key(time_slot_id) - value() 쌍으로 저장
    time_slot[time_slot_id] = {
        'day': day,
        'start_hour': token[2],
        'start_min': token[3],
        'end_hour': token[4],
        'end_min': token[5]
    }

cursor.execute("""
    select * from INSTRUCTOR
""")

for token in cursor:
    ID = token[0]
    Name = token[1]
    dept_name = token[2]
    salary = float(token[3])
    Json = {
        'ID' : ID,
        'name': Name,
        'salary': int(salary),
        'department': department[dept_name],
        'advisor': ''
    }
    instructor.append(Json)

cursor.execute("""
    select * from STUDENT
""")

for token in cursor:
    ID = token[0]
    Name = token[1]
    dept_name = token[2]
    tot_credit = int(token[3])
    Json = {
        'ID' : ID,
        'name': Name,
        'tot_credit': tot_credit,
        'department': department[dept_name],
        'advisor': ''
    }
    student.append(Json)

cursor.execute("""
    select * from COURSE
""")

for token in cursor:
    course_id = token[0]
    title = token[1]
    dept_name = token[2]
    credits = int(token[3])
    Json = {
        'course_id' : course_id,
        'title': title,
        'credits': credits,
        'department': department[dept_name],
        'prereq': [],
    }
    course[course_id] = Json

cursor.execute("""
    select * from PREREQ
""")

for token in cursor:
    course_id = token[0]
    prereq_id = token[1]

    Json = course[prereq_id].copy()
    Json.pop('prereq')
    course[course_id]['prereq'].append(Json)


cursor.execute("""
    select * from SECTION
""")

for token in cursor:
    course_id = token[0]
    section_id = token[1]
    semester = token[2]
    year = int(token[3])
    building = token[4]
    roomnumber = token[5]
    time_slot_id = token[6]
    Json = {
        'course' : course[course_id],
        'section_id': section_id,
        'semester': semester,
        'year': year,
        'time_slot': '',
        'classroom': classroom[building][roomnumber]
    }
    if time_slot_id in time_slot.keys():
        Json['time_slot'] = time_slot[time_slot_id]
    section.append(Json)


print("----------------------on--------------------")

# collection에 link 제외한 embed 저장
instructordb.insert_many(instructor)
print("----------------------on--------------------")

studentdb.insert_many(student)
print("----------------------on--------------------")

sectiondb.insert_many(section)

print("----------------------on--------------------")

# link 연결
cursor.execute("""
    select * from ADVISOR
""")

for token in cursor:
    s_id = token[0]
    i_id = token[1]

    s_obi = studentdb.find_one({'ID': s_id})['_id']
    i_obi = instructordb.find_one({'ID': i_id})['_id']

    instructordb.update_one({'ID' : i_id}, {'$set': {'advisor' : s_obi}})
    studentdb.update_one({'ID': s_id}, {'$set': {'advisor': i_obi}})

cursor.execute("""
    select * from TAKES
""")

for token in cursor:
    ID = token[0]
    course_id = token[1]
    sec_id = token[2]
    seme = token[3]
    year = int(token[4])
    grade = token[5]

    s_obi = studentdb.find_one({'ID': ID})['_id']

    sec_obi = sectiondb.find_one({'course': course[course_id], 'section_id': sec_id, 'semester': seme, 'year': year})['_id']

    Json = {
        'section_id': sec_obi,
        'student_id': s_obi,
        'grade': grade 
    }
    takesdb.insert_one(Json)

cursor.execute("""
    select * from TEACHES
""")

for token in cursor:
    i_id = token[0]
    course_id = token[1]
    sec_id = token[2]
    semester = token[3]
    year = int(token[4])
    
    i_obi = instructordb.find_one({'ID': i_id})['_id']
    sec_obi = sectiondb.find_one({'course': course[course_id], 'section_id': sec_id, 'semester': semester, 'year': year})['_id']

    Json = {
        'instructor_id': i_obi,
        'section_id': sec_obi
    }

    teaches.append(Json)

teachesdb.insert_many(teaches)
