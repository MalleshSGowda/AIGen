from fastapi import FastAPI

app = FastAPI()


# Employee List
employees = [
    {
        "id": 101,
        "name": "Thanesh",
        "age": 30,
        "salary": 50000,
        "designation": "Developer"
    },
    {
        "id": 102,
        "name": "Ramesh",
        "age": 28,
        "salary": 40000,
        "designation": "Tester"
    }
    
]


# 1. HOME API
@app.get("/")
def home():
    return {
        "message": "Welcome to Employee Management API"
    }


# 2. GET ALL EMPLOYEES
@app.get("/employees")
def get_all_employees():
    return employees


# 3. GET EMPLOYEE BY ID
@app.get("/employees/{id}")
def get_employee_by_id(id: int):
    for employee in employees:
        if employee["id"] == id:
            return employee
    return {
        "message": "Employee not found"
    }

# 4. CREATE EMPLOYEE
@app.post("/employees")
def add_employee(   id: int,name: str, age: int,salary: int,designation: str ):

    employee = {
        "id": id,
        "name": name,
        "age": age,
        "salary": salary,
        "designation": designation
    }

    employees.append(employee)

    return {
        "message": "Employee added successfully",
        "employee": employee
    }

# 5. UPDATE EMPLOYEE
@app.put("/employees/{id}")
def update_employee(
    id: int,
    name: str,
    age: int,
    salary: int,
    designation: str
):

    for employee in employees:

        if employee["id"] == id:

            employee["name"] = name
            employee["age"] = age
            employee["salary"] = salary
            employee["designation"] = designation

            return {
                "message": "Employee updated successfully",
                "employee": employee
            }

    return {
        "message": "Employee not found"
    }

# 6. DELETE EMPLOYEE
@app.delete("/employees/{id}")
def delete_employee(id: int):
    for employee in employees:
        if employee["id"] == id:
            employees.remove(employee)
            return {
                "message": "Employee deleted successfully"
            }
    return {
        "message": "Employee not found"
    }
    
# 7. GET EMPLOYEES BY DESIGNATION
@app.get("/employees/designation/{designation}")
def get_by_designation(designation: str):

    result = []

    for employee in employees:
        if employee["designation"].lower() == designation.lower():
            result.append(employee)

    if len(result) == 0:
        return {
            "message": "No employees found"
        }

    return result


# 8. GET EMPLOYEES BY AGE
@app.get("/employees/age/{age}")
def get_by_age(age: int):

    result = []

    for employee in employees:
        if employee["age"] == age:
            result.append(employee)

    return result


# 9. GET EMPLOYEES WITH SALARY GREATER THAN GIVEN AMOUNT
@app.get("/employees/salary/greater/{amount}")
def get_salary_greater(amount: int):

    result = []

    for employee in employees:
        if employee["salary"] > amount:
            result.append(employee)

    return result


# 10. GET EMPLOYEES WITH SALARY LESS THAN GIVEN AMOUNT
@app.get("/employees/salary/less/{amount}")
def get_salary_less(amount: int):

    result = []

    for employee in employees:
        if employee["salary"] < amount:
            result.append(employee)

    return result


# 11. GET TOTAL NUMBER OF EMPLOYEES
@app.get("/employees-count")
def employee_count():

    return {
        "total_employees": len(employees)
    }


# 12. GET TOTAL SALARY
@app.get("/employees-total-salary")
def total_salary():

    total = 0

    for employee in employees:
        total = total + employee["salary"]

    return {
        "total_salary": total
    }


# 13. GET HIGHEST SALARY EMPLOYEE
@app.get("/employees-highest-salary")
def highest_salary():

    if len(employees) == 0:
        return {
            "message": "No employees available"
        }

    highest = employees[0]

    for employee in employees:

        if employee["salary"] > highest["salary"]:
            highest = employee

    return highest


# 14. GET LOWEST SALARY EMPLOYEE
@app.get("/employees-lowest-salary")
def lowest_salary():

    if len(employees) == 0:
        return {
            "message": "No employees available"
        }

    lowest = employees[0]

    for employee in employees:

        if employee["salary"] < lowest["salary"]:
            lowest = employee

    return lowest


# 15. SEARCH EMPLOYEE BY NAME
@app.get("/employees-name/{name}")
def search_by_name(name: str):

    result = []

    for employee in employees:

        if name.lower() in employee["name"].lower():
            result.append(employee)

    return result


# 16. INCREASE EMPLOYEE SALARY
@app.put("/employees/{id}/increase-salary")
def increase_salary(id: int, amount: int):

    for employee in employees:

        if employee["id"] == id:

            employee["salary"] = employee["salary"] + amount

            return {
                "message": "Salary increased successfully",
                "employee": employee
            }

    return {
        "message": "Employee not found"
    }


# 17. UPDATE ONLY DESIGNATION
@app.put("/employees/{id}/designation")
def update_designation(id: int, designation: str):

    for employee in employees:

        if employee["id"] == id:

            employee["designation"] = designation

            return {
                "message": "Designation updated successfully",
                "employee": employee
            }

    return {
        "message": "Employee not found"
    }


# 18. DELETE ALL EMPLOYEES
@app.delete("/employees")
def delete_all_employees():

    employees.clear()

    return {
        "message": "All employees deleted successfully"
    }