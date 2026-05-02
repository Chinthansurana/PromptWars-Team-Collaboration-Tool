/**
 * TeamFlow Main Application
 * Handles navigation, CRUD, Kanban board, chat, Genie chatbot, and theming.
 */
const App = {
  currentView: 'dashboard',
  currentUser: 'Team Member',
  currentUserRole: 'admin', // admin, editor, viewer
  projects: [],
  allTasks: [],

  async init() {
    this.bindNav();
    this.bindSidebar();
    this.bindProjectActions();
    this.bindTaskActions();
    this.bindChat();
    this.bindGenie();
    this.bindTheme();
    AI.init();
    await this.loadDashboard();
  },

  // --- Theme ---
  bindTheme() {
    const saved = localStorage.getItem('teamflow-theme') || 'dark';
    this.applyTheme(saved);
    document.getElementById('theme-toggle').addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : current === 'light' ? 'system' : 'dark';
      this.applyTheme(next);
      localStorage.setItem('teamflow-theme', next);
    });
  },

  applyTheme(theme) {
    const btn = document.getElementById('theme-toggle');
    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
      document.documentElement.setAttribute('data-theme', theme);
    }
    const icons = { dark: '🌙', light: '☀️', system: '💻' };
    const labels = { dark: 'Dark Mode', light: 'Light Mode', system: 'System' };
    btn.innerHTML = `<span aria-hidden="true">${icons[theme]}</span> <span class="nav-label">${labels[theme]}</span>`;
    btn.setAttribute('aria-label', `Current theme: ${labels[theme]}. Click to change.`);
  },

  // --- Navigation ---
  bindNav() {
    document.querySelectorAll('.nav-item[data-view]').forEach(btn => {
      btn.addEventListener('click', () => this.switchView(btn.dataset.view));
    });
  },

  switchView(view) {
    this.currentView = view;
    document.querySelectorAll('.nav-item[data-view]').forEach(n => {
      n.classList.remove('active');
      n.setAttribute('aria-selected', 'false');
    });
    const activeNav = document.querySelector(`[data-view="${view}"]`);
    if (activeNav) {
      activeNav.classList.add('active');
      activeNav.setAttribute('aria-selected', 'true');
    }
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const viewEl = document.getElementById(`view-${view}`);
    if (viewEl) viewEl.classList.add('active');

    const titles = {
      dashboard: ['Dashboard', 'Overview of your team\'s coordination and workflow'],
      projects: ['Projects', 'Manage and organize team projects'],
      board: ['Kanban Board', 'Visualize task workflow and track progress'],
      chat: ['Team Chat', 'Coordinate and communicate with your team'],
      ai: ['AI Tools', 'AI-powered collaboration and productivity tools']
    };
    const [t, s] = titles[view] || ['', ''];
    document.getElementById('page-title').textContent = t;
    document.getElementById('page-subtitle').textContent = s;

    const newBtn = document.getElementById('btn-new-project');
    newBtn.style.display = (view === 'projects' || view === 'dashboard') ? '' : 'none';

    if (view === 'projects') this.loadProjects();
    if (view === 'board') this.loadBoard();
    if (view === 'dashboard') this.loadDashboard();
  },

  bindSidebar() {
    const toggle = document.getElementById('sidebar-toggle');
    toggle.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      const collapsed = sidebar.classList.toggle('collapsed');
      toggle.setAttribute('aria-expanded', String(!collapsed));
    });
  },

  // --- Permission Checks ---
  canEdit() {
    return this.currentUserRole === 'admin' || this.currentUserRole === 'editor';
  },

  canDelete() {
    return this.currentUserRole === 'admin';
  },

  enforcePermissionUI() {
    document.querySelectorAll('.btn-edit-project, .btn-edit-task, #btn-new-project, #btn-new-task').forEach(btn => {
      btn.style.display = this.canEdit() ? '' : 'none';
    });
    document.querySelectorAll('.btn-delete-project, .btn-delete-task').forEach(btn => {
      btn.style.display = this.canDelete() ? '' : 'none';
    });
  },

  // --- Projects ---
  bindProjectActions() {
    document.getElementById('btn-new-project').addEventListener('click', () => {
      if (!this.canEdit()) { Components.toast('You don\'t have permission to create projects.', 'error'); return; }
      this.showProjectForm();
    });
    document.getElementById('projects-grid').addEventListener('click', (e) => {
      const editBtn = e.target.closest('.btn-edit-project');
      const delBtn = e.target.closest('.btn-delete-project');
      if (editBtn) {
        if (!this.canEdit()) { Components.toast('Permission denied.', 'error'); return; }
        this.editProject(editBtn.dataset.id);
      }
      if (delBtn) {
        if (!this.canDelete()) { Components.toast('Only admins can delete projects.', 'error'); return; }
        this.deleteProject(delBtn.dataset.id);
      }
    });
  },

  async loadProjects() {
    const grid = document.getElementById('projects-grid');
    grid.innerHTML = '<p class="empty-state" role="status"><span class="loading"></span> Loading projects...</p>';
    try {
      this.projects = await API.listProjects();
      if (!this.projects.length) {
        grid.innerHTML = '<p class="empty-state" role="status">No projects yet. Click "New Project" to create your first team project!</p>';
        return;
      }
      grid.innerHTML = this.projects.map(p => Components.projectCard(p, this.canEdit(), this.canDelete())).join('');
      this.updateProjectSelects();
    } catch (err) {
      grid.innerHTML = '<p class="empty-state" role="status" style="color:var(--danger)">Failed to load projects. Please refresh.</p>';
      Components.toast('Failed to load projects: ' + err.message, 'error');
    }
  },

  updateProjectSelects() {
    const opts = '<option value="">— Select a project —</option>' +
      this.projects.map(p => `<option value="${p.id}">${Components.escapeHtml(p.name)}</option>`).join('');
    ['board-project-select', 'chat-project-select', 'ai-project-select'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = opts;
    });
  },

  showProjectForm(project = null) {
    const title = project ? 'Edit Project' : 'Create New Project';
    Components.showModal(title, Components.projectFormHtml(project),
      `<button class="btn btn-secondary" id="modal-cancel" type="button">Cancel</button>
       <button class="btn btn-primary" id="modal-save" type="button">${project ? 'Update' : 'Create'} Project</button>`);
    document.getElementById('modal-cancel').addEventListener('click', Components.closeModal);
    document.getElementById('modal-save').addEventListener('click', () => this.saveProject(project));
    document.getElementById('form-project-name').focus();
  },

  async saveProject(existing) {
    const name = document.getElementById('form-project-name').value.trim();
    if (!name) { Components.toast('Project name is required.', 'error'); return; }
    const data = {
      name,
      description: document.getElementById('form-project-desc').value.trim(),
      members: document.getElementById('form-project-members').value.split(',').map(m => m.trim()).filter(Boolean)
    };
    try {
      if (existing) {
        await API.updateProject(existing.id, data);
        Components.toast('Project updated successfully!', 'success');
      } else {
        await API.createProject(data);
        Components.toast('Project created successfully!', 'success');
      }
      Components.closeModal();
      await this.loadProjects();
      if (this.currentView === 'dashboard') await this.loadDashboard();
    } catch (err) { Components.toast('Error: ' + err.message, 'error'); }
  },

  async editProject(id) {
    try {
      const project = await API.getProject(id);
      this.showProjectForm(project);
    } catch (err) { Components.toast('Failed to load project details.', 'error'); }
  },

  async deleteProject(id) {
    if (!confirm('Are you sure you want to delete this project? All tasks and messages will also be deleted. This cannot be undone.')) return;
    try {
      await API.deleteProject(id);
      Components.toast('Project deleted successfully.', 'success');
      await this.loadProjects();
      if (this.currentView === 'dashboard') await this.loadDashboard();
    } catch (err) { Components.toast('Failed to delete project.', 'error'); }
  },

  // --- Dashboard ---
  async loadDashboard() {
    // Show loading states
    document.getElementById('recent-projects-list').innerHTML = '<p class="empty-state" role="status"><span class="loading"></span> Loading...</p>';
    document.getElementById('recent-tasks-list').innerHTML = '<p class="empty-state" role="status"><span class="loading"></span> Loading...</p>';

    try {
      this.projects = await API.listProjects();
      this.updateProjectSelects();
    } catch (err) {
      document.getElementById('recent-projects-list').innerHTML = '<p class="empty-state" role="status">Could not load projects.</p>';
      document.getElementById('recent-tasks-list').innerHTML = '<p class="empty-state" role="status">Could not load tasks.</p>';
      return;
    }

    // Render project stats
    document.getElementById('stat-projects-count').textContent = this.projects.length;

    // Render recent projects
    const rp = document.getElementById('recent-projects-list');
    rp.innerHTML = this.projects.length
      ? this.projects.slice(0, 5).map(p => Components.listItem(p.name, p.status || 'active')).join('')
      : '<p class="empty-state" role="status">No projects yet. Create one to get started!</p>';

    // Load tasks per project (with individual error handling)
    let totalTasks = 0, doneTasks = 0, progressTasks = 0;
    this.allTasks = [];

    const taskPromises = this.projects.slice(0, 10).map(async (p) => {
      try {
        const tasks = await API.listTasks(p.id);
        return tasks.map(t => ({ ...t, _projectName: p.name }));
      } catch (e) {
        return []; // Skip failed projects silently
      }
    });

    const results = await Promise.allSettled(taskPromises);
    results.forEach(r => {
      if (r.status === 'fulfilled' && r.value) {
        this.allTasks.push(...r.value);
      }
    });

    totalTasks = this.allTasks.length;
    doneTasks = this.allTasks.filter(t => t.status === 'done').length;
    progressTasks = this.allTasks.filter(t => t.status === 'in_progress').length;

    document.getElementById('stat-tasks-count').textContent = totalTasks;
    document.getElementById('stat-done-count').textContent = doneTasks;
    document.getElementById('stat-progress-count').textContent = progressTasks;

    const rt = document.getElementById('recent-tasks-list');
    rt.innerHTML = this.allTasks.length
      ? this.allTasks.slice(0, 8).map(t => Components.listItem(t.title, `${(t.status || 'todo').replace('_', ' ')} · ${t._projectName}`)).join('')
      : '<p class="empty-state" role="status">No tasks yet. Go to the Board to create tasks.</p>';
  },

  // --- Kanban Board ---
  bindTaskActions() {
    document.getElementById('board-project-select').addEventListener('change', (e) => {
      const pid = e.target.value;
      document.getElementById('btn-new-task').disabled = !pid;
      if (pid) this.loadBoardTasks(pid);
      else this.clearBoard();
    });
    document.getElementById('btn-new-task').addEventListener('click', () => {
      if (!this.canEdit()) { Components.toast('You don\'t have permission to create tasks.', 'error'); return; }
      const pid = document.getElementById('board-project-select').value;
      if (pid) this.showTaskForm(pid);
    });
    document.getElementById('kanban-board').addEventListener('click', (e) => {
      const editBtn = e.target.closest('.btn-edit-task');
      const delBtn = e.target.closest('.btn-delete-task');
      if (editBtn) {
        if (!this.canEdit()) { Components.toast('Permission denied.', 'error'); return; }
        this.editTask(editBtn.dataset.id);
      }
      if (delBtn) {
        if (!this.canDelete()) { Components.toast('Only admins can delete tasks.', 'error'); return; }
        this.removeTask(delBtn.dataset.id);
      }
    });
    this.initDragDrop();
  },

  clearBoard() {
    ['tasks-todo', 'tasks-in-progress', 'tasks-review', 'tasks-done'].forEach(id => {
      document.getElementById(id).innerHTML = '<p class="empty-state" style="padding:16px;font-size:12px" role="status">No tasks</p>';
    });
    ['count-todo', 'count-in-progress', 'count-review', 'count-done'].forEach(id => {
      document.getElementById(id).textContent = '0';
    });
  },

  async loadBoard() {
    const pid = document.getElementById('board-project-select').value;
    if (pid) await this.loadBoardTasks(pid);
    else this.clearBoard();
  },

  async loadBoardTasks(projectId) {
    try {
      const tasks = await API.listTasks(projectId);
      const columns = { todo: [], in_progress: [], review: [], done: [] };
      tasks.forEach(t => { if (columns[t.status]) columns[t.status].push(t); });

      Object.entries(columns).forEach(([status, items]) => {
        const colId = status === 'in_progress' ? 'tasks-in-progress' : `tasks-${status}`;
        const countId = status === 'in_progress' ? 'count-in-progress' : `count-${status}`;
        const container = document.getElementById(colId);
        container.innerHTML = items.length
          ? items.map(t => Components.taskCard(t, this.canEdit(), this.canDelete())).join('')
          : '<p class="empty-state" style="padding:16px;font-size:12px" role="status">No tasks</p>';
        document.getElementById(countId).textContent = items.length;
      });
    } catch (err) {
      Components.toast('Failed to load tasks: ' + err.message, 'error');
    }
  },

  showTaskForm(projectId, task = null) {
    const title = task ? 'Edit Task' : 'Create New Task';
    Components.showModal(title, Components.taskFormHtml(task),
      `<button class="btn btn-secondary" id="modal-cancel" type="button">Cancel</button>
       <button class="btn btn-primary" id="modal-save" type="button">${task ? 'Update' : 'Create'} Task</button>`);
    document.getElementById('modal-cancel').addEventListener('click', Components.closeModal);
    document.getElementById('modal-save').addEventListener('click', () => this.saveTask(projectId, task));
    document.getElementById('form-task-title').focus();
  },

  async saveTask(projectId, existing) {
    const title = document.getElementById('form-task-title').value.trim();
    if (!title) { Components.toast('Task title is required.', 'error'); return; }
    const data = {
      title,
      description: document.getElementById('form-task-desc').value.trim(),
      status: document.getElementById('form-task-status').value,
      priority: document.getElementById('form-task-priority').value,
      assignee: document.getElementById('form-task-assignee').value.trim(),
      due_date: document.getElementById('form-task-due').value || null,
      tags: document.getElementById('form-task-tags').value.split(',').map(t => t.trim()).filter(Boolean)
    };
    try {
      if (existing) {
        await API.updateTask(existing.id, data);
        Components.toast('Task updated successfully!', 'success');
      } else {
        await API.createTask(projectId, data);
        Components.toast('Task created successfully!', 'success');
      }
      Components.closeModal();
      await this.loadBoardTasks(projectId);
    } catch (err) { Components.toast('Failed to save task: ' + err.message, 'error'); }
  },

  async editTask(id) {
    try {
      const task = await API.request('GET', `/api/tasks/${id}`);
      const pid = document.getElementById('board-project-select').value || task.project_id;
      this.showTaskForm(pid, task);
    } catch (err) { Components.toast('Failed to load task details.', 'error'); }
  },

  async removeTask(id) {
    if (!confirm('Are you sure you want to delete this task? This cannot be undone.')) return;
    try {
      await API.deleteTask(id);
      Components.toast('Task deleted.', 'success');
      const pid = document.getElementById('board-project-select').value;
      if (pid) await this.loadBoardTasks(pid);
    } catch (err) { Components.toast('Failed to delete task.', 'error'); }
  },

  initDragDrop() {
    if (!this.canEdit()) return;
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
      col.addEventListener('dragover', (e) => { e.preventDefault(); col.style.background = 'rgba(108,92,231,0.08)'; });
      col.addEventListener('dragleave', () => { col.style.background = ''; });
      col.addEventListener('drop', async (e) => {
        e.preventDefault();
        col.style.background = '';
        const taskId = e.dataTransfer.getData('text/plain');
        const newStatus = col.closest('.kanban-column').dataset.status;
        if (!taskId) return;
        try {
          await API.updateTaskStatus(taskId, newStatus);
          Components.toast('Task moved!', 'success');
          const pid = document.getElementById('board-project-select').value;
          if (pid) await this.loadBoardTasks(pid);
        } catch (err) { Components.toast('Failed to move task.', 'error'); }
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
      else document.getElementById('chat-messages').innerHTML = '<p class="empty-state" role="status">Select a project to view the chat.</p>';
    });
    document.getElementById('btn-send-message').addEventListener('click', () => this.sendMessage());
    document.getElementById('chat-input').addEventListener('keydown', (e) => { if (e.key === 'Enter') this.sendMessage(); });
  },

  async loadMessages(projectId) {
    const container = document.getElementById('chat-messages');
    container.innerHTML = '<p class="empty-state" role="status"><span class="loading"></span> Loading messages...</p>';
    try {
      const msgs = await API.listMessages(projectId);
      container.innerHTML = msgs.length
        ? msgs.map(m => Components.chatMessage(m, this.currentUser)).join('')
        : '<p class="empty-state" role="status">No messages yet. Say hello to your team! 👋</p>';
      container.scrollTop = container.scrollHeight;
    } catch (err) { container.innerHTML = '<p class="empty-state" role="status">Failed to load messages.</p>'; }
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
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());
