const API = "/employees";
const $ = (id) => document.getElementById(id);
let employees = [];
let editingId = null;

function showMessage(text, type = "success") {
  const element = $("message");
  element.textContent = text;
  element.className = `message ${type}`;
  element.hidden = false;
}

async function request(url, options = {}) {
  let response;
  try {
    response = await fetch(url, options);
  } catch (_) {
    throw new Error("Cannot reach FastAPI. Make sure the server is running.");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    throw new Error(typeof detail === "string" ? detail : `Request failed (${response.status})`);
  }
  return data;
}

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function renderEmployees() {
  const query = $("search").value.trim().toLowerCase();
  const filtered = employees.filter(emp => String(emp.eid).includes(query) || emp.name.toLowerCase().includes(query));
  $("totalCount").textContent = employees.length;
  $("employeeRows").innerHTML = filtered.length ? filtered.map(emp => `
    <tr>
      <td>${emp.eid}</td><td><strong>${escapeHtml(emp.name)}</strong></td><td>${emp.age}</td>
      <td>₹${Number(emp.salary).toLocaleString("en-IN")}</td><td>${escapeHtml(emp.desig)}</td>
      <td><div class="actions"><button class="btn small ghost" data-action="edit" data-id="${emp.eid}">Edit</button>
      <button class="btn small danger" data-action="delete" data-id="${emp.eid}">Delete</button></div></td>
    </tr>`).join("") : `<tr><td colspan="6" class="empty">No employees found</td></tr>`;
}

async function getAllEmployees() {
  try {
    employees = await request(API);
    renderEmployees();
  } catch (err) {
    showMessage(err.message, "error");
  }
}

async function getEmployeeById(id) {
  return request(`${API}/${encodeURIComponent(id)}`);
}

function formData() {
  const name = $("name").value.trim();
  const desig = $("desig").value.trim();
  if (!name || !desig) throw new Error("Name and designation cannot be empty.");
  return {eid: Number($("eid").value), name, age: Number($("age").value), salary: Number($("salary").value), desig};
}

function resetForm() {
  $("employeeForm").reset();
  editingId = null;
  $("eid").disabled = false;
  $("saveBtn").textContent = "+ Add employee";
  $("formTitle").textContent = "Add employee";
}

async function addEmployee(data) {
  return request(API, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)});
}

async function updateEmployee(id, data) {
  const {eid, ...changes} = data;
  return request(`${API}/${id}`, {method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(changes)});
}

async function deleteEmployee(id) {
  const employee = await getEmployeeById(id);
  if (!confirm(`Delete ${employee.name} (ID ${id})?`)) return;
  try {
    const result = await request(`${API}/${id}`, {method:"DELETE"});
    if (editingId === id) resetForm();
    await getAllEmployees();
    showMessage(result.message);
  } catch (err) { showMessage(err.message, "error"); }
}

async function deleteAllEmployees() {
  if (!employees.length) return showMessage("No employees to delete.", "error");
  if (!confirm(`Delete ALL ${employees.length} employees? This cannot be undone.`)) return;
  try {
    const result = await request(API, {method:"DELETE"});
    resetForm();
    await getAllEmployees();
    showMessage(result.message);
  } catch (err) { showMessage(err.message, "error"); }
}

$("employeeForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = $("saveBtn");
  try {
    const data = formData();
    button.disabled = true;
    const result = editingId === null ? await addEmployee(data) : await updateEmployee(editingId, data);
    resetForm();
    await getAllEmployees();
    showMessage(result.message);
  } catch (err) { showMessage(err.message, "error"); }
  finally { button.disabled = false; }
});

$("employeeRows").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = Number(button.dataset.id);
  if (button.dataset.action === "delete") {
    try { await deleteEmployee(id); } catch(err) { showMessage(err.message, "error"); }
  } else if (button.dataset.action === "edit") {
    try {
      const emp = await getEmployeeById(id);
      for (const field of ["eid", "name", "age", "salary", "desig"]) $(field).value = emp[field];
      editingId = id;
      $("eid").disabled = true;
      $("saveBtn").textContent = "Save changes";
      $("formTitle").textContent = `Edit employee #${id}`;
      $("employeeForm").scrollIntoView({behavior:"smooth", block:"start"});
    } catch(err) { showMessage(err.message, "error"); }
  }
});

$("search").addEventListener("input", renderEmployees);
$("refreshBtn").addEventListener("click", getAllEmployees);
$("clearBtn").addEventListener("click", resetForm);
$("deleteAllBtn").addEventListener("click", deleteAllEmployees);
getAllEmployees();
