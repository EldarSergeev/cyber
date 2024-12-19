
from db_tools import *    
host = '127.0.0.1'
print("____1____")
mydb = init()
print("____2____")
create_database(mydb, "mysql")
print("____3____")
dbs = show_databases(mydb)    
print(dbs)
print("____4____")
mydb_db = init_with_db("mysql")
print("____5____")
tables = show_tables(mydb_db)
print(tables)
print("____5____")
create_table(mydb_db, "data_user",
                 "(id INT, ip VARCHAR(255), port INT, Isblacklisted VARCHAR(255),Connections_per_day INT )")
# TODO: create other tables HERE! Noah :)
print("____6____")
delete_table(mydb_db, "component")
tables = show_tables(mydb_db)
print(tables)
print("____7____")
print(get_all_rows(mydb_db, "data_user"))
print("____8____")
insert_row(mydb_db, "data_user",
                 "(id, ip, port ,Isblacklisted ,Connections_per_day )",
                 "(%s, %s, %s, %s, %s )",
                 (1, "127.0.0.1", 9000 ,"True" ,1 ))
insert_row(mydb_db, "data_user",
                 "(id, ip, port ,Isblacklisted ,Connections_per_day )",
                 "(%s, %s, %s, %s, %s )",
                 (7, "127.0.78,09", 2000 ,"False" ,2 ))
print("____9____")
print(get_all_rows(mydb_db, "data_user"))
print("___________10_________")
#delete_row(mydb_db, "users", "id", "1")
print("____11____")
print(get_all_rows(mydb_db, "data_user"))
   
print("____12______")
print(get_rows_from_table_with_value(mydb_db, "data_user", "id", "7"))