# Migration Test 3 :: 가장 초기 설계 버전

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
![image](https://user-images.githubusercontent.com/22045163/83541494-ad253280-a534-11ea-9b09-a4ef56aa73f7.png)

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
![image](https://user-images.githubusercontent.com/22045163/83541634-dba30d80-a534-11ea-85ae-1d8795fcab7c.png)

3. 교수가 자신의 학과에서 가르치는 과목에 대하여 교수명과 과목명을 도출하여라.
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
![image](https://user-images.githubusercontent.com/22045163/83541734-00978080-a535-11ea-9b2d-00228e98ebf2.png)

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

![image](https://user-images.githubusercontent.com/22045163/83541819-1b69f500-a535-11ea-8d39-009d76acc7be.png)

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
![image](https://user-images.githubusercontent.com/22045163/83541879-2f155b80-a535-11ea-82a6-56c7ad6f0333.png)

### 결과
1. 0.001s
2. 0.009s
3. 0.076s
4. 0.005s
5. 0.001s
