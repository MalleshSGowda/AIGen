from pathlib import Path

import mysql.connector
from mysql.connector import Error, IntegrityError
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Employee Management API")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost", user="root", password="root", database="genAIB2"
        )
    except Error as exc:
        print("Database connection error:", exc)
        raise HTTPException(status_code=503, detail="Cannot connect to MySQL. Check database settings and server.") from exc


class EmployeeCreate(BaseModel):
    eid: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=18, le=100)
    salary: int = Field(ge=0)
    desig: str = Field(min_length=1, max_length=50)


class EmployeeUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=18, le=100)
    salary: int = Field(ge=0)
    desig: str = Field(min_length=1, max_length=50)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/employees")
def get_all_employees():
    con = get_connection()
    cursor = None
    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT eid, name, age, salary, desig FROM Employee ORDER BY eid")
        return cursor.fetchall()
    except Error as exc:
        print("Database error:", exc)
        raise HTTPException(status_code=500, detail="Could not load employees") from exc
    finally:
        if cursor is not None:
            cursor.close()
        con.close()


@app.get("/employees/{id}")
def get_employee_by_id(id: int):
    con = get_connection()
    cursor = None
    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT eid, name, age, salary, desig FROM Employee WHERE eid = %s", (id,))
        employee = cursor.fetchone()
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except Error as exc:
        print("Database error:", exc)
        raise HTTPException(status_code=500, detail="Could not find employee") from exc
    finally:
        if cursor is not None:
            cursor.close()
        con.close()


@app.post("/employees", status_code=201)
def add_employee(employee: EmployeeCreate):
    con = get_connection()
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO Employee(eid, name, age, salary, desig) VALUES (%s, %s, %s, %s, %s)",
            (employee.eid, employee.name.strip(), employee.age, employee.salary, employee.desig.strip()),
        )
        con.commit()
        return {"message": "Employee added successfully"}
    except IntegrityError as exc:
        con.rollback()
        if exc.errno == 1062:
            raise HTTPException(status_code=409, detail="Employee ID already exists") from exc
        print("Database integrity error:", exc)
        raise HTTPException(status_code=400, detail="Employee could not be added") from exc
    except Error as exc:
        con.rollback()
        print("Database error:", exc)
        raise HTTPException(status_code=500, detail="Could not add employee") from exc
    finally:
        if cursor is not None:
            cursor.close()
        con.close()


@app.put("/employees/{id}")
def update_employee(id: int, employee: EmployeeUpdate):
    con = get_connection()
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("SELECT eid FROM Employee WHERE eid = %s", (id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        cursor.execute(
            "UPDATE Employee SET name = %s, age = %s, salary = %s, desig = %s WHERE eid = %s",
            (employee.name.strip(), employee.age, employee.salary, employee.desig.strip(), id),
        )
        con.commit()
        return {"message": "Employee updated successfully"}
    except Error as exc:
        con.rollback()
        print("Database error:", exc)
        raise HTTPException(status_code=500, detail="Could not update employee") from exc
    finally:
        if cursor is not None:
            cursor.close()
        con.close()


@app.delete("/employees/{id}")
def delete_employee(id: int):
    con = get_connection()
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM Employee WHERE eid = %s", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee not found")
        con.commit()
        return {"message": "Employee deleted successfully"}
    except Error as exc:
        con.rollback()
        print("Database error:", exc)
        raise HTTPException(status_code=500, detail="Could not delete employee") from exc
    finally:
        if cursor is not None:
            cursor.close()
        con.close()


@app.delete("/employees")
def delete_all_employees():
    con = get_connection()
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM Employee")
        count = cursor.rowcount
        con.commit()
        return {"message": f"Deleted {count} employee(s) successfully"}
    except Error as exc:
        con.rollback()
        print("Database error:", exc)
        raise HTTPException(status_code=500, detail="Could not delete employees") from exc
    finally:
        if cursor is not None:
            cursor.close()
        con.close()
