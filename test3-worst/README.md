# Migration Test 3 :: WORST VERSION

## MongoDB Collections

<img width="1155" alt="mongodb" src="https://user-images.githubusercontent.com/22045163/83502293-4edc5d80-a4fc-11ea-939f-f9e54dc6f2ea.png">

![image](https://user-images.githubusercontent.com/22045163/83501991-eb523000-a4fb-11ea-8657-167920ab503b.png)

## Query Performance

1. Comp.Sci. 학과의 salary가 80000 이상인 instructor의 name을 찾아라.
```SQL
SELECT name
FROM instructor
WHERE dept_name = 'Comp. Sci.' and salary > 80000
```
```js
db.INSTRUCTOR.find({ 'department.dept_name': 'Comp. Sci.', 'salary': { '$gt': 80000 }}, { '_id': 0, 'name': 1})
```
![image](https://user-images.githubusercontent.com/22045163/83502451-8f3bdb80-a4fc-11ea-881c-d4ffa18e53ec.png)

2. 교수가 가르치는 과목 id를 도출하여라.
```SQL
SELECT name, course_id
FROM instructor, teaches
WHERE instructor.ID = teaches.ID
```
```js
db.INSTRUCTOR.aggregate([
   { "$unwind": "$section_id" },
   {
     $lookup:
       {
         from: "SECTION",
         localField: "section_id",
         foreignField: "_id",
         as: "section"
       }
    },
    {
      $project:
        {
          _id: 0,
          'name': 1,
          'course_id': '$section.course_id'
        }
    },
    { "$unwind": "$course_id" },
    { $sort : { 'name': 1, 'course_id': 1 }},
]);
```
![image](https://user-images.githubusercontent.com/22045163/83503073-84357b00-a4fd-11ea-8df9-e1c68254241c.png)

3. 교수가 가르치는 과목명을 도출하여라.
```SQL
SELECT name, title
FROM instructor NATURAL JOIN teaches NATURAL JOIN course
```
```js
db.INSTRUCTOR.aggregate([
    { $match: {"section_id": { $ne: null }} },
    { "$unwind": "$section_id" },
    {
        $lookup:
        {
            from: "SECTION",
            localField: "section_id",
            foreignField: "_id",
            as: "section"
        }
    },
    { "$unwind": "$section" },
    {
        $lookup:
        {
         from: "COURSE",
         let: { course_id: "$section.course_id", dept_name: "$department.dept_name" },
         pipeline: [
              { $match:
                 { $expr:
                    { $and:
                       [
                         { $eq: [ "$course_id",  "$$course_id" ] },
                         { $eq: [ "$department.dept_name",  "$$dept_name" ] },
                       ]
                    }
                 }
              },
         ],
         as: "course"
       }
    },
    {
      $project:
        {
            _id: 0,
            'name': 1,
            'title': '$course.title',
        },
    },
    { "$unwind": "$title" },
    { $sort : { 'name': 1, 'title': 1 }},
]);
```
![image](https://user-images.githubusercontent.com/22045163/83507819-09239300-a504-11ea-83b9-6c671c495622.png)

4. 2009년 가을, 2010년 봄에 열린 과목들 중 공통되는 과목을 도출하여라.
```SQL
(
    SELECT course_id
    FROM section 
    WHERE semester = 'Fall' and year = 2009
)
INTERSECT
(
    SELECT course_id
    FROM section
    WHERE semester = 'Spring' and year = 2010
)
```
```js
db.SECTION.find({'semester': 'Fall', 'year' : 2006}).forEach(function(obj1){
    db.SECTION.find({'semester': 'Fall', 'year': 2009}).forEach(function(obj2){
        if (obj1.course_id == obj2.course_id) print(obj1.course_id)
    });
});
```
예제는 결과값이 없어서, 다른 값으로 돌림
![image](https://user-images.githubusercontent.com/22045163/83508101-6b7c9380-a504-11ea-98f6-21056d0e3951.png)

5. 학과 별 교수들 연봉의 평균을 도출하여라.
```SQL
SELECT dept_name, avg(salary)
FROM instructor
GROUP BY dept_name
```
```js
db.INSTRUCTOR.aggregate([
    {'$group': { _id : '$department.dept_name', avg : { $avg : '$salary' } }}
]);
```
![image](https://user-images.githubusercontent.com/22045163/83508191-8b13bc00-a504-11ea-897b-76991101ca32.png)

### 결과
1. 0.001s
2. 0.009s
3. 0.071s
4. 0.005s
5. 0.001s
