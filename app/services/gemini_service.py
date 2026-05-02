"""Gemini AI service.

Provides AI-powered features for team collaboration using
Google Gemini 2.0 Flash model via the google-genai SDK.
Includes task summarization, smart suggestions, meeting notes
generation, sentiment analysis, and the Genie AI chatbot.
"""

import logging
import os
from typing import Any, Optional

from google import genai

logger = logging.getLogger(__name__)

# Module-level client (lazy-initialized)
_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    """Get or create the Gemini client (singleton).

    Uses GEMINI_API_KEY environment variable for authentication.

    Returns:
        Gemini client instance.

    Raises:
        RuntimeError: If no API key is configured.
    """
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            _client = genai.Client(api_key=api_key)
        else:
            _client = genai.Client()
        logger.info("Gemini client initialized")
    return _client


def set_client(client: Any) -> None:
    """Override the Gemini client (used for testing).

    Args:
        client: Mock Gemini client.
    """
    global _client
    _client = client


def _get_model() -> str:
    """Get the configured Gemini model name.

    Returns:
        Model name string.
    """
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def _generate(prompt: str) -> str:
    """Generate content using Gemini with error handling.

    Args:
        prompt: The prompt to send to Gemini.

    Returns:
        Generated text response.
    """
    try:
        client = get_client()
        response = client.models.generate_content(
            model=_get_model(),
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error("Gemini generation error: %s", str(e))
        raise


def summarize_tasks(tasks: list[dict], project_name: str) -> str:
    """Generate a concise AI summary of project tasks.

    Args:
        tasks: List of task dictionaries.
        project_name: Name of the project.

    Returns:
        Markdown-formatted summary string.
    """
    if not tasks:
        return "No tasks found in this project yet. Create some tasks to get an AI summary!"

    task_lines = []
    for t in tasks:
        task_lines.append(
            f"- [{t.get('status', 'todo').upper()}] {t.get('title', 'Untitled')} "
            f"(Priority: {t.get('priority', 'medium')}, "
            f"Assignee: {t.get('assignee', 'Unassigned')})"
        )
    tasks_text = "\n".join(task_lines)

    prompt = (
        f'You are a project management assistant for TeamFlow. '
        f'Analyze the tasks for project "{project_name}" and provide a status report.\n\n'
        f'Tasks:\n{tasks_text}\n\n'
        f'Provide:\n'
        f'1. **Overall Progress**: Brief project status overview\n'
        f'2. **Key Metrics**: Task counts by status\n'
        f'3. **Priorities**: Critical/high-priority items\n'
        f'4. **Recommendations**: 2-3 actionable suggestions\n\n'
        f'Use markdown formatting. Be concise and professional.'
    )

    try:
        return _generate(prompt)
    except Exception as e:
        return f"AI summary temporarily unavailable. Error: {str(e)}"


def suggest_tasks(project_name: str, project_description: str) -> str:
    """Generate AI-suggested tasks for a project.

    Args:
        project_name: Name of the project.
        project_description: Description of the project.

    Returns:
        JSON-formatted string of suggested tasks.
    """
    prompt = (
        f'You are a project planning assistant. Suggest 5-8 actionable tasks.\n\n'
        f'Project: {project_name}\nDescription: {project_description}\n\n'
        f'For each task provide: title, description, priority (low/medium/high/critical), tags.\n'
        f'Respond with ONLY a valid JSON array. Example:\n'
        f'[{{"title": "Setup repo", "description": "Init git", "priority": "high", "tags": ["setup"]}}]'
    )

    try:
        return _generate(prompt)
    except Exception as e:
        return f"AI suggestions temporarily unavailable. Error: {str(e)}"


def generate_meeting_notes(messages: list[dict], project_name: str) -> str:
    """Generate structured meeting notes from recent messages.

    Args:
        messages: List of message dictionaries.
        project_name: Name of the project.

    Returns:
        Markdown-formatted meeting notes.
    """
    if not messages:
        return "No messages found. Start a conversation to generate meeting notes!"

    msg_lines = [f"[{m.get('sender', 'Unknown')}]: {m.get('content', '')}" for m in messages]
    conversation = "\n".join(msg_lines)

    prompt = (
        f'Generate structured meeting notes for project "{project_name}".\n\n'
        f'Conversation:\n{conversation}\n\n'
        f'Include: Summary, Key Decisions, Action Items, Open Questions, Next Steps.\n'
        f'Use markdown formatting.'
    )

    try:
        return _generate(prompt)
    except Exception as e:
        return f"AI meeting notes temporarily unavailable. Error: {str(e)}"


def analyze_sentiment(messages: list[dict]) -> str:
    """Analyze team sentiment from recent messages.

    Args:
        messages: List of message dictionaries.

    Returns:
        Markdown-formatted sentiment analysis.
    """
    if not messages:
        return "No messages to analyze. Start a conversation to check team sentiment!"

    msg_lines = [
        f"[{m.get('sender', 'Unknown')}]: {m.get('content', '')}"
        for m in messages if m.get("msg_type") == "chat"
    ]
    if not msg_lines:
        return "No chat messages to analyze."

    prompt = (
        f'Analyze team sentiment from this conversation:\n\n'
        f'{chr(10).join(msg_lines)}\n\n'
        f'Provide: Sentiment Score (1-10), Morale Assessment, '
        f'Communication Style, Concerns, Positive Signals, Recommendations.\n'
        f'Use markdown. Be constructive.'
    )

    try:
        return _generate(prompt)
    except Exception as e:
        return f"AI sentiment analysis temporarily unavailable. Error: {str(e)}"


def genie_chat(
    user_message: str,
    project: dict,
    tasks: list[dict],
    messages: list[dict],
) -> str:
    """Genie AI Chatbot — context-aware team collaboration assistant.

    Genie understands the project context and helps the team
    with coordination, task management, and communication.

    Args:
        user_message: The user's message to Genie.
        project: Current project dictionary.
        tasks: List of task dictionaries for context.
        messages: List of recent message dictionaries.

    Returns:
        Genie's response text.
    """
    # Build context summary
    task_summary = "No tasks yet."
    if tasks:
        status_counts: dict[str, int] = {}
        for t in tasks:
            s = t.get("status", "todo")
            status_counts[s] = status_counts.get(s, 0) + 1
        task_lines = [f"  {k}: {v}" for k, v in status_counts.items()]
        task_summary = f"Total: {len(tasks)}\n" + "\n".join(task_lines)

    recent_msgs = ""
    if messages:
        last_5 = messages[-5:]
        recent_msgs = "\n".join(
            f"  [{m.get('sender', '?')}]: {m.get('content', '')}"
            for m in last_5
        )

    members = ", ".join(project.get("members", [])) or "No members listed"

    prompt = (
        f'You are Genie, a friendly and helpful AI assistant built into TeamFlow, '
        f'a team collaboration platform. You help teams coordinate better, '
        f'manage tasks, and communicate effectively.\n\n'
        f'Current Project: {project.get("name", "Unknown")}\n'
        f'Description: {project.get("description", "N/A")}\n'
        f'Members: {members}\n'
        f'Task Status:\n{task_summary}\n'
        f'Recent Messages:\n{recent_msgs or "  No recent messages"}\n\n'
        f'User says: {user_message}\n\n'
        f'Respond helpfully and concisely. If asked about tasks, reference the '
        f'actual task data. Suggest actionable steps when appropriate. '
        f'Keep responses under 300 words. Use markdown for formatting.'
    )

    try:
        return _generate(prompt)
    except Exception as e:
        return f"Genie is temporarily unavailable. Error: {str(e)}"
