
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import mysql.connector

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent


# MySQL Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="genaib2"
    )


# HOME - Open HTML Page
@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


# 1. POST - Add Employee
@app.post("/employees")
def add_employee(eid: int,name: str,age: int,salary: int,desig: str):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT eid FROM employee WHERE eid = %s",(eid,))
        
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Employee ID already exists")

        sql = """INSERT INTO employee(eid, name, age, salary, desig)VALUES (%s, %s, %s, %s, %s)"""
        values = (eid, name, age, salary, desig)
        cursor.execute(sql, values)
        connection.commit()
        return {"message": "Employee Added Successfully"}
    finally:
        cursor.close()
        connection.close()




# 2. GET - Display All Employees
@app.get("/employees")
def get_employees():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM employee ORDER BY eid")
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


# 3. GET - Search Employee by ID
@app.get("/employees/{eid}")
def get_employee_by_id(eid: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM employee WHERE eid = %s",(eid,))
        employee = cursor.fetchone()
        if employee is None:
            raise HTTPException(status_code=404,detail="Employee Not Found" )
        return employee
    finally:
        cursor.close()
        connection.close()

# 5. DELETE - Delete Employee by ID
@app.delete("/employees/{eid}")
def delete_employee(eid: int):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM employee WHERE eid = %s",(eid,) )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee Not Found" )
        connection.commit()
        return {"message": "Employee Deleted Successfully"}
    finally:
        cursor.close()
        connection.close()
        
# 6. DELETE - Delete All Employees
@app.delete("/employees")
def delete_all_employees():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM employee")
        deleted_count = cursor.rowcount
        connection.commit()
        return {
            "message": "All Employees Deleted Successfully",
            "deleted_count": deleted_count
        }

    finally:
        cursor.close()
        connection.close()

# 4. PUT - Update Employee
@app.put("/employees/{eid}")
def update_employee(
    eid: int,
    name: str,
    age: int,
    salary: int,
    desig: str
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT eid FROM employee WHERE eid = %s",
            (eid,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Employee Not Found"
            )

        sql = """
            UPDATE employee
            SET name = %s,
                age = %s,
                salary = %s,
                desig = %s
            WHERE eid = %s
        """

        values = (name, age, salary, desig, eid)

        cursor.execute(sql, values)
        connection.commit()

        return {"message": "Employee Updated Successfully"}

    finally:
        cursor.close()
        connection.close()












# 3. GET - Search Employee by ID
@app.get("/employees/{eid}")
def get_employee_by_id(eid: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM employee WHERE eid = %s",
            (eid,)
        )

        employee = cursor.fetchone()

        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Employee Not Found"
            )

        return employee

    finally:
        cursor.close()
        connection.close()


# 4. PUT - Update Employee
@app.put("/employees/{eid}")
def update_employee(
    eid: int,
    name: str,
    age: int,
    salary: int,
    desig: str
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT eid FROM employee WHERE eid = %s",
            (eid,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Employee Not Found"
            )

        sql = """
            UPDATE employee
            SET name = %s,
                age = %s,
                salary = %s,
                desig = %s
            WHERE eid = %s
        """

        values = (name, age, salary, desig, eid)

        cursor.execute(sql, values)
        connection.commit()

        return {"message": "Employee Updated Successfully"}

    finally:
        cursor.close()
        connection.close()


# 5. DELETE - Delete Employee by ID
@app.delete("/employees/{eid}")
def delete_employee(eid: int):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM employee WHERE eid = %s",
            (eid,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Employee Not Found"
            )

        connection.commit()

        return {"message": "Employee Deleted Successfully"}

    finally:
        cursor.close()
        connection.close()


# 6. DELETE - Delete All Employees
@app.delete("/employees")
def delete_all_employees():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM employee")
        deleted_count = cursor.rowcount
        connection.commit()

        return {
            "message": "All Employees Deleted Successfully",
            "deleted_count": deleted_count
        }

    finally:
        cursor.close()
        connection.close()
