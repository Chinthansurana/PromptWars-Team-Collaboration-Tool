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

  showModal(title, bodyHtml, footerHtml = '') {
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

  projectCard(project) {
    const memberHtml = (project.members || []).slice(0, 3)
      .map(m => `<span class="member-badge">${this.escapeHtml(m)}</span>`).join('');
    const extra = (project.members || []).length > 3 ? `<span class="member-badge">+${project.members.length - 3}</span>` : '';
    return `<div class="project-card" data-id="${project.id}" tabindex="0" role="button" aria-label="Project: ${this.escapeHtml(project.name)}">
      <h3 class="project-card-title">${this.escapeHtml(project.name)}</h3>
      <p class="project-card-desc">${this.escapeHtml(project.description || 'No description')}</p>
      <div class="project-card-meta">${memberHtml}${extra}</div>
      <div class="project-card-actions">
        <button class="btn btn-sm btn-secondary btn-edit-project" data-id="${project.id}" aria-label="Edit project">Edit</button>
        <button class="btn btn-sm btn-danger btn-delete-project" data-id="${project.id}" aria-label="Delete project">Delete</button>
      </div>
    </div>`;
  },

  taskCard(task) {
    const priorityClass = `priority-${task.priority || 'medium'}`;
    const assignee = task.assignee ? `<span class="assignee-badge">👤 ${this.escapeHtml(task.assignee)}</span>` : '';
    const tags = (task.tags || []).map(t => `<span class="tag-badge">${this.escapeHtml(t)}</span>`).join('');
    return `<div class="task-card" draggable="true" data-id="${task.id}" data-status="${task.status}" tabindex="0" role="listitem" aria-label="Task: ${this.escapeHtml(task.title)}">
      <div class="task-card-title">${this.escapeHtml(task.title)}</div>
      <div class="task-card-meta">
        <span class="priority-badge ${priorityClass}">${task.priority || 'medium'}</span>
        ${assignee}${tags}
      </div>
      <div class="task-card-actions">
        <button class="btn btn-sm btn-secondary btn-edit-task" data-id="${task.id}" aria-label="Edit task">Edit</button>
        <button class="btn btn-sm btn-danger btn-delete-task" data-id="${task.id}" aria-label="Delete task">✕</button>
      </div>
    </div>`;
  },

  chatMessage(msg, currentUser) {
    const isSent = msg.sender === currentUser;
    const isAi = msg.msg_type === 'ai';
    const isSystem = msg.msg_type === 'system';
    let cls = isSent ? 'sent' : 'received';
    if (isAi) cls = 'ai-msg';
    if (isSystem) cls = 'system-msg';
    const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
    return `<div class="chat-message ${cls}">
      ${!isSent && !isSystem ? `<span class="msg-sender">${isAi ? '🤖 AI' : this.escapeHtml(msg.sender)}</span>` : ''}
      <span class="msg-content">${this.escapeHtml(msg.content)}</span>
      <span class="msg-time">${time}</span>
    </div>`;
  },

  projectFormHtml(project = null) {
    const n = project ? this.escapeHtml(project.name) : '';
    const d = project ? this.escapeHtml(project.description) : '';
    const m = project ? (project.members || []).join(', ') : '';
    return `<div class="form-group"><label class="form-label" for="form-project-name">Project Name *</label><input class="form-input" id="form-project-name" type="text" value="${n}" required placeholder="Enter project name"></div>
    <div class="form-group"><label class="form-label" for="form-project-desc">Description</label><textarea class="form-textarea" id="form-project-desc" placeholder="Describe your project">${d}</textarea></div>
    <div class="form-group"><label class="form-label" for="form-project-members">Members (comma-separated)</label><input class="form-input" id="form-project-members" type="text" value="${m}" placeholder="Alice, Bob, Charlie"></div>`;
  },

  taskFormHtml(task = null) {
    const t = task || {};
    const statuses = ['todo','in_progress','review','done'];
    const priorities = ['low','medium','high','critical'];
    const sOpts = statuses.map(s => `<option value="${s}" ${t.status===s?'selected':''}>${s.replace('_',' ')}</option>`).join('');
    const pOpts = priorities.map(p => `<option value="${p}" ${t.priority===p?'selected':''}>${p}</option>`).join('');
    return `<div class="form-group"><label class="form-label" for="form-task-title">Title *</label><input class="form-input" id="form-task-title" type="text" value="${this.escapeHtml(t.title||'')}" required placeholder="Task title"></div>
    <div class="form-group"><label class="form-label" for="form-task-desc">Description</label><textarea class="form-textarea" id="form-task-desc" placeholder="Task details">${this.escapeHtml(t.description||'')}</textarea></div>
    <div class="form-group"><label class="form-label" for="form-task-status">Status</label><select class="form-select" id="form-task-status">${sOpts}</select></div>
    <div class="form-group"><label class="form-label" for="form-task-priority">Priority</label><select class="form-select" id="form-task-priority">${pOpts}</select></div>
    <div class="form-group"><label class="form-label" for="form-task-assignee">Assignee</label><input class="form-input" id="form-task-assignee" type="text" value="${this.escapeHtml(t.assignee||'')}" placeholder="Team member name"></div>
    <div class="form-group"><label class="form-label" for="form-task-due">Due Date</label><input class="form-input" id="form-task-due" type="date" value="${t.due_date||''}"></div>
    <div class="form-group"><label class="form-label" for="form-task-tags">Tags (comma-separated)</label><input class="form-input" id="form-task-tags" type="text" value="${(t.tags||[]).join(', ')}" placeholder="frontend, bug, urgent"></div>`;
  },

  listItem(title, meta) {
    return `<div class="list-item"><span class="list-item-title">${this.escapeHtml(title)}</span><span class="list-item-meta">${this.escapeHtml(meta)}</span></div>`;
  },

  escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
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
