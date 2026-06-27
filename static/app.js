// ============================================================
// app.js  —  Task Manager frontend
// All API calls use the Fetch API (no frameworks).
// Each function is labelled with the HTTP method it exercises.
// ============================================================

const API = "/tasks";   // base URL — same origin as the FastAPI server
let currentFilter = "all";   // "all" | "Pending" | "Completed"
let editingTaskId = null;    // tracks which task is in the edit modal

// ============================================================
// UTILITY: show a short toast notification
// ============================================================
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === "success" ? "✓" : "✗"}</span> ${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = "fadeOut .3s ease forwards";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ============================================================
// FORMAT a UTC date string to readable local time
// ============================================================
function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

// ============================================================
// BUILD the HTML for one task card
// ============================================================
function buildTaskCard(task) {
  const isCompleted = task.status === "Completed";

  return `
    <div class="task-card ${isCompleted ? "completed" : ""}" data-id="${task.id}">
      <div class="task-meta">
        <div class="task-title">${escapeHtml(task.title)}</div>
        ${task.description
          ? `<div class="task-description">${escapeHtml(task.description)}</div>`
          : ""}
        <div class="task-footer">
          <span class="status-badge ${isCompleted ? "completed" : "pending"}">
            <span class="status-dot"></span>
            ${task.status}
          </span>
          <span class="task-date">🕐 ${formatDate(task.created_at)}</span>
        </div>
      </div>

      <div class="task-actions-col">
        <div class="task-actions">
          ${!isCompleted ? `
          <button
            class="btn btn-success btn-sm"
            title="Mark as Completed (PATCH)"
            onclick="markComplete(${task.id})">
            <span class="method-tag patch">PATCH</span> Done
          </button>` : `
          <button
            class="btn btn-ghost btn-sm"
            title="Revert to Pending (PATCH)"
            onclick="markPending(${task.id})">
            <span class="method-tag patch">PATCH</span> Undo
          </button>`}
          <button
            class="btn btn-ghost btn-sm"
            title="Edit task (PUT)"
            onclick="openEditModal(${task.id})">
            <span class="method-tag put">PUT</span> Edit
          </button>
          <button
            class="btn btn-danger btn-sm"
            title="Delete task (DELETE)"
            onclick="deleteTask(${task.id})">
            <span class="method-tag delete">DEL</span>
          </button>
        </div>
      </div>
    </div>
  `;
}

// Simple XSS prevention
function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ============================================================
// GET /tasks  — load and render the task list
// ============================================================
async function loadTasks() {
  const list = document.getElementById("task-list");
  list.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div> Loading tasks…
    </div>`;

  try {
    const res = await fetch(API);
    const json = await res.json();

    if (!json.success) throw new Error(json.message);

    let tasks = json.data || [];

    // Apply client-side filter
    if (currentFilter !== "all") {
      tasks = tasks.filter(t => t.status === currentFilter);
    }

    // Update count badge
    const totalRes = await fetch(API);
    const totalJson = await totalRes.json();
    document.getElementById("task-count").textContent = (totalJson.data || []).length;

    if (tasks.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>${currentFilter === "all" ? "No tasks yet" : `No ${currentFilter} tasks`}</h3>
          <p>${currentFilter === "all"
            ? "Add your first task using the form above."
            : "Try a different filter."}</p>
        </div>`;
      return;
    }

    list.innerHTML = tasks.map(buildTaskCard).join("");

  } catch (err) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">⚠️</div>
        <h3>Failed to load tasks</h3>
        <p>${err.message}</p>
      </div>`;
  }
}

// ============================================================
// POST /tasks  — create a new task
// ============================================================
document.getElementById("task-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const title       = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const status      = document.getElementById("status").value;
  const btn         = document.getElementById("submit-btn");

  if (!title) {
    showToast("Title is required", "error");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Saving…";

  try {
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description, status }),
    });

    const json = await res.json();
    if (!json.success) throw new Error(json.message);

    showToast("Task created successfully ✓");
    e.target.reset();
    await loadTasks();

  } catch (err) {
    showToast(err.message || "Failed to create task", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Add Task";
  }
});

// ============================================================
// PATCH /tasks/{id}  — mark task as Completed
// ============================================================
async function markComplete(id) {
  try {
    const res = await fetch(`${API}/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "Completed" }),
    });
    const json = await res.json();
    if (!json.success) throw new Error(json.message);

    showToast("Task marked as completed");
    await loadTasks();

  } catch (err) {
    showToast(err.message || "Failed to update status", "error");
  }
}

// ============================================================
// PATCH /tasks/{id}  — revert task back to Pending
// ============================================================
async function markPending(id) {
  try {
    const res = await fetch(`${API}/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "Pending" }),
    });
    const json = await res.json();
    if (!json.success) throw new Error(json.message);

    showToast("Task reverted to Pending");
    await loadTasks();

  } catch (err) {
    showToast(err.message || "Failed to update status", "error");
  }
}

// ============================================================
// DELETE /tasks/{id}  — delete a task
// ============================================================
async function deleteTask(id) {
  if (!confirm("Delete this task? This cannot be undone.")) return;

  try {
    const res = await fetch(`${API}/${id}`, { method: "DELETE" });
    const json = await res.json();
    if (!json.success) throw new Error(json.message);

    showToast("Task deleted");
    await loadTasks();

  } catch (err) {
    showToast(err.message || "Failed to delete task", "error");
  }
}

// ============================================================
// GET /tasks/{id}  — fetch one task then open the edit modal
// ============================================================
async function openEditModal(id) {
  editingTaskId = id;

  try {
    const res = await fetch(`${API}/${id}`);
    const json = await res.json();
    if (!json.success) throw new Error(json.message);

    const task = json.data;
    document.getElementById("edit-title").value       = task.title;
    document.getElementById("edit-description").value = task.description || "";
    document.getElementById("edit-status").value      = task.status;

    document.getElementById("edit-modal").style.display = "flex";

  } catch (err) {
    showToast(err.message || "Could not load task", "error");
  }
}

// ============================================================
// PUT /tasks/{id}  — full update from the edit modal
// ============================================================
document.getElementById("edit-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const title       = document.getElementById("edit-title").value.trim();
  const description = document.getElementById("edit-description").value.trim();
  const status      = document.getElementById("edit-status").value;
  const btn         = document.getElementById("edit-submit-btn");

  if (!title) {
    showToast("Title is required", "error");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Saving…";

  try {
    const res = await fetch(`${API}/${editingTaskId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description, status }),
    });

    const json = await res.json();
    if (!json.success) throw new Error(json.message);

    showToast("Task updated successfully");
    closeModal();
    await loadTasks();

  } catch (err) {
    showToast(err.message || "Failed to update task", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Changes";
  }
});

// ============================================================
// Modal helpers
// ============================================================
function closeModal() {
  document.getElementById("edit-modal").style.display = "none";
  editingTaskId = null;
}

// Close modal when clicking outside the card
document.getElementById("edit-modal").addEventListener("click", (e) => {
  if (e.target === e.currentTarget) closeModal();
});

// Close on Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

// ============================================================
// Filter buttons
// ============================================================
document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    currentFilter = btn.dataset.filter;
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    loadTasks();
  });
});

// ============================================================
// Cancel button in the create form
// ============================================================
document.getElementById("cancel-btn").addEventListener("click", () => {
  document.getElementById("task-form").reset();
});

// ============================================================
// Bootstrap — load tasks when the page first opens
// ============================================================
loadTasks();
