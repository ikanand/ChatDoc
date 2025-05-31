import os
import json
from typing import List
from langchain.schema import BaseMessage, messages_to_dict, messages_from_dict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.schema import AIMessage, HumanMessage

CONV_DIR = './conversation_logs'

# --- Conversation File Storage Class ---
class FilePerConversationMessageHistory(BaseChatMessageHistory):
    def __init__(self, conv_id: str):
        self.conv_id = conv_id
        self.file_path = os.path.join(CONV_DIR, f"{conv_id}.json")
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                data = json.load(f)
                try:
                    self.messages: List[BaseMessage] = messages_from_dict(data.get("messages", []))
                except ValueError as e:
                    raise ValueError(f"Error loading messages: {e}")
        else:
            self.messages: List[BaseMessage] = []
            self._save()

    def _save(self):
        with open(self.file_path, "w") as f:
            json.dump({"messages": messages_to_dict(self.messages)}, f, indent=2)

    def add_message(self, message: BaseMessage) -> None:
        if isinstance(message, dict):
            try:
                message = BaseMessage(**message)  # Convert dictionary to BaseMessage
            except Exception as e:
                raise ValueError(f"Invalid message format: {e}")


    def add_message_without_context(self, message: BaseMessage) -> None:
        if isinstance(message, dict):
            try:
                message = BaseMessage(**message)  # Convert dictionary to BaseMessage
            except Exception as e:
                raise ValueError(f"Invalid message format: {e}")
        if isinstance(message, (HumanMessage, AIMessage)):
            self.messages.append(message)
            self._save()
        else:
            print(f"Skipped storing non-user/AI message: {message}")

    

    def clear(self):
        self.messages = []
        self._save()

    def get_last_n(self, n=5):
        return self.messages[-n:]
    
    def load_messages(self) -> List[dict]:
        return [{"type": "human" if isinstance(msg, HumanMessage) else "ai", "content": msg.content} for msg in self.messages]

