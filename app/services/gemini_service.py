"""Gemini AI service.

Provides AI-powered features for team collaboration using
Google Gemini 2.0 Flash model via the google-genai SDK.
"""

import logging
import os
from typing import Optional

from google import genai

logger = logging.getLogger(__name__)

# Module-level client (lazy-initialized)
_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    """Get or create the Gemini client (singleton).

    Uses GEMINI_API_KEY environment variable for authentication.
    Falls back to Application Default Credentials on Cloud Run.

    Returns:
        Gemini client instance.
    """
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            _client = genai.Client(api_key=api_key)
        else:
            # Use Application Default Credentials (ADC) on Cloud Run
            _client = genai.Client()
        logger.info("Gemini client initialized")
    return _client


def set_client(client) -> None:
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
    return os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


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

    task_descriptions = []
    for t in tasks:
        task_descriptions.append(
            f"- [{t.get('status', 'todo').upper()}] {t.get('title', 'Untitled')} "
            f"(Priority: {t.get('priority', 'medium')}, "
            f"Assignee: {t.get('assignee', 'Unassigned')})"
        )
    tasks_text = "\n".join(task_descriptions)

    prompt = f"""You are a project management assistant. Analyze the following tasks for the project "{project_name}" and provide a concise status report.

Tasks:
{tasks_text}

Please provide:
1. **Overall Progress**: A brief overview of the project status
2. **Key Metrics**: Count of tasks by status (todo, in progress, review, done)
3. **Priorities**: Highlight any critical or high-priority items
4. **Recommendations**: 2-3 actionable suggestions for the team

Keep the response concise, professional, and actionable. Use markdown formatting."""

    try:
        client = get_client()
        response = client.models.generate_content(
            model=_get_model(),
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error("Gemini summarize error: %s", str(e))
        return f"AI summary temporarily unavailable. Error: {str(e)}"


def suggest_tasks(project_name: str, project_description: str) -> str:
    """Generate AI-suggested tasks for a project.

    Args:
        project_name: Name of the project.
        project_description: Description of the project.

    Returns:
        JSON-formatted string of suggested tasks.
    """
    prompt = f"""You are a project planning assistant. Based on the following project, suggest 5-8 actionable tasks to get started.

Project: {project_name}
Description: {project_description}

For each task, provide:
- title: A clear, concise task title
- description: A brief description of what needs to be done
- priority: One of "low", "medium", "high", "critical"
- tags: Relevant tags as a list

Respond with ONLY a valid JSON array of task objects. Example format:
[
  {{"title": "Set up project repository", "description": "Initialize git repo with README and .gitignore", "priority": "high", "tags": ["setup", "infrastructure"]}}
]"""

    try:
        client = get_client()
        response = client.models.generate_content(
            model=_get_model(),
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error("Gemini suggest error: %s", str(e))
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

    message_text = []
    for m in messages:
        message_text.append(f"[{m.get('sender', 'Unknown')}]: {m.get('content', '')}")
    conversation = "\n".join(message_text)

    prompt = f"""You are a meeting notes assistant. Based on the following team conversation from the project "{project_name}", generate structured meeting notes.

Conversation:
{conversation}

Please provide:
1. **Meeting Summary**: A brief overview of what was discussed
2. **Key Decisions**: Any decisions that were made
3. **Action Items**: Specific tasks that need to be done, with owners if mentioned
4. **Open Questions**: Any unresolved questions or topics
5. **Next Steps**: Suggested next steps for the team

Use markdown formatting. Keep it professional and concise."""

    try:
        client = get_client()
        response = client.models.generate_content(
            model=_get_model(),
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error("Gemini meeting notes error: %s", str(e))
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

    message_text = []
    for m in messages:
        if m.get("msg_type") == "chat":
            message_text.append(f"[{m.get('sender', 'Unknown')}]: {m.get('content', '')}")
    conversation = "\n".join(message_text)

    if not conversation.strip():
        return "No chat messages to analyze."

    prompt = f"""You are a team dynamics analyst. Analyze the sentiment and morale of the following team conversation.

Conversation:
{conversation}

Please provide:
1. **Overall Sentiment Score**: Rate from 1-10 (1=very negative, 10=very positive)
2. **Team Morale**: Brief assessment of team morale
3. **Communication Style**: Observations about how the team communicates
4. **Potential Concerns**: Any signs of frustration, confusion, or conflict
5. **Positive Signals**: Any signs of enthusiasm, collaboration, or progress
6. **Recommendations**: 2-3 suggestions to improve team dynamics

Use markdown formatting. Be constructive and supportive in your analysis."""

    try:
        client = get_client()
        response = client.models.generate_content(
            model=_get_model(),
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error("Gemini sentiment error: %s", str(e))
        return f"AI sentiment analysis temporarily unavailable. Error: {str(e)}"
