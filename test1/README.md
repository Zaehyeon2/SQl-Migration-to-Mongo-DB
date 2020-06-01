# Migration Test 1

## MongoDB Collections
![image](https://user-images.githubusercontent.com/22045163/83442731-9d014a80-a483-11ea-9723-668caba5d8bf.png)

## Query Performance

1. Comp.Sci. 학과의 salary가 80000 이상인 instructor의 name을 찾아라.
```SQL
SELECT name
FROM instructor
WHERE dept_name = 'Comp. Sci.' and salary > 80000
```
![image](https://user-images.githubusercontent.com/22045163/83442844-cf12ac80-a483-11ea-842d-5709dd2275f8.png)

2. 교수가 가르치는 과목 id를 도출하여라.
```SQL
SELECT name, course_id
FROM instructor, teaches
WHERE instructor.ID = teaches.ID
```
기존 DATABASE
![image](https://user-images.githubusercontent.com/22045163/83442969-f6697980-a483-11ea-94da-1020e91253dd.png)
바꾼 TEST1 - aggregation framework 사용, INSTRUCTOR & SECTION 으로만 돌림
![image](https://user-images.githubusercontent.com/22045163/83443064-19942900-a484-11ea-84fd-81743a6bf030.png)

3. 교수가 가르치는 과목명을 도출하여라. <= natural join은 그 결과가 2번과 다름. (총 84개 row, 공통 필드 ID, course_id, dept_name)
```SQL
SELECT name, title
FROM instructor NATURAL JOIN teaches NATURAL JOIN course
```
(마찬가지로 forEach, collection 3개 참조보다 좋은 성능)
![image](https://user-images.githubusercontent.com/22045163/83443314-7db6ed00-a484-11ea-86a1-3eda7eb7b71d.png)

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
그냥 forEach를 돌려봅니다.
![image](https://user-images.githubusercontent.com/22045163/83443528-dab2a300-a484-11ea-8fb9-46744c3d63ed.png)

5. 학과 별 교수들 연봉의 평균을 도출하여라.
```SQL
SELECT dept_name, avg(salary)
FROM instructor
GROUP BY dept_name
```
아유 쉬워라
![image](https://user-images.githubusercontent.com/22045163/83443695-25341f80-a485-11ea-965b-910c012e8edb.png)
