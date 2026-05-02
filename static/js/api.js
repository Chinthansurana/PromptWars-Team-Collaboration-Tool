/**
 * TeamFlow API Client
 * Handles all HTTP requests to the Flask backend.
 */
const API = {
  baseUrl: '',

  async request(method, path, body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${this.baseUrl}${path}`, opts);
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || `Request failed (${res.status})`);
    return json.data !== undefined ? json.data : json;
  },

  // Projects
  listProjects() { return this.request('GET', '/api/projects'); },
  getProject(id) { return this.request('GET', `/api/projects/${id}`); },
  createProject(data) { return this.request('POST', '/api/projects', data); },
  updateProject(id, data) { return this.request('PUT', `/api/projects/${id}`, data); },
  deleteProject(id) { return this.request('DELETE', `/api/projects/${id}`); },

  // Tasks
  listTasks(projectId) { return this.request('GET', `/api/projects/${projectId}/tasks`); },
  createTask(projectId, data) { return this.request('POST', `/api/projects/${projectId}/tasks`, data); },
  updateTask(id, data) { return this.request('PUT', `/api/tasks/${id}`, data); },
  updateTaskStatus(id, status) { return this.request('PATCH', `/api/tasks/${id}/status`, { status }); },
  deleteTask(id) { return this.request('DELETE', `/api/tasks/${id}`); },

  // Messages
  listMessages(projectId, limit = 50) { return this.request('GET', `/api/projects/${projectId}/messages?limit=${limit}`); },
  sendMessage(projectId, data) { return this.request('POST', `/api/projects/${projectId}/messages`, data); },

  // Users
  listUsers() { return this.request('GET', '/api/users'); },
  getUser(id) { return this.request('GET', `/api/users/${id}`); },
  createUser(data) { return this.request('POST', '/api/users', data); },
  updateUser(id, data) { return this.request('PUT', `/api/users/${id}`, data); },
  deleteUser(id) { return this.request('DELETE', `/api/users/${id}`); },

  // AI
  aiSummarize(projectId) { return this.request('POST', '/api/ai/summarize', { project_id: projectId }); },
  aiSuggest(projectId) { return this.request('POST', '/api/ai/suggest-tasks', { project_id: projectId }); },
  aiMeetingNotes(projectId) { return this.request('POST', '/api/ai/meeting-notes', { project_id: projectId }); },
  aiSentiment(projectId) { return this.request('POST', '/api/ai/sentiment', { project_id: projectId }); },
};
