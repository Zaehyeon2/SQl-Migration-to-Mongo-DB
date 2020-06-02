# Migration Test 2

## MongoDB Collections
![image](https://user-images.githubusercontent.com/22045163/83492543-657bb800-a4ee-11ea-8a03-58d67078f2fd.png)

TEACHES collection => section_id, instructor_id

## Query Performance

1. Comp.Sci. 학과의 salary가 80000 이상인 instructor의 name을 찾아라.
```SQL
SELECT name
FROM instructor
WHERE dept_name = 'Comp. Sci.' and salary > 80000
```
![image](https://user-images.githubusercontent.com/22045163/83492625-83491d00-a4ee-11ea-9075-d47a80a0d809.png)

2. 교수가 가르치는 과목 id를 도출하여라.
```SQL
SELECT name, course_id
FROM instructor, teaches
WHERE instructor.ID = teaches.ID
```
```js
db.TEACHES.aggregate([
   {
     $lookup:
       {
         from: "INSTRUCTOR",
         localField: "instructor_id",
         foreignField: "_id",
         as: "instructor"
       }
  },
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
            'name': 'instructor.name',
            'course_id': '$section.course.course_id'
        }
  },
  { "$unwind": "$course_id" },
  { $sort : { 'name': 1, 'course_id': 1 }},
]);
```

collection 3개를 참고하기 때문에, TEST1 대비 1.7배 정도 느리다.

![image](https://user-images.githubusercontent.com/22045163/83492713-a5db3600-a4ee-11ea-8cec-b20d85f80312.png)

3. 교수가 자신의 학과에서 가르치는 과목에 대하여 교수명과 과목명을 도출하여라.
```SQL
SELECT name, title
FROM instructor NATURAL JOIN teaches NATURAL JOIN course
```
```js
db.TEACHES.aggregate([
   {
     $lookup:
       {
         from: "INSTRUCTOR",
         localField: "instructor_id",
         foreignField: "_id",
         as: "instructor"
       }
  },
  { "$unwind": "$instructor" },
  {
    $lookup:
    {
         from: "SECTION",
         let: { section_id: "$section_id", dept_name: "$instructor.department.dept_name" },
         pipeline: [
              { $match:
                 { $expr:
                    { $and:
                       [
                         { $eq: [ "$_id",  "$$section_id" ] },
                         { $eq: [ "$course.department.dept_name",  "$$dept_name" ] },
                       ]
                    }
                 }
              },
         ],
         as: "section"
       }
    },
  {
      $project:
        {
            _id: 0,
            'name': '$instructor.name',
            'title': '$section.course.title',
        },
        
  },
  { "$unwind": "$name" },
  { "$unwind": "$title" },
  { $sort : { 'name': 1, 'title': 1 }},
]);
```

마찬가지로, TEST1보다 1.4배 정도 느리다.

![image](https://user-images.githubusercontent.com/22045163/83509168-fd38d080-a505-11ea-9eea-0b1743229234.png)

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

여전히... forEach... 방법 없나..

![image](https://user-images.githubusercontent.com/22045163/83493310-8ee91380-a4ef-11ea-979e-ece3bb6a9169.png)

5. 학과 별 교수들 연봉의 평균을 도출하여라.
```SQL
SELECT dept_name, avg(salary)
FROM instructor
GROUP BY dept_name
```
![image](https://user-images.githubusercontent.com/22045163/83493371-a6280100-a4ef-11ea-976f-96eca7a036b8.png)

### 결과
1. 0.001s
2. 0.016s
3. 0.027s
4. 0.005s
5. 0.001s
