import time
import logging

from src.agent.core import create_telegram_agent
from src.database.checkpointer import get_checkpointer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AgentService:
    """Service for managing LangChain agent lifecycle."""

    def __init__(self):
        self.agent = None
        self.checkpointer = None

    async def initialize(self):
        """Initialize agent and checkpointer."""
        try:
            logger.info("Initializing checkpointer...")
            self.checkpointer = get_checkpointer()

            logger.info("Initializing agent...")
         
            self.agent = create_telegram_agent(checkpointer=self.checkpointer)

            logger.info("✅ Agent service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent service: {e}")
            raise

    async def process_message(self, user_id: int, message: str) -> str:
        """Process user message with the LangChain agent asynchronously with detailed timers."""
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        t_start = time.perf_counter()
        try:
            logger.info(f"⏱️ [AGENT START] Processing message for user {user_id}: {message[:50]}...")

            agent_input = {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            }

            thread_config = {
                "configurable": {
                    "thread_id": str(user_id)
                }
            }

            
            t_llm_start = time.perf_counter()
            response = await self.agent.ainvoke(
                agent_input,
                config=thread_config,
            )
            logger.info(f"⏱️ [LANGGRAPH AINVOKE] Execution took: {time.perf_counter() - t_llm_start:.3f} sec")

            
            t_ext_start = time.perf_counter()
            agent_response = self._extract_response(response)
            logger.info(f"⏱️ [EXTRACT RESPONSE] Extraction took: {time.perf_counter() - t_ext_start:.3f} sec")

            logger.info(f"⏱️ [AGENT TOTAL TIME] Total agent processing time: {time.perf_counter() - t_start:.3f} sec")
            return agent_response

        except Exception as e:
            logger.error(f"❌ Agent processing error: {e}", exc_info=True)
            raise

    @staticmethod
    def _extract_response(response: dict) -> str:
        try:
            if "messages" in response and len(response["messages"]) > 0:
                last_message = response["messages"][-1]

                
                content = getattr(last_message, "content", None)
                if content is None and isinstance(last_message, dict):
                    content = last_message.get("content")

                
                if isinstance(content, str):
                    return content

                
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            text_parts.append(block)
                    if text_parts:
                        return "".join(text_parts)

                return str(content if content is not None else last_message)

            return str(response)

        except Exception as e:
            logger.error(f"Failed to extract response: {e}")
            return "I couldn't process your message. Please try again."

    async def is_ready(self) -> bool:
        return self.agent is not None and self.checkpointer is not None