# SQl-Migration-to-Mongo-DB
Hanyang Univ. ERICA 데이터베이스응용 PBL2

Sql Migration to NoSql(MongoDB)

## Specification
|Name| Version |
|--|--|
| Python3 | 3.6.8 |
| pip | 20.1.1 |
| cx-Oracle  | 7.3.0 |
| pymongo  | 3.10.1 |
| bson  | 0.5.10 |
| pprint  |  0.1 |
| Oracle Database  | 11g Express Edition |

    pip3 install cx-Oracle pymongo bson pprint

## using_insertfile.py
Migration using largeRelationsInsertFile.sql

    
    // using_insertfile.py
    7| connection = pymongo.MongoClient(hostip(default="127.0.0.1"), port(default=27017))
    //
    
    $ python3 using_insertfile.py


## using_oracledb.py
Migration using Oracle Database

    $ sqlplus username(mongo)/password(mongo)
    
    SQL> c@DDL+drop.sql
    SQL> c@largeRelationsInsertFile.sql
    SQL> exit
    Disconnected from Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production
    
    // using_oracledb.py
    7 | connection = pymongo.MongoClient(host_ip(default="127.0.0.1"), port(default=27017))
    13| oconnection = cx_Oracle.connect(username(defalut='mongo'), password(defalut='mongo'), host(defalut='localhost:1521'))
    //
    
    $ python3 using_oracledb.py
