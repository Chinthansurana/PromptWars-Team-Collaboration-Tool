/**
 * TeamFlow UI Components
 * Reusable component rendering functions.
 */
const Components = {
  toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = message;
    el.setAttribute('role', 'alert');
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 4000);
  },

  // --- Project Card ---
  projectCard(project, canEdit = true, canDelete = true) {
    const memberCount = (project.members || []).length;
    const desc = this.escapeHtml(project.description || 'No description provided');
    const name = this.escapeHtml(project.name);
    const status = this.escapeHtml(project.status || 'active');
    const actions = [];
    if (canEdit) actions.push(`<button class="btn btn-sm btn-secondary btn-edit-project" data-id="${project.id}" aria-label="Edit project ${name}">✏️ Edit</button>`);
    if (canDelete) actions.push(`<button class="btn btn-sm btn-danger btn-delete-project" data-id="${project.id}" aria-label="Delete project ${name}">🗑️ Delete</button>`);

    return `<article class="project-card" role="listitem" aria-label="Project: ${name}">
      <h3 class="project-card-title">${name}</h3>
      <p class="project-card-desc">${desc}</p>
      <div class="project-card-meta">
        <span class="member-badge" aria-label="${memberCount} team member${memberCount !== 1 ? 's' : ''}">👥 ${memberCount} member${memberCount !== 1 ? 's' : ''}</span>
        <span class="status-badge status-${status}" aria-label="Status: ${status}">${status}</span>
      </div>
      ${actions.length ? `<div class="project-card-actions">${actions.join('')}</div>` : ''}
    </article>`;
  },

  // --- Task Card ---
  taskCard(task, canEdit = true, canDelete = true) {
    const title = this.escapeHtml(task.title);
    const priority = task.priority || 'medium';
    const assignee = this.escapeHtml(task.assignee || 'Unassigned');
    const tags = (task.tags || []).map(t => `<span class="tag-badge">${this.escapeHtml(t)}</span>`).join('');
    const due = task.due_date ? `<span class="due-badge" aria-label="Due: ${this.escapeHtml(task.due_date)}">📅 ${this.escapeHtml(task.due_date)}</span>` : '';
    const actions = [];
    if (canEdit) actions.push(`<button class="btn btn-sm btn-secondary btn-edit-task" data-id="${task.id}" aria-label="Edit task: ${title}">✏️</button>`);
    if (canDelete) actions.push(`<button class="btn btn-sm btn-danger btn-delete-task" data-id="${task.id}" aria-label="Delete task: ${title}">🗑️</button>`);

    return `<div class="task-card" draggable="true" data-id="${task.id}" role="listitem" aria-label="Task: ${title}, Priority: ${priority}">
      <div class="task-card-title">${title}</div>
      <div class="task-card-meta">
        <span class="priority-badge priority-${priority}" aria-label="Priority: ${priority}">${priority}</span>
        <span class="assignee-badge" aria-label="Assigned to ${assignee}">👤 ${assignee}</span>
        ${due}
      </div>
      ${tags ? `<div class="task-card-tags">${tags}</div>` : ''}
      ${actions.length ? `<div class="task-card-actions">${actions.join('')}</div>` : ''}
    </div>`;
  },

  // --- Project Form ---
  projectFormHtml(project = null, users = []) {
    const selectedMembers = project?.members || [];
    return `
      <div class="form-group">
        <label for="form-project-name" class="form-label">Project Name <span aria-hidden="true">*</span></label>
        <input type="text" class="form-input" id="form-project-name" placeholder="Enter project name" value="${this.escapeHtml(project?.name || '')}" required aria-required="true" maxlength="100">
      </div>
      <div class="form-group">
        <label for="form-project-desc" class="form-label">Description</label>
        <textarea class="form-textarea" id="form-project-desc" placeholder="Describe what this project is about" maxlength="500">${this.escapeHtml(project?.description || '')}</textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Team Members</label>
        <div class="user-multi-select" id="form-project-members">
          ${users.length ? this.userMultiSelect(users, selectedMembers) : '<p class="form-hint">No users available. Create users first in the Users section.</p>'}
        </div>
        <small class="form-hint">Select team members for this project</small>
      </div>`;
  },

  // --- Task Form ---
  taskFormHtml(task = null, projectMembers = []) {
    const statuses = [
      { value: 'todo', label: 'To Do' },
      { value: 'in_progress', label: 'In Progress' },
      { value: 'review', label: 'In Review' },
      { value: 'done', label: 'Done' }
    ];
    const priorities = [
      { value: 'low', label: 'Low' },
      { value: 'medium', label: 'Medium' },
      { value: 'high', label: 'High' },
      { value: 'critical', label: 'Critical' }
    ];
    const currentStatus = task?.status || 'todo';
    const currentPriority = task?.priority || 'medium';
    const currentAssignee = task?.assignee || '';

    return `
      <div class="form-group">
        <label for="form-task-title" class="form-label">Task Title <span aria-hidden="true">*</span></label>
        <input type="text" class="form-input" id="form-task-title" placeholder="Enter task title" value="${this.escapeHtml(task?.title || '')}" required aria-required="true" maxlength="200">
      </div>
      <div class="form-group">
        <label for="form-task-desc" class="form-label">Description</label>
        <textarea class="form-textarea" id="form-task-desc" placeholder="Describe the task in detail" maxlength="1000">${this.escapeHtml(task?.description || '')}</textarea>
      </div>
      <div class="form-row">
        <div class="form-group form-half">
          <label for="form-task-status" class="form-label">Status</label>
          <select class="form-select" id="form-task-status" aria-label="Task status">
            ${statuses.map(s => `<option value="${s.value}" ${currentStatus === s.value ? 'selected' : ''}>${s.label}</option>`).join('')}
          </select>
        </div>
        <div class="form-group form-half">
          <label for="form-task-priority" class="form-label">Priority</label>
          <select class="form-select" id="form-task-priority" aria-label="Task priority">
            ${priorities.map(p => `<option value="${p.value}" ${currentPriority === p.value ? 'selected' : ''}>${p.label}</option>`).join('')}
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group form-half">
          <label for="form-task-assignee" class="form-label">Assignee</label>
          <select class="form-select" id="form-task-assignee" aria-label="Task assignee">
            <option value="">— Unassigned —</option>
            ${projectMembers.map(m => {
              const isSelected = m.id === currentAssignee ? 'selected' : '';
              return `<option value="${m.id}" ${isSelected}>${this.escapeHtml(m.name)}</option>`;
            }).join('')}
          </select>
          ${!projectMembers.length ? '<small class="form-hint">No members in this project. Add members to the project first.</small>' : ''}
        </div>
        <div class="form-group form-half">
          <label for="form-task-due" class="form-label">Due Date</label>
          <input type="date" class="form-input" id="form-task-due" value="${this.escapeHtml(task?.due_date || '')}">
        </div>
      </div>
      <div class="form-group">
        <label for="form-task-tags" class="form-label">Tags</label>
        <input type="text" class="form-input" id="form-task-tags" placeholder="Enter tags separated by commas (e.g., frontend, urgent)" value="${this.escapeHtml((task?.tags || []).join(', '))}">
        <small class="form-hint">Separate multiple tags with commas</small>
      </div>`;
  },

  // --- Chat Message ---
  chatMessage(msg, currentUser) {
    const isSent = msg.sender === currentUser;
    const isAI = msg.msg_type === 'ai_response';
    const cls = isAI ? 'ai-msg' : (isSent ? 'sent' : 'received');
    const sender = isAI ? '🤖 AI' : this.escapeHtml(msg.sender || 'Unknown');
    const content = this.escapeHtml(msg.content || '');
    const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
    return `<div class="chat-message ${cls}" role="article" aria-label="Message from ${sender}">
      <span class="msg-sender">${sender}</span>
      <span class="msg-content">${content}</span>
      ${time ? `<span class="msg-time" aria-label="Sent at ${time}">${time}</span>` : ''}
    </div>`;
  },

  // --- Dashboard List Item ---
  listItem(title, meta) {
    return `<div class="list-item" role="listitem">
      <span class="list-item-title">${this.escapeHtml(title)}</span>
      <span class="list-item-meta">${this.escapeHtml(meta)}</span>
    </div>`;
  },

  // --- Modal ---
  showModal(title, body, footer) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = body;
    document.getElementById('modal-footer').innerHTML = footer;
    const overlay = document.getElementById('modal-overlay');
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = bodyHtml;
    document.getElementById('modal-footer').innerHTML = footerHtml;
    overlay.classList.add('active');
    overlay.setAttribute('aria-hidden', 'false');
    document.getElementById('modal-close').focus();
  },

  closeModal() {
    const overlay = document.getElementById('modal-overlay');
    overlay.classList.remove('active');
    overlay.setAttribute('aria-hidden', 'true');
  },

  // --- Toast ---
  toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `<span aria-hidden="true">${icons[type] || 'ℹ️'}</span> ${this.escapeHtml(message)}`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 4000);
  },

  // --- User Card ---
  userCard(user, canEdit = true, canDelete = true) {
    const name = this.escapeHtml(user.name);
    const email = this.escapeHtml(user.email);
    const role = this.escapeHtml(user.role || 'member');
    const actions = [];
    if (canEdit) actions.push(`<button class="btn btn-sm btn-secondary btn-edit-user" data-id="${user.id}" aria-label="Edit user ${name}">✏️ Edit</button>`);
    if (canDelete) actions.push(`<button class="btn btn-sm btn-danger btn-delete-user" data-id="${user.id}" aria-label="Delete user ${name}">🗑️ Delete</button>`);

    return `<article class="user-card" role="listitem" aria-label="User: ${name}">
      <div class="user-card-header">
        <div class="user-avatar" aria-hidden="true">${name.charAt(0).toUpperCase()}</div>
        <div class="user-card-info">
          <h3 class="user-card-name">${name}</h3>
          <p class="user-card-email">${email}</p>
        </div>
      </div>
      <div class="user-card-meta">
        <span class="role-badge role-${role}" aria-label="Role: ${role}">${role}</span>
      </div>
      ${actions.length ? `<div class="user-card-actions">${actions.join('')}</div>` : ''}
    </article>`;
  },

  // --- User Form ---
  userFormHtml(user = null) {
    const roles = [
      { value: 'member', label: 'Member' },
      { value: 'editor', label: 'Editor' },
      { value: 'admin', label: 'Admin' }
    ];
    const currentRole = user?.role || 'member';

    return `
      <div class="form-group">
        <label for="form-user-name" class="form-label">Name <span aria-hidden="true">*</span></label>
        <input type="text" class="form-input" id="form-user-name" placeholder="Enter user name" value="${this.escapeHtml(user?.name || '')}" required aria-required="true" maxlength="100">
      </div>
      <div class="form-group">
        <label for="form-user-email" class="form-label">Email <span aria-hidden="true">*</span></label>
        <input type="email" class="form-input" id="form-user-email" placeholder="Enter email address" value="${this.escapeHtml(user?.email || '')}" required aria-required="true" maxlength="255">
      </div>
      <div class="form-group">
        <label for="form-user-role" class="form-label">Role</label>
        <select class="form-select" id="form-user-role" aria-label="User role">
          ${roles.map(r => `<option value="${r.value}" ${currentRole === r.value ? 'selected' : ''}>${r.label}</option>`).join('')}
        </select>
      </div>`;
  },

  // --- User Dropdown ---
  userDropdown(users, selectedId = '', includeEmpty = true) {
    let options = includeEmpty ? '<option value="">— Unassigned —</option>' : '';
    users.forEach(u => {
      const selected = u.id === selectedId ? 'selected' : '';
      options += `<option value="${u.id}" ${selected}>${this.escapeHtml(u.name)} (${this.escapeHtml(u.email)})</option>`;
    });
    return options;
  },

  // --- Multi-select for Project Members ---
  userMultiSelect(users, selectedIds = []) {
    let checkboxes = '';
    users.forEach(u => {
      const checked = selectedIds.includes(u.id) ? 'checked' : '';
      checkboxes += `
        <label class="checkbox-label">
          <input type="checkbox" class="user-checkbox" value="${u.id}" ${checked}>
          <span>${this.escapeHtml(u.name)} (${this.escapeHtml(u.email)})</span>
        </label>`;
    });
    return checkboxes;
  }
};

// Modal close handlers
document.getElementById('modal-close').addEventListener('click', Components.closeModal);
document.getElementById('modal-overlay').addEventListener('click', (e) => {
  if (e.target.id === 'modal-overlay') Components.closeModal();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') Components.closeModal();
});
