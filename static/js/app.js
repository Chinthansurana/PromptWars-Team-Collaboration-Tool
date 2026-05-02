/**
 * TeamFlow Main Application
 */
const App = {
  currentView: 'dashboard',
  currentUser: 'Team Member',
  projects: [],
  allTasks: [],

  async init() {
    this.bindNav();
    this.bindSidebar();
    this.bindProjectActions();
    this.bindTaskActions();
    this.bindChat();
    AI.init();
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
    document.getElementById(`view-${view}`).classList.add('active');
    const titles = { dashboard: ['Dashboard', 'Overview of your team\'s activity'], projects: ['Projects', 'Manage your team projects'], board: ['Kanban Board', 'Drag tasks across workflow stages'], chat: ['Team Chat', 'Communicate with your team'], ai: ['AI Assistant', 'AI-powered collaboration tools'] };
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
    const title = project ? 'Edit Project' : 'New Project';
    const body = Components.projectFormHtml(project);
    const footer = `<button class="btn btn-secondary" id="modal-cancel">Cancel</button><button class="btn btn-primary" id="modal-save">Save</button>`;
    Components.showModal(title, body, footer);
    document.getElementById('modal-cancel').addEventListener('click', Components.closeModal);
    document.getElementById('modal-save').addEventListener('click', () => this.saveProject(project));
  },

  async saveProject(existing) {
    const name = document.getElementById('form-project-name').value.trim();
    if (!name) { Components.toast('Project name is required', 'error'); return; }
    const data = {
      name,
      description: document.getElementById('form-project-desc').value.trim(),
      members: document.getElementById('form-project-members').value.split(',').map(m => m.trim()).filter(Boolean)
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
    const title = task ? 'Edit Task' : 'New Task';
    const body = Components.taskFormHtml(task);
    const footer = '<button class="btn btn-secondary" id="modal-cancel">Cancel</button><button class="btn btn-primary" id="modal-save">Save</button>';
    Components.showModal(title, body, footer);
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
    } catch (err) { Components.toast('Failed to send message', 'error'); }
  }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => App.init());
