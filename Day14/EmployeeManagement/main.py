from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import mysql.connector

app = FastAPI(title="Employee Management")


def get_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="root", database="genAIB2"
    )


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML


@app.get("/employees")
def get_employees():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    try:
        cursor.execute("SELECT eid, name, age, salary, desig FROM Employee ORDER BY eid")
        return cursor.fetchall()
    finally:
        cursor.close()
        con.close()


@app.post("/employees", status_code=201)
def add_employee(employee: dict):
    fields = ("eid", "name", "age", "salary", "desig")
    if any(field not in employee for field in fields):
        raise HTTPException(status_code=400, detail="All employee fields are required")
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute(
            "INSERT INTO Employee (eid, name, age, salary, desig) VALUES (%s, %s, %s, %s, %s)",
            tuple(employee[field] for field in fields),
        )
        con.commit()
        return {"message": "Employee added successfully"}
    except mysql.connector.IntegrityError:
        con.rollback()
        raise HTTPException(status_code=409, detail="Employee ID already exists")
    finally:
        cursor.close()
        con.close()


@app.put("/employees/{eid}")
def update_employee(eid: int, employee: dict):
    fields = ("name", "age", "salary", "desig")
    if any(field not in employee for field in fields):
        raise HTTPException(status_code=400, detail="All employee fields are required")
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT eid FROM Employee WHERE eid = %s", (eid,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        cursor.execute(
            "UPDATE Employee SET name=%s, age=%s, salary=%s, desig=%s WHERE eid=%s",
            tuple(employee[field] for field in fields) + (eid,),
        )
        con.commit()
        return {"message": "Employee updated successfully"}
    finally:
        cursor.close()
        con.close()


@app.delete("/employees/{eid}")
def delete_employee(eid: int):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM Employee WHERE eid=%s", (eid,))
        con.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {"message": "Employee deleted successfully"}
    finally:
        cursor.close()
        con.close()


@app.delete("/employees")
def delete_all_employees():
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM Employee")
        con.commit()
        return {"message": "All employees deleted successfully"}
    finally:
        cursor.close()
        con.close()


HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Employee Management</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Arial, sans-serif; background: #f2f5fa; color: #202b3a; }
    .container { max-width: 1020px; margin: 35px auto; padding: 0 18px; }
    h1 { text-align: center; color: #153b72; }
    .panel { background: white; padding: 24px; border-radius: 12px; margin: 20px 0; box-shadow: 0 3px 14px #102b4d13; }
    h2 { margin-top: 0; font-size: 19px; }
    .form-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); gap: 14px; }
    label { font-size: 13px; font-weight: bold; display: block; margin-bottom: 6px; }
    input { width: 100%; padding: 11px; border: 1px solid #c9d3df; border-radius: 6px; font-size: 14px; }
    .actions { margin-top: 18px; display: flex; flex-wrap: wrap; gap: 10px; }
    button { border: 0; background: #2166d1; color: white; padding: 11px 16px; border-radius: 6px; cursor: pointer; }
    button:hover { filter: brightness(.9); }
    .secondary { background: #66758a; }
    .danger { background: #c9363e; }
    .edit { background: #b07517; }
    .small { padding: 7px 10px; margin: 2px; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; margin-top: 14px; }
    th, td { text-align: left; border-bottom: 1px solid #e1e5eb; padding: 12px; }
    th { background: #eaf1fc; }
    #message { min-height: 20px; margin-top: 12px; font-weight: bold; }
    .ok { color: #176b36; } .error { color: #c9363e; }
  </style>
</head>
<body>
<div class="container">
  <h1>Employee Management System</h1>
  <div class="panel">
    <h2 id="formTitle">Add Employee</h2>
    <form id="employeeForm">
      <div class="form-grid">
        <div><label for="eid">Employee ID</label><input id="eid" type="number" required min="1"></div>
        <div><label for="name">Name</label><input id="name" required maxlength="50"></div>
        <div><label for="age">Age</label><input id="age" type="number" required min="1"></div>
        <div><label for="salary">Salary</label><input id="salary" type="number" required min="0"></div>
        <div><label for="desig">Designation</label><input id="desig" required maxlength="50"></div>
      </div>
      <div class="actions">
        <button type="submit" id="saveButton">Add Employee</button>
        <button type="button" class="secondary" onclick="resetForm()">Clear</button>
      </div>
    </form>
    <div id="message" role="status"></div>
  </div>
  <div class="panel">
    <h2>Employee Records</h2>
    <div class="actions"><button onclick="loadEmployees()">Refresh</button><button class="danger" onclick="deleteAll()">Delete All</button></div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Age</th><th>Salary</th><th>Designation</th><th>Actions</th></tr></thead>
        <tbody id="employeeTable"></tbody>
      </table>
    </div>
  </div>
</div>
<script>
  let editingId = null;
  let currentEmployees = [];
  const byId = id => document.getElementById(id);

  function showMessage(message, error = false) {
    byId('message').textContent = message;
    byId('message').className = error ? 'error' : 'ok';
  }

  async function request(url, options = {}) {
    const response = await fetch(url, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || 'Request failed');
    return result;
  }

  function resetForm() {
    byId('employeeForm').reset();
    byId('eid').disabled = false;
    editingId = null;
    byId('formTitle').textContent = 'Add Employee';
    byId('saveButton').textContent = 'Add Employee';
  }

  byId('employeeForm').addEventListener('submit', async event => {
    event.preventDefault();
    const employee = {
      eid: Number(byId('eid').value),
      name: byId('name').value.trim(),
      age: Number(byId('age').value),
      salary: Number(byId('salary').value),
      desig: byId('desig').value.trim()
    };
    const isEditing = editingId !== null;
    try {
      const result = await request(isEditing ? '/employees/' + editingId : '/employees', {
        method: isEditing ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(employee)
      });
      resetForm();
      showMessage(result.message);
      await loadEmployees();
    } catch (error) { showMessage(error.message, true); }
  });

  async function loadEmployees() {
    try {
      currentEmployees = await request('/employees');
      const tbody = byId('employeeTable');
      tbody.replaceChildren();
      for (const emp of currentEmployees) {
        const tr = document.createElement('tr');
        for (const key of ['eid','name','age','salary','desig']) {
          const td = document.createElement('td');
          td.textContent = emp[key];
          tr.appendChild(td);
        }
        const actions = document.createElement('td');
        const edit = document.createElement('button');
        edit.textContent = 'Edit'; edit.className = 'small edit';
        edit.onclick = () => editEmployee(emp.eid);
        const del = document.createElement('button');
        del.textContent = 'Delete'; del.className = 'small danger';
        del.onclick = () => deleteEmployee(emp.eid);
        actions.append(edit, del);
        tr.appendChild(actions);
        tbody.appendChild(tr);
      }
      if (!currentEmployees.length) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 6; cell.textContent = 'No employees found';
      }
    } catch (error) { showMessage(error.message, true); }
  }

  function editEmployee(id) {
    const emp = currentEmployees.find(item => item.eid === id);
    if (!emp) return;
    editingId = id;
    for (const key of ['eid','name','age','salary','desig']) byId(key).value = emp[key];
    byId('eid').disabled = true;
    byId('formTitle').textContent = 'Update Employee';
    byId('saveButton').textContent = 'Update Employee';
    window.scrollTo({top: 0, behavior: 'smooth'});
  }

  async function deleteEmployee(id) {
    if (!confirm('Delete employee ' + id + '?')) return;
    try {
      const result = await request('/employees/' + id, {method: 'DELETE'});
      if (editingId === id) resetForm();
      showMessage(result.message);
      await loadEmployees();
    } catch (error) { showMessage(error.message, true); }
  }

  async function deleteAll() {
    if (!confirm('Delete ALL employee records?')) return;
    try {
      const result = await request('/employees', {method: 'DELETE'});
      resetForm();
      showMessage(result.message);
      await loadEmployees();
    } catch (error) { showMessage(error.message, true); }
  }

  loadEmployees();
</script>
</body>
</html>'''
