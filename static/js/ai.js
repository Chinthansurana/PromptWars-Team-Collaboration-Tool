/**
 * TeamFlow AI Features UI
 */
const AI = {
  currentProject: null,
  init() {
    document.getElementById('ai-project-select').addEventListener('change', (e) => {
      this.currentProject = e.target.value;
      document.querySelectorAll('.btn-ai').forEach(b => b.disabled = !this.currentProject);
    });
    document.getElementById('btn-ai-summarize').addEventListener('click', () => this.run('summarize'));
    document.getElementById('btn-ai-suggest').addEventListener('click', () => this.run('suggest'));
    document.getElementById('btn-ai-meeting').addEventListener('click', () => this.run('meeting'));
    document.getElementById('btn-ai-sentiment').addEventListener('click', () => this.run('sentiment'));
  },
  async run(feature) {
    if (!this.currentProject) { Components.toast('Select a project first', 'error'); return; }
    const panel = document.getElementById('ai-result-content');
    panel.innerHTML = '<div style="text-align:center;padding:40px"><div class="loading loading-large"></div><p style="margin-top:16px;color:var(--text-muted)">AI is thinking...</p></div>';
    try {
      let result;
      if (feature === 'summarize') { result = await API.aiSummarize(this.currentProject); panel.innerHTML = this.md(result.summary); }
      else if (feature === 'suggest') { result = await API.aiSuggest(this.currentProject); this.renderSuggestions(result.suggestions, panel); }
      else if (feature === 'meeting') { result = await API.aiMeetingNotes(this.currentProject); panel.innerHTML = this.md(result.notes); }
      else if (feature === 'sentiment') { result = await API.aiSentiment(this.currentProject); panel.innerHTML = this.md(result.analysis); }
      Components.toast('AI response generated!', 'success');
    } catch (err) {
      panel.innerHTML = '<p class="empty-state" style="color:var(--danger)">Error: ' + Components.escapeHtml(err.message) + '</p>';
      Components.toast('AI request failed', 'error');
    }
  },
  renderSuggestions(raw, panel) {
    try {
      const cleaned = raw.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      const tasks = JSON.parse(cleaned);
      let html = '<h3 style="margin-bottom:16px">Suggested Tasks</h3>';
      tasks.forEach(t => {
        html += '<div class="task-card" style="margin-bottom:10px"><div class="task-card-title">' + Components.escapeHtml(t.title) + '</div>';
        html += '<div style="font-size:13px;color:var(--text-secondary);margin:6px 0">' + Components.escapeHtml(t.description || '') + '</div>';
        html += '<span class="priority-badge priority-' + (t.priority||'medium') + '">' + (t.priority||'medium') + '</span></div>';
      });
      panel.innerHTML = html;
    } catch (e) { panel.innerHTML = this.md(raw); }
  },
  md(text) {
    if (!text) return '<p class="empty-state">No content</p>';
    return '<div class="ai-result-content">' + Components.escapeHtml(text)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^- (.*$)/gm, '<li>$1</li>')
      .replace(/\n/g, '<br>') + '</div>';
  }
};
