from fastapi import FastAPI

app = FastAPI()


employees = []


@app.get("/")
def hello():
    return {"message": "Hello! My First FastAPI Application"}


# CREATE
@app.post("/employees/{eid}/{name}/{salary}")
def add_employee(eid: int, name: str, salary: int):

    employee = {
        "id": eid,
        "name": name,
        "salary": salary
    }

    employees.append(employee)

    return {
        "message": "Employee Added Successfully",
        "employee": employee
    }


# READ ALL
@app.get("/employees")
def get_all_employees():
    return employees


# READ BY ID
@app.get("/employees/{eid}")
def get_employee(eid: int):

    for employee in employees:
        if employee["id"] == eid:
            return employee

    return {"message": "Employee Not Found"}


# UPDATE
@app.put("/employees/{eid}/{name}/{salary}")
def update_employee(eid: int, name: str, salary: int):

    for employee in employees:

        if employee["id"] == eid:

            employee["name"] = name
            employee["salary"] = salary

            return {
                "message": "Employee Updated Successfully",
                "employee": employee
            }

    return {"message": "Employee Not Found"}


# DELETE
@app.delete("/employees/{eid}")
def delete_employee(eid: int):

    for employee in employees:

        if employee["id"] == eid:

            employees.remove(employee)

            return {
                "message": "Employee Deleted Successfully"
            }

    return {"message": "Employee Not Found"}