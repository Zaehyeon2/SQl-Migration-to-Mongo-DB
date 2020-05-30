import json
from pprint import pprint
import pymongo
from bson.objectid import ObjectId

connection = pymongo.MongoClient("127.0.0.1", 27017)

# embedding 하기 위한 dictionary
department = {

}

classroom = {

}

ctmp = {

}

time_slot = {

}

# collectio 저장 배열
instructor = []
student = []
section = []
course = []
takes = []

# .sql파일 불러오기
with open("largeRelationsInsertFile.sql", "r") as f:
    lines = f.readlines()
    for line in lines:
        # 예외 처리 (" ')")
        line = line.replace(" ')", "')")
        line = line.replace("values", "values ")
        # insert, into, table, values, value로 나누기
        token = line.split(" ", 4)
        # value 리스트화
        # token[2] == table name, token[4][] == value
        if(token[0] == 'insert'):
            token[4] = token[4][1:-3]
            token[4] = token[4].replace("'", '')
            token[4] = token[4].split(", ")

        if(token[0] == "insert" and token[2] == 'department'):
            dept_name = token[4][0]
            building = token[4][1]
            budget = float(token[4][2])
            # dictionry에 key(dept_name) - value(dept_name, building, budget) 쌍으로 저장
            department[dept_name] = {
                'dept_name': dept_name,
                'building' : building,
                'budget': budget
            }

        if(token[0] == "insert" and token[2] == 'classroom'):
            building = token[4][0]
            roomnumber = token[4][1]
            capacity = int(token[4][2])
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
        
        if(token[0] == "insert" and token[2] == 'time_slot'):
            time_slot_id = token[4][0]
            day = token[4][1]
            start_hour = token[4][2]
            start_min = token[4][3]
            end_hour = token[4][4]
            end_min = token[4][5]
            # dictionry에 key(time_slot_id) - value() 쌍으로 저장
            time_slot[time_slot_id] = {
                'day': day,
                'start_hour': token[4][2],
                'start_min': token[4][3],
                'end_hour': token[4][4],
                'end_min': token[4][5]
            }

        if(token[0] == 'insert' and token[2] == 'instructor'):
            ID = token[4][0]
            Name = token[4][1]
            dept_name = token[4][2]
            salary = float(token[4][3])
            Json = {
                'ID' : ID,
                'name': Name,
                'salary': int(salary),
                'department': department[dept_name],
                'section_id': [],
                'advisor': ''
            }
            instructor.append(Json)
            
        if(token[0] == 'insert' and token[2] == 'student'):
            ID = token[4][0]
            Name = token[4][1]
            dept_name = token[4][2]
            tot_credit = int(token[4][3])
            Json = {
                'ID' : ID,
                'name': Name,
                'tot_credit': tot_credit,
                'department': department[dept_name],
                'advisor': ''
            }
            student.append(Json)

        if(token[0] == 'insert' and token[2] == 'section'):
            course_id = token[4][0]
            section_id = token[4][1]
            semester = token[4][2]
            year = int(token[4][3])
            building = token[4][4]
            roomnumber = token[4][5]
            time_slot_id = token[4][6]
            Json = {
                'course_id' : course_id,
                'section_id': section_id,
                'semester': semester,
                'year': year,
                'time_slot': '',
                'classroom': classroom[building][roomnumber]
            }
            if time_slot_id in time_slot.keys():
                Json['time_slot'] = time_slot[time_slot_id]
            section.append(Json)

        if(token[0] == 'insert' and token[2] == 'course'):
            course_id = token[4][0]
            title = token[4][1]
            dept_name = token[4][2]
            credits = int(token[4][3])
            Json = {
                'course_id' : course_id,
                'title': title,
                'credits': credits,
                'department': department[dept_name],
                'prereq_id': [],
            }
            course.append(Json)

db = connection.DATABASE

instructordb = db['INSTRUCTOR']
studentdb = db['STUDENT']
takesdb = db['TAKES']
sectiondb = db['SECTION']
coursedb = db['COURSE']

# collection 초기화
instructordb.delete_many({})
studentdb.delete_many({})
takesdb.delete_many({})
sectiondb.delete_many({})
coursedb.delete_many({})

# collection에 link 제외한 embed 저장
instructordb.insert_many(instructor)
studentdb.insert_many(student)
sectiondb.insert_many(section)
coursedb.insert_many(course)

# link 연결
with open("largeRelationsInsertFile.sql", "r") as f:
    lines = f.readlines()
    for line in lines:
        # 예외 처리 (" ')")
        line = line.replace(" ')", "')")
        line = line.replace("values", "values ")
        # insert, into, table, values, value로 나누기
        token = line.split(" ", 4)
        # value 리스트화
        # token[2] == table name, token[4][] == value
        if(token[0] == 'insert'):
            token[4] = token[4][1:-3]
            token[4] = token[4].replace("'", '')
            token[4] = token[4].split(", ")

        if(token[0] == "insert" and token[2] == 'advisor'):
            s_id = token[4][0]
            i_id = token[4][1]

            s_obi = studentdb.find_one({'ID': s_id})['_id']
            i_obi = instructordb.find_one({'ID': i_id})['_id']

            instructordb.update_one({'ID' : i_id}, {'$set': {'advisor' : s_obi}})
            studentdb.update_one({'ID': s_id}, {'$set': {'advisor': i_obi}})

        if(token[0] == 'insert' and token[2] == 'section'):
            course_id = token[4][0]
            section_id = token[4][1]
            semester = token[4][2]
            year = int(token[4][3])
            building = token[4][4]
            roomnumber = token[4][5]
            time_slot_id = token[4][6]

            c_obi = coursedb.find_one({'course_id' : course_id})['_id']
            sectiondb.update_many({'course_id': course_id}, {'$set': {'course_id' : c_obi}})

        if(token[0] == 'insert' and token[2] == 'takes'):
            ID = token[4][0]
            course_id = token[4][1]
            sec_id = token[4][2]
            seme = token[4][3]
            year = int(token[4][4])
            grade = token[4][5]

            c_obi = coursedb.find_one({'course_id' : course_id})['_id']
            s_obi = studentdb.find_one({'ID': ID})['_id']

            sec_obi = sectiondb.find_one({'course_id': c_obi, 'section_id': sec_id, 'semester': seme, 'year': year})['_id']

            Json = {
                'section_id': sec_obi,
                'student_id': s_obi,
                'grade': grade 
            }
            takesdb.insert_one(Json)

        if(token[0] == 'insert' and token[2] == 'prereq'):
            course_id = token[4][0]
            prereq_id = token[4][1]

            c_obi = coursedb.find_one({'course_id' : course_id})['_id']
            p_obi = coursedb.find_one({'course_id' : prereq_id})['_id']

            coursedb.update_many({'course_id': course_id}, {'$push' : {'prereq_id': p_obi}})

        if(token[0] == 'insert' and token[2] == 'teaches'):
            i_id = token[4][0]
            course_id = token[4][1]
            sec_id = token[4][2]
            semester = token[4][3]
            year = int(token[4][4])
            
            c_obi = coursedb.find_one({'course_id' : course_id})['_id']

            sec_obi = sectiondb.find_one({'course_id': c_obi, 'section_id': sec_id, 'semester': semester, 'year': year})['_id']

            instructordb.update({'ID': i_id}, {'$push' : {'section_id': sec_obi}})
