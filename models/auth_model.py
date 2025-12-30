from database.db_connection import get_db_connection
    
def user_authentication(table, id, user_id, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = f"SELECT * FROM {table} WHERE {id} = %s AND password = %s"
        cursor.execute(query,(user_id, password))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

def forget_password(user_id, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        role_map = {
            "students":  "register_no",
            "teachers":  "teacher_id",
            "incharge":  "incharge_id",
            "hod":       "hod_id",
            "admin":     "admin_id"
        }

        for table, column in role_map.items():
            cursor.execute(
                f"SELECT 1 FROM {table} WHERE {column} = %s",
                (user_id,)
            )

            if cursor.fetchone():
                cursor.execute(
                    f"UPDATE {table} SET password = %s WHERE {column} = %s",
                    (new_password, user_id)
                )
                conn.commit()
                return True 
            
        return False  
    
    finally:
        cursor.close()
        conn.close()
