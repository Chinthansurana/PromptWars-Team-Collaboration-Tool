/**
 * TeamFlow Main Application
 */
const App = {
  currentView: 'dashboard',
  currentUser: 'Team Member',
  projects: [],
  allTasks: [],
  users: [],

  async init() {
    this.bindNav();
    this.bindSidebar();
    this.bindProjectActions();
    this.bindTaskActions();
    this.bindChat();
    this.bindGenie();
    this.bindTheme();
    this.bindUserActions();
    AI.init();
    await this.loadUsers();
    await this.loadDashboard();
  },

  // --- Navigation ---
  bindNav() {
    document.querySelectorAll('.nav-item').forEach(btn => {
      btn.addEventListener('click', () => this.switchView(btn.dataset.view));
    });
  },

  switchView(view) {
    this.currentView = view;
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const viewEl = document.getElementById(`view-${view}`);
    if (viewEl) viewEl.classList.add('active');

    const titles = {
      dashboard: ['Dashboard', 'Overview of your team\'s coordination and workflow'],
      projects: ['Projects', 'Manage and organize team projects'],
      board: ['Kanban Board', 'Visualize task workflow and track progress'],
      chat: ['Team Chat', 'Coordinate and communicate with your team'],
      ai: ['AI Tools', 'AI-powered collaboration and productivity tools'],
      users: ['Users', 'Manage team members and permissions']
    };
    const [t, s] = titles[view] || ['', ''];
    document.getElementById('page-title').textContent = t;
    document.getElementById('page-subtitle').textContent = s;
    const newBtn = document.getElementById('btn-new-project');
    const newUserBtn = document.getElementById('btn-new-user-header');
    newBtn.style.display = (view === 'projects' || view === 'dashboard') ? '' : 'none';
    newUserBtn.style.display = (view === 'users') ? '' : 'none';

    if (view === 'projects') this.loadProjects();
    if (view === 'board') this.loadBoard();
    if (view === 'dashboard') this.loadDashboard();
    if (view === 'users') this.loadUsers();
  },

  bindSidebar() {
    document.getElementById('sidebar-toggle').addEventListener('click', () => {
      document.getElementById('sidebar').classList.toggle('collapsed');
    });
  },

  // --- Projects ---
  bindProjectActions() {
    document.getElementById('btn-new-project').addEventListener('click', () => this.showProjectForm());
    document.getElementById('projects-grid').addEventListener('click', (e) => {
      const editBtn = e.target.closest('.btn-edit-project');
      const delBtn = e.target.closest('.btn-delete-project');
      if (editBtn) { this.editProject(editBtn.dataset.id); }
      else if (delBtn) { this.deleteProject(delBtn.dataset.id); }
    });
  },

  async loadProjects() {
    try {
      this.projects = await API.listProjects();
      const grid = document.getElementById('projects-grid');
      if (!this.projects.length) { grid.innerHTML = '<p class="empty-state">No projects yet. Click "New Project" to get started!</p>'; return; }
      grid.innerHTML = this.projects.map(p => Components.projectCard(p)).join('');
      this.updateProjectSelects();
    } catch (err) { Components.toast('Failed to load projects', 'error'); }
  },

  updateProjectSelects() {
    const opts = '<option value="">Select a project</option>' + this.projects.map(p => `<option value="${p.id}">${Components.escapeHtml(p.name)}</option>`).join('');
    ['board-project-select', 'chat-project-select', 'ai-project-select'].forEach(id => { document.getElementById(id).innerHTML = opts; });
  },

  showProjectForm(project = null) {
    const title = project ? 'Edit Project' : 'Create New Project';
    Components.showModal(title, Components.projectFormHtml(project, this.users),
      `<button class="btn btn-secondary" id="modal-cancel" type="button">Cancel</button>
       <button class="btn btn-primary" id="modal-save" type="button">${project ? 'Update' : 'Create'} Project</button>`);
    document.getElementById('modal-cancel').addEventListener('click', Components.closeModal);
    document.getElementById('modal-save').addEventListener('click', () => this.saveProject(project));
  },

  async saveProject(existing) {
    const name = document.getElementById('form-project-name').value.trim();
    if (!name) { Components.toast('Project name is required.', 'error'); return; }
    
    // Get selected user IDs from checkboxes
    const checkboxes = document.querySelectorAll('.user-checkbox:checked');
    const members = Array.from(checkboxes).map(cb => cb.value);
    
    const data = {
      name,
      description: document.getElementById('form-project-desc').value.trim(),
      members: members
    };
    try {
      if (existing) { await API.updateProject(existing.id, data); Components.toast('Project updated!', 'success'); }
      else { await API.createProject(data); Components.toast('Project created!', 'success'); }
      Components.closeModal();
      await this.loadProjects();
      await this.loadDashboard();
    } catch (err) { Components.toast(err.message, 'error'); }
  },

  async editProject(id) {
    try {
      const project = await API.getProject(id);
      this.showProjectForm(project);
    } catch (err) { Components.toast('Failed to load project', 'error'); }
  },

  async deleteProject(id) {
    if (!confirm('Delete this project and all its tasks?')) return;
    try {
      await API.deleteProject(id);
      Components.toast('Project deleted', 'success');
      await this.loadProjects();
      await this.loadDashboard();
    } catch (err) { Components.toast('Failed to delete project', 'error'); }
  },

  // --- Dashboard ---
  async loadDashboard() {
    try {
      this.projects = await API.listProjects();
      this.updateProjectSelects();
      let totalTasks = 0, doneTasks = 0, progressTasks = 0;
      this.allTasks = [];
      for (const p of this.projects.slice(0, 10)) {
        const tasks = await API.listTasks(p.id);
        tasks.forEach(t => { t._projectName = p.name; });
        this.allTasks.push(...tasks);
        totalTasks += tasks.length;
        doneTasks += tasks.filter(t => t.status === 'done').length;
        progressTasks += tasks.filter(t => t.status === 'in_progress').length;
      }
      document.getElementById('stat-projects-count').textContent = this.projects.length;
      document.getElementById('stat-tasks-count').textContent = totalTasks;
      document.getElementById('stat-done-count').textContent = doneTasks;
      document.getElementById('stat-progress-count').textContent = progressTasks;
      const recentProjects = document.getElementById('recent-projects-list');
      recentProjects.innerHTML = this.projects.length ? this.projects.slice(0, 5).map(p => Components.listItem(p.name, p.status)).join('') : '<p class="empty-state">No projects yet</p>';
      const recentTasks = document.getElementById('recent-tasks-list');
      recentTasks.innerHTML = this.allTasks.length ? this.allTasks.slice(0, 5).map(t => Components.listItem(t.title, `${t.status} • ${t._projectName || ''}`)).join('') : '<p class="empty-state">No tasks yet</p>';
    } catch (err) { console.error(err); }
  },

  // --- Kanban Board ---
  bindTaskActions() {
    document.getElementById('board-project-select').addEventListener('change', (e) => {
      document.getElementById('btn-new-task').disabled = !e.target.value;
      if (e.target.value) this.loadBoardTasks(e.target.value);
    });
    document.getElementById('btn-new-task').addEventListener('click', () => {
      const pid = document.getElementById('board-project-select').value;
      if (pid) this.showTaskForm(pid);
    });
    document.getElementById('kanban-board').addEventListener('click', (e) => {
      const editBtn = e.target.closest('.btn-edit-task');
      const delBtn = e.target.closest('.btn-delete-task');
      if (editBtn) this.editTask(editBtn.dataset.id);
      else if (delBtn) this.removeTask(delBtn.dataset.id);
    });
    this.initDragDrop();
  },

  async loadBoard() {
    const pid = document.getElementById('board-project-select').value;
    if (pid) await this.loadBoardTasks(pid);
  },

  async loadBoardTasks(projectId) {
    try {
      const tasks = await API.listTasks(projectId);
      const columns = { todo: [], in_progress: [], review: [], done: [] };
      tasks.forEach(t => { if (columns[t.status]) columns[t.status].push(t); });
      Object.entries(columns).forEach(([status, items]) => {
        const colId = status === 'in_progress' ? 'tasks-in-progress' : `tasks-${status}`;
        const countId = status === 'in_progress' ? 'count-in-progress' : `count-${status}`;
        document.getElementById(colId).innerHTML = items.map(t => Components.taskCard(t)).join('') || '<p class="empty-state" style="padding:20px">No tasks</p>';
        document.getElementById(countId).textContent = items.length;
      });
    } catch (err) { Components.toast('Failed to load tasks', 'error'); }
  },

  showTaskForm(projectId, task = null) {
    const title = task ? 'Edit Task' : 'Create New Task';
    
    // Get project members for the assignee dropdown
    const project = this.projects.find(p => p.id === projectId);
    const projectMembers = [];
    if (project && project.members) {
      project.members.forEach(memberId => {
        const user = this.users.find(u => u.id === memberId);
        if (user) projectMembers.push(user);
      });
    }
    
    Components.showModal(title, Components.taskFormHtml(task, projectMembers),
      `<button class="btn btn-secondary" id="modal-cancel" type="button">Cancel</button>
       <button class="btn btn-primary" id="modal-save" type="button">${task ? 'Update' : 'Create'} Task</button>`);
    document.getElementById('modal-cancel').addEventListener('click', Components.closeModal);
    document.getElementById('modal-save').addEventListener('click', () => this.saveTask(projectId, task));
  },

  async saveTask(projectId, existing) {
    const title = document.getElementById('form-task-title').value.trim();
    if (!title) { Components.toast('Task title is required', 'error'); return; }
    const data = {
      title, description: document.getElementById('form-task-desc').value.trim(),
      status: document.getElementById('form-task-status').value,
      priority: document.getElementById('form-task-priority').value,
      assignee: document.getElementById('form-task-assignee').value.trim(),
      due_date: document.getElementById('form-task-due').value || null,
      tags: document.getElementById('form-task-tags').value.split(',').map(t => t.trim()).filter(Boolean)
    };
    try {
      if (existing) { await API.updateTask(existing.id, data); Components.toast('Task updated!', 'success'); }
      else { await API.createTask(projectId, data); Components.toast('Task created!', 'success'); }
      Components.closeModal();
      await this.loadBoardTasks(projectId);
    } catch (err) { Components.toast(err.message, 'error'); }
  },

  async editTask(id) {
    try {
      const task = await API.request('GET', `/api/tasks/${id}`);
      const pid = document.getElementById('board-project-select').value || task.project_id;
      this.showTaskForm(pid, task);
    } catch (err) { Components.toast('Failed to load task', 'error'); }
  },

  async removeTask(id) {
    if (!confirm('Delete this task?')) return;
    try {
      await API.deleteTask(id);
      Components.toast('Task deleted', 'success');
      const pid = document.getElementById('board-project-select').value;
      if (pid) await this.loadBoardTasks(pid);
    } catch (err) { Components.toast('Failed to delete', 'error'); }
  },

  initDragDrop() {
    const board = document.getElementById('kanban-board');
    board.addEventListener('dragstart', (e) => {
      const card = e.target.closest('.task-card');
      if (card) { e.dataTransfer.setData('text/plain', card.dataset.id); card.classList.add('dragging'); }
    });
    board.addEventListener('dragend', (e) => {
      const card = e.target.closest('.task-card');
      if (card) card.classList.remove('dragging');
    });
    document.querySelectorAll('.column-tasks').forEach(col => {
      col.addEventListener('dragover', (e) => { e.preventDefault(); col.style.background = 'rgba(108,92,231,0.1)'; });
      col.addEventListener('dragleave', () => { col.style.background = ''; });
      col.addEventListener('drop', async (e) => {
        e.preventDefault(); col.style.background = '';
        const taskId = e.dataTransfer.getData('text/plain');
        const newStatus = col.closest('.kanban-column').dataset.status;
        try {
          await API.updateTaskStatus(taskId, newStatus);
          const pid = document.getElementById('board-project-select').value;
          if (pid) await this.loadBoardTasks(pid);
        } catch (err) { Components.toast('Failed to move task', 'error'); }
      });
    });
  },

  // --- Chat ---
  bindChat() {
    document.getElementById('chat-project-select').addEventListener('change', (e) => {
      const v = e.target.value;
      document.getElementById('chat-input').disabled = !v;
      document.getElementById('btn-send-message').disabled = !v;
      if (v) this.loadMessages(v);
    });
    document.getElementById('btn-send-message').addEventListener('click', () => this.sendMessage());
    document.getElementById('chat-input').addEventListener('keydown', (e) => { if (e.key === 'Enter') this.sendMessage(); });
  },

  async loadMessages(projectId) {
    try {
      const msgs = await API.listMessages(projectId);
      const container = document.getElementById('chat-messages');
      container.innerHTML = msgs.length ? msgs.map(m => Components.chatMessage(m, this.currentUser)).join('') : '<p class="empty-state">No messages yet. Say hello!</p>';
      container.scrollTop = container.scrollHeight;
    } catch (err) { Components.toast('Failed to load messages', 'error'); }
  },

  async sendMessage() {
    const input = document.getElementById('chat-input');
    const pid = document.getElementById('chat-project-select').value;
    const content = input.value.trim();
    if (!content || !pid) return;
    input.value = '';
    try {
      await API.sendMessage(pid, { content, sender: this.currentUser });
      await this.loadMessages(pid);
    } catch (err) { Components.toast('Failed to send message.', 'error'); }
  },

  // --- Genie AI Chatbot ---
  bindGenie() {
    const toggle = document.getElementById('genie-toggle');
    const panel = document.getElementById('genie-panel');
    const close = document.getElementById('genie-close');
    const sendBtn = document.getElementById('btn-genie-send');
    const input = document.getElementById('genie-input');

    toggle.addEventListener('click', () => {
      const isOpen = panel.classList.toggle('active');
      panel.setAttribute('aria-hidden', String(!isOpen));
      toggle.setAttribute('aria-expanded', String(isOpen));
      if (isOpen) input.focus();
    });
    close.addEventListener('click', () => {
      panel.classList.remove('active');
      panel.setAttribute('aria-hidden', 'true');
      toggle.setAttribute('aria-expanded', 'false');
    });
    sendBtn.addEventListener('click', () => this.sendGenieMessage());
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') this.sendGenieMessage(); });
  },

  async sendGenieMessage() {
    const input = document.getElementById('genie-input');
    const messages = document.getElementById('genie-messages');
    const content = input.value.trim();
    if (!content) return;
    input.value = '';

    const projectId = this.projects.length ? this.projects[0].id : null;

    messages.innerHTML += `<div class="chat-message sent"><span class="msg-content">${Components.escapeHtml(content)}</span></div>`;
    messages.innerHTML += '<div class="chat-message ai-msg" id="genie-typing"><span class="msg-sender">🧞 Genie</span><span class="msg-content"><span class="loading"></span> Thinking...</span></div>';
    messages.scrollTop = messages.scrollHeight;

    try {
      const result = await API.genieChat(projectId, content);
      const typing = document.getElementById('genie-typing');
      if (typing) typing.remove();
      messages.innerHTML += `<div class="chat-message ai-msg"><span class="msg-sender">🧞 Genie</span><span class="msg-content">${Components.escapeHtml(result.response)}</span></div>`;
    } catch (err) {
      const typing = document.getElementById('genie-typing');
      if (typing) typing.remove();
      messages.innerHTML += '<div class="chat-message ai-msg"><span class="msg-sender">🧞 Genie</span><span class="msg-content">Sorry, I encountered an error. Please try again later.</span></div>';
    }
    messages.scrollTop = messages.scrollHeight;
  },

  // --- User Management ---
  bindUserActions() {
    document.getElementById('btn-new-user').addEventListener('click', () => {
      if (!this.canEdit()) { Components.toast('You don\'t have permission to create users.', 'error'); return; }
      this.showUserForm();
    });
    document.getElementById('btn-new-user-header').addEventListener('click', () => {
      if (!this.canEdit()) { Components.toast('You don\'t have permission to create users.', 'error'); return; }
      this.showUserForm();
    });
    document.getElementById('users-grid').addEventListener('click', (e) => {
      const editBtn = e.target.closest('.btn-edit-user');
      const delBtn = e.target.closest('.btn-delete-user');
      if (editBtn) {
        if (!this.canEdit()) { Components.toast('Permission denied.', 'error'); return; }
        this.editUser(editBtn.dataset.id);
      }
      if (delBtn) {
        if (!this.canDelete()) { Components.toast('Only admins can delete users.', 'error'); return; }
        this.deleteUser(delBtn.dataset.id);
      }
    });
  },

  async loadUsers() {
    const grid = document.getElementById('users-grid');
    grid.innerHTML = '<p class="empty-state" role="status"><span class="loading"></span> Loading users...</p>';
    try {
      this.users = await API.listUsers();
      if (!this.users.length) {
        grid.innerHTML = '<p class="empty-state" role="status">No users yet. Click "New User" to add your first team member!</p>';
        return;
      }
      grid.innerHTML = this.users.map(u => Components.userCard(u, this.canEdit(), this.canDelete())).join('');
    } catch (err) {
      grid.innerHTML = '<p class="empty-state" role="status" style="color:var(--danger)">Failed to load users. Please refresh.</p>';
      Components.toast('Failed to load users: ' + err.message, 'error');
    }
  },

  showUserForm(user = null) {
    const title = user ? 'Edit User' : 'Create New User';
    Components.showModal(title, Components.userFormHtml(user),
      `<button class="btn btn-secondary" id="modal-cancel" type="button">Cancel</button>
       <button class="btn btn-primary" id="modal-save" type="button">${user ? 'Update' : 'Create'} User</button>`);
    document.getElementById('modal-cancel').addEventListener('click', Components.closeModal);
    document.getElementById('modal-save').addEventListener('click', () => this.saveUser(user));
    document.getElementById('form-user-name').focus();
  },

  async saveUser(existing) {
    const name = document.getElementById('form-user-name').value.trim();
    const email = document.getElementById('form-user-email').value.trim();
    if (!name || !email) { Components.toast('Name and email are required.', 'error'); return; }
    const data = {
      name,
      email,
      role: document.getElementById('form-user-role').value
    };
    try {
      if (existing) {
        await API.updateUser(existing.id, data);
        Components.toast('User updated successfully!', 'success');
      } else {
        await API.createUser(data);
        Components.toast('User created successfully!', 'success');
      }
      Components.closeModal();
      await this.loadUsers();
    } catch (err) { Components.toast('Error: ' + err.message, 'error'); }
  },

  async editUser(id) {
    try {
      const user = await API.getUser(id);
      this.showUserForm(user);
    } catch (err) { Components.toast('Failed to load user details.', 'error'); }
  },

  async deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user? This cannot be undone.')) return;
    try {
      await API.deleteUser(id);
      Components.toast('User deleted successfully.', 'success');
      await this.loadUsers();
    } catch (err) { Components.toast('Failed to delete user.', 'error'); }
  }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => App.init());
