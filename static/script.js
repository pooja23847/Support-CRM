// ---------- Helpers ----------
console.log("SCRIPT LOADED");
function statusColor(status) {
  if (status === "Open") return "bg-yellow-100 text-yellow-800";
  if (status === "In Progress") return "bg-blue-100 text-blue-800";
  if (status === "Closed") return "bg-green-100 text-green-800";
  return "bg-gray-100 text-gray-800";
}

function priorityColor(priority) {
  if (priority === "High") return "bg-red-100 text-red-800";
  if (priority === "Medium") return "bg-orange-100 text-orange-800";
  return "bg-gray-100 text-gray-800";
}

function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

// ---------- HOME PAGE: load + search + filter tickets ----------

async function loadTickets() {
  const tableBody = document.getElementById("ticketTableBody");
  const emptyMessage = document.getElementById("emptyMessage");
  if (!tableBody) return; // not on the home page

  const search = document.getElementById("searchBox").value;
  const status = document.getElementById("statusFilter").value;

  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (status) params.append("status", status);

  const res = await fetch(`/api/tickets?${params.toString()}`);
  const tickets = await res.json();

  if (tickets.length === 0) {
    tableBody.innerHTML = "";
    emptyMessage.classList.remove("hidden");
    return;
  }
  emptyMessage.classList.add("hidden");

  tableBody.innerHTML = tickets.map(t => `
  <tr class="border-t hover:bg-gray-50 cursor-pointer" onclick="window.location.href='/tickets/${t.ticket_id}'">
    <td class="px-4 py-3 font-medium text-gray-700">${t.ticket_id}</td>
    <td class="px-4 py-3">${t.customer_name}</td>
    <td class="px-4 py-3">${t.subject}</td>
    <td class="px-4 py-3">
      <span class="text-xs px-2 py-1 rounded-full ${priorityColor(t.priority)}">${t.priority}</span>
    </td>
    <td class="px-4 py-3">
      <span class="text-xs px-2 py-1 rounded-full ${statusColor(t.status)}">${t.status}</span>
    </td>
    <td class="px-4 py-3 text-gray-500 text-sm">${formatDate(t.created_at)}</td>
  </tr>
`).join("");
}

const searchBox = document.getElementById("searchBox");
const statusFilter = document.getElementById("statusFilter");
if (searchBox) {
  searchBox.addEventListener("input", loadTickets);   // fires on every keystroke
  statusFilter.addEventListener("change", loadTickets);
  loadTickets(); // initial load when page opens
}

// ---------- CREATE PAGE: submit new ticket ----------

const createForm = document.getElementById("createForm");
if (createForm) {
  createForm.addEventListener("submit", async function (e) {
    e.preventDefault(); // stop the browser's default full-page-reload form submit

    const payload = {
      customer_name: document.getElementById("customer_name").value,
      customer_email: document.getElementById("customer_email").value,
      subject: document.getElementById("subject").value,
      description: document.getElementById("description").value,
      priority: document.getElementById("priority").value,
    };

    const res = await fetch("/api/tickets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      const errorBox = document.getElementById("formError");
      errorBox.textContent = data.error || "Something went wrong.";
      errorBox.classList.remove("hidden");
      return;
    }

    // success — go to the new ticket's detail page
    window.location.href = `/tickets/${data.ticket_id}`;
  });
}

// ---------- DETAIL PAGE: load ticket + handle status/notes update ----------

const ticketDetailDiv = document.getElementById("ticketDetail");
if (ticketDetailDiv) {
  const ticketId = ticketDetailDiv.dataset.ticketId;
  loadTicketDetail(ticketId);
}

async function loadTicketDetail(ticketId) {
  const res = await fetch(`/api/tickets/${ticketId}`);
  const container = document.getElementById("ticketDetail");

  if (!res.ok) {
    container.innerHTML = `<p class="text-red-600">Ticket not found.</p>`;
    return;
  }

  const t = await res.json();

  const notesHtml = t.notes.length
    ? t.notes.map(n => `
        <div class="border-l-2 border-blue-300 pl-3 py-1 mb-2">
          <p class="text-sm text-gray-700">${n.note_text}</p>
          <p class="text-xs text-gray-400">${formatDate(n.created_at)}</p>
        </div>
      `).join("")
    : `<p class="text-gray-400 text-sm">No notes yet.</p>`;

  container.innerHTML = `
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-start mb-4">
        <div>
          <h1 class="text-xl font-bold text-gray-800">${t.subject}</h1>
          <p class="text-sm text-gray-500">${t.ticket_id}</p>
        </div>
        <span class="text-xs px-2 py-1 rounded-full ${statusColor(t.status)}">${t.status}</span>
      </div>

      <p class="text-sm text-gray-600 mb-1"><strong>Customer:</strong> ${t.customer_name} (${t.customer_email})</p>
      <p class="text-sm text-gray-600 mb-4"><strong>Created:</strong> ${formatDate(t.created_at)}</p>
      <p class="text-gray-700 mb-6">${t.description}</p>

      <div class="border-t pt-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Update Status</label>
        <select id="statusSelect" class="border border-gray-300 rounded-lg px-3 py-2 mb-4">
          <option value="Open" ${t.status === "Open" ? "selected" : ""}>Open</option>
          <option value="In Progress" ${t.status === "In Progress" ? "selected" : ""}>In Progress</option>
          <option value="Closed" ${t.status === "Closed" ? "selected" : ""}>Closed</option>
        </select>

        <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
        <select id="prioritySelect" class="border border-gray-300 rounded-lg px-3 py-2 mb-4">
          <option value="Low" ${t.priority === "Low" ? "selected" : ""}>Low</option>
          <option value="Medium" ${t.priority === "Medium" ? "selected" : ""}>Medium</option>
          <option value="High" ${t.priority === "High" ? "selected" : ""}>High</option>
        </select>

        <label class="block text-sm font-medium text-gray-700 mb-1">Add Note</label>
        <textarea id="noteText" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-3"></textarea>

        <button id="updateBtn" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          Save Update
        </button>
      </div>

      <div class="border-t mt-6 pt-4">
        <h2 class="text-sm font-medium text-gray-700 mb-2">Notes History</h2>
        ${notesHtml}
      </div>
    </div>
  `;

  document.getElementById("updateBtn").addEventListener("click", async function () {
    const status = document.getElementById("statusSelect").value;
    const notes = document.getElementById("noteText").value;
    const priority = document.getElementById("prioritySelect").value;

    await fetch(`/api/tickets/${ticketId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, notes, priority }),
    });

    

    loadTicketDetail(ticketId); // reload to show the update
  });
}