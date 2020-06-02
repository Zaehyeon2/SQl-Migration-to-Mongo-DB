# Migration Test 1 :: BEST version

## MongoDB Collections
![image](https://user-images.githubusercontent.com/22045163/83544120-65a0a580-a538-11ea-9aff-9432eb0eb489.png)
![image](https://user-images.githubusercontent.com/22045163/83544242-8ff26300-a538-11ea-9956-e4d17fdae66e.png)

## Query Performance

1. Comp.Sci. 학과의 salary가 80000 이상인 instructor의 name을 찾아라. (0.001 sec.)

```SQL
SELECT name
FROM instructor
WHERE dept_name = 'Comp. Sci.' and salary > 80000
```

```js
db.INSTRUCTOR.find({ 'department.dept_name': 'Comp. Sci.', 'salary': { '$gt': 80000 }}, { '_id': 0, 'name': 1})
```

![image](https://user-images.githubusercontent.com/22045163/83544344-b4e6d600-a538-11ea-99e8-045260027d41.png)

2. 교수가 가르치는 과목 id를 도출하여라. (0.009 sec.)

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
            'course_id': '$section.course.course_id'
        }
  },
  { "$unwind": "$course_id" },
  { $sort : { 'name': 1, 'course_id': 1 }},
]);
```

+ aggregation framework 사용, INSTRUCTOR & SECTION 으로만 돌림
+ 편의상 sort 사용

![image](https://user-images.githubusercontent.com/22045163/83544513-f7101780-a538-11ea-864a-caaa47f8802a.png)


3. 교수가 자신의 학과에서 가르치는 과목에 대하여 교수명과 과목명을 도출하여라. (0.019 sec.)
** natural join은 그 의미 및 결과가 2번과 다름. (총 84개 row, 공통 필드 ID, course_id, dept_name)

```SQL
SELECT name, title
FROM instructor NATURAL JOIN teaches NATURAL JOIN course
```

```js
db.INSTRUCTOR.aggregate([
   { "$unwind": "$section_id" },
   {
     $lookup:
       {
         from: "SECTION",
         let: { section_id: "$section_id", dept_name: "$department.dept_name" },
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
         as: "course"
       }
  },
  {
      $project:
        {
            _id: 0,
            'name': 1,
            'title': '$course.course.title'
        }
  },
  { "$unwind": "$title" },
  { $sort : { 'name': 1, 'title': 1 }},
]);
```

+ aggregation framework 사용, INSTRUCTOR & SECTION 으로만 돌림
+ $lookup 방법 중 여러 field 참조 가능한 방법 적용
+ 편의상 sort 사용

![image](https://user-images.githubusercontent.com/22045163/83544865-83223f00-a539-11ea-841e-1cc21e71ec28.png)

4. 2009년 가을, 2010년 봄에 열린 과목들 중 공통되는 과목을 도출하여라. (0.005 sec.)

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
        if (obj1.course.course_id == obj2.course.course_id) print(obj1.course.course_id)
    });
});
```

+ 원래의 문제로는 답이 나오지 않으므로, 2006년 가을학기와 2009년 가을학기의 공통 과목을 조회하였음

![image](https://user-images.githubusercontent.com/22045163/83545270-f1ff9800-a539-11ea-93cf-bd4a335ed9a5.png)

5. 학과 별 교수들 연봉의 평균을 도출하여라. (0.001 sec.)

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

![image](https://user-images.githubusercontent.com/22045163/83545367-10659380-a53a-11ea-8ee3-9b9d62c028e3.png)


### 결과
1. 0.001s
2. 0.009s
3. 0.019s
4. 0.005s
5. 0.001s
