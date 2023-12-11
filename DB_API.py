import sqlite3
from sqlite3.dbapi2 import Cursor, Connection


# 通过科室、医师、时间来查询是否有余额
def DB_query(conn:Connection, data:dict) -> list:
    department: str = data['department']
    time: str = data['time']
    level: str = data['level']
    id_num: str = data['id_num']
    query_list = (department, level, time, id_num,)
    cursor = conn.cursor()

    # 查询特定行
    sql = "SELECT * FROM mytable WHERE department = ? AND level = ? AND time = ? AND id = ?"
    cursor.execute(sql, query_list)
    rows = cursor.fetchall()
    
    return rows

# 通过科室、医师、时间来查询是否有余额
def DB_queryDLTCount(conn:Connection, data:dict) -> int:
    department: str = data['department']
    time: str = data['time']
    level: str = data['level']
    query_list = (department, level, time,)
    cursor = conn.cursor()

    # 查询特定行
    sql = "SELECT COUNT(*) FROM mytable WHERE department = ? AND level = ? AND time = ?"
    cursor.execute(sql, query_list)
    rows = cursor.fetchall()
    
    return rows[0][0]

def DB_queryID(conn:Connection, id_num:str) -> list:
    query_list = (id_num,)
    cursor = conn.cursor()

    sql = "SELECT * FROM mytable WHERE id = ?"
    cursor.execute(sql, query_list)
    rows = cursor.fetchall()

    return rows

def DB_queryIDAtSameTime(conn:Connection, data:dict) -> list:
    time = data['time']
    id_num = data['id_num']
    query_list = (id_num, time)
    cursor = conn.cursor()

    sql = "SELECT * FROM mytable WHERE id = ? AND time = ?"
    cursor.execute(sql, query_list)
    rows = cursor.fetchall()

    return rows

def DB_insert(conn:Connection, data:dict) -> None:
    department: str = data['department']
    time: str = data['time']
    level: str = data['level']
    id_num: str = data['id_num']
    query_list = (department, level, time, id_num,)
    cursor = conn.cursor()

    sql = "INSERT INTO mytable (department, level, time, id) VALUES (?, ?, ?, ?)"
    cursor.execute(sql, query_list)
    conn.commit()

def DB_delete(conn:Connection, id_num:str) -> None:
    query_list = (id_num,)
    cursor = conn.cursor()

    sql = "DELETE FROM mytable WHERE id = ?"
    cursor.execute(sql, query_list)
    conn.commit()

# if __name__ == "__main__":

#     data = {
#         'department': '1',
#         'level': '3',
#         'time': '2023-07-19',
#         'id_num': '450881199910235675'
#     }

#     conn = sqlite3.connect('mydatabase.db')  
#     # DB_insert(conn, data)
#     DB_delete(conn, '450881199910235675')
#     rows = DB_query(conn, data)
#     # print(row)
#     for x in rows:
#         print(x)

#     print(DB_queryDLTCount(conn, data))