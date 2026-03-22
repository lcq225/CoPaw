# -*- coding: utf-8 -*-
"""Context recovery utilities for memory compaction.

This module provides functionality to extract recent conversations and
pending tasks from session files after memory compaction, enhancing
context continuity.
"""
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


class ContextRecoveryConfig:
    """Configuration for context recovery."""
    
    def __init__(
        self,
        enabled: bool = True,
        recent_n: int = 5,
        show_pending_tasks: bool = True,
        max_task_length: int = 100,
    ):
        self.enabled = enabled
        self.recent_n = recent_n
        self.show_pending_tasks = show_pending_tasks
        self.max_task_length = max_task_length


class ContextRecovery:
    """Extract and format context for recovery after compaction."""
    
    # Task patterns to identify user requests
    TASK_PATTERNS = [
        r'帮我(.+)',
        r'请(.+)',
        r'需要(.+)',
        r'处理(.+)',
        r'分析(.+)',
        r'整理(.+)',
        r'写(.+)',
        r'生成(.+)',
        r'检查(.+)',
        r'搜索(.+)',
    ]
    
    # Completion indicators
    COMPLETION_KEYWORDS = ['完成', '好了', '搞定', '已处理', '✅', '已完成']
    
    def __init__(
        self,
        workspace_dir: str,
        session_id: str,
        config: Optional[ContextRecoveryConfig] = None,
    ):
        """
        Args:
            workspace_dir: CoPaw workspace directory
            session_id: Current session identifier
            config: Recovery configuration
        """
        self.workspace_dir = Path(workspace_dir)
        self.session_id = session_id
        self.config = config or ContextRecoveryConfig()
        self.sessions_dir = self.workspace_dir / "sessions"
    
    def find_session_file(self) -> Optional[Path]:
        """Find the session file for current session."""
        if not self.sessions_dir.exists():
            logger.debug(f"Sessions directory not found: {self.sessions_dir}")
            return None
        
        # Try different matching patterns
        patterns = [
            f"*{self.session_id}*.json",
            f"{self.session_id}.json",
        ]
        
        for pattern in patterns:
            matches = list(self.sessions_dir.glob(pattern))
            if matches:
                # Return most recently modified
                return sorted(matches, key=lambda x: x.stat().st_mtime, reverse=True)[0]
        
        logger.debug(f"No session file found for: {self.session_id}")
        return None
    
    def load_messages(self) -> List[dict]:
        """Load messages from session file."""
        session_file = self.find_session_file()
        if not session_file:
            return []
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            messages = self._extract_messages_from_data(data)
            logger.debug(f"Loaded {len(messages)} messages from {session_file.name}")
            return messages
            
        except Exception as e:
            logger.warning(f"Failed to load session file: {e}")
            return []
    
    def _extract_messages_from_data(self, data: dict) -> List[dict]:
        """Extract message list from session data structure."""
        messages = []
        
        # Structure 1: data['agent']['memory']['content']
        if 'agent' in data:
            memory = data['agent'].get('memory', {})
            content = memory.get('content', [])
            for item in content:
                if isinstance(item, list) and len(item) > 0:
                    msg = item[0]
                    if isinstance(msg, dict) and 'role' in msg:
                        messages.append(msg)
                elif isinstance(item, dict) and 'role' in item:
                    messages.append(item)
        
        # Filter to user and assistant messages only
        return [m for m in messages if m.get('role') in ('user', 'assistant')]
    
    def _extract_text(self, content) -> str:
        """Extract text from content field."""
        if isinstance(content, str):
            return content
        
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    parts.append(block.get('text', ''))
            return '\n'.join(parts)
        
        return str(content)
    
    def get_recent_qa_pairs(self, messages: List[dict], n: int) -> List[Tuple[dict, dict]]:
        """Get the most recent N question-answer pairs."""
        qa_pairs = []
        i = len(messages) - 1
        
        while i >= 0 and len(qa_pairs) < n:
            msg = messages[i]
            if msg.get('role') == 'assistant':
                # Find preceding user message
                j = i - 1
                while j >= 0:
                    if messages[j].get('role') == 'user':
                        qa_pairs.insert(0, (messages[j], msg))
                        i = j - 1
                        break
                    j -= 1
                else:
                    i -= 1
            else:
                i -= 1
        
        return qa_pairs
    
    def extract_pending_tasks(self, messages: List[dict]) -> List[dict]:
        """Identify pending/incomplete tasks from recent messages."""
        if not self.config.show_pending_tasks:
            return []
        
        tasks = []
        qa_pairs = self.get_recent_qa_pairs(messages, self.config.recent_n)
        
        for user_msg, assistant_msg in qa_pairs:
            content = self._extract_text(user_msg.get('content', ''))
            
            # Check for task patterns
            for pattern in self.TASK_PATTERNS:
                match = re.search(pattern, content)
                if match:
                    task_text = match.group(1).strip()
                    if len(task_text) > 5:
                        # Check if completed in assistant response
                        assistant_text = self._extract_text(assistant_msg.get('content', ''))
                        is_completed = any(kw in assistant_text for kw in self.COMPLETION_KEYWORDS)
                        
                        if not is_completed:
                            tasks.append({
                                'task': task_text[:self.config.max_task_length],
                                'timestamp': user_msg.get('timestamp', ''),
                                'original': content[:200]
                            })
                    break
        
        return tasks[-3:]  # Keep last 3 pending tasks
    
    def format_for_summary(self) -> str:
        """Format recent context for injection into compressed summary."""
        messages = self.load_messages()
        if not messages:
            return ""
        
        qa_pairs = self.get_recent_qa_pairs(messages, self.config.recent_n)
        if not qa_pairs:
            return ""
        
        lines = ["\n[上下文恢复 - 最近对话]"]
        
        for user_msg, assistant_msg in qa_pairs:
            user_text = self._extract_text(user_msg.get('content', ''))
            if len(user_text) > 200:
                user_text = user_text[:200] + "..."
            lines.append(f"用户: {user_text}")
            
            assistant_text = self._extract_text(assistant_msg.get('content', ''))
            if len(assistant_text) > 300:
                assistant_text = assistant_text[:300] + "..."
            lines.append(f"助手: {assistant_text}")
            lines.append("")
        
        # Add pending tasks
        pending = self.extract_pending_tasks(messages)
        if pending:
            lines.append("[待处理任务]")
            for i, task in enumerate(pending, 1):
                lines.append(f"{i}. {task['task']}")
        
        return '\n'.join(lines)
    
    def format_for_user(self) -> str:
        """Format recovery info for display to user."""
        messages = self.load_messages()
        if not messages:
            return ""
        
        qa_pairs = self.get_recent_qa_pairs(messages, self.config.recent_n)
        pending = self.extract_pending_tasks(messages)
        
        lines = [
            "📋 **上下文恢复摘要**",
            f"- 保留最近 {len(qa_pairs)} 组对话",
            f"- 时间: {datetime.now().strftime('%H:%M:%S')}"
        ]
        
        if pending:
            lines.append(f"- 待处理任务: {len(pending)} 项")
            lines.append("")
            lines.append("**待处理:**")
            for i, task in enumerate(pending, 1):
                lines.append(f"  {i}. {task['task']}")
        
        return '\n'.join(lines)


def enhance_compressed_summary(
    workspace_dir: str,
    session_id: str,
    original_summary: str,
    config: Optional[ContextRecoveryConfig] = None,
) -> str:
    """
    Enhance compressed summary with recent context.
    
    Args:
        workspace_dir: CoPaw workspace directory
        session_id: Current session identifier
        original_summary: Original compressed summary from LLM
        config: Recovery configuration
    
    Returns:
        Enhanced summary with recent context appended
    """
    recovery = ContextRecovery(
        workspace_dir=workspace_dir,
        session_id=session_id,
        config=config,
    )
    
    context = recovery.format_for_summary()
    
    if context:
        return f"{original_summary}\n{context}"
    
    return original_summary


def get_recovery_message(
    workspace_dir: str,
    session_id: str,
    config: Optional[ContextRecoveryConfig] = None,
) -> str:
    """
    Get user-facing recovery message after compaction.
    
    Args:
        workspace_dir: CoPaw workspace directory
        session_id: Current session identifier
        config: Recovery configuration
    
    Returns:
        Formatted message for user display
    """
    recovery = ContextRecovery(
        workspace_dir=workspace_dir,
        session_id=session_id,
        config=config,
    )
    
    return recovery.format_for_user()