# app/services/llm/llm_service.py
from typing import Dict, Any, List
import json
import re
from openai import AsyncOpenAI

from app.services.llm.prompts.prompts import REACT_AGENT_SYSTEM_PROMPT


class LLMService:
    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client

    async def get_next_action(
            self,
            agent_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get the next action from the LLM based on the agent state
        This implements the ReAct pattern (Reasoning + Acting)
        """

        # Build prompt with available tools
        tools_text = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in agent_state["tools"]
        ])

        # Include past actions and results
        action_history = ""
        for i, action in enumerate(agent_state.get("actions", [])):
            action_history += f"\nStep {i+1}:\n"
            action_history += f"Tool: {action.get('tool')}\n"
            action_history += f"Input: {action.get('input')}\n"

            result = action.get('result', {})
            if isinstance(result, dict):
                result_str = json.dumps(result, indent=2)
            else:
                result_str = str(result)

            action_history += f"Result: {result_str}\n"

        prompt = REACT_AGENT_SYSTEM_PROMPT.format(
            agent_state=agent_state['query'],
            tools_text=tools_text,
            action_history=action_history
        )

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        response_text = response.choices[0].message.content

        # Extract thought, action, and action input using regex
        thought_match = re.search(r"Thought: (.*?)(?=\n\nAction:|\Z)", response_text, re.DOTALL)
        action_match = re.search(r"Action: (.*?)(?=\n\nAction Input:|\Z)", response_text, re.DOTALL)
        action_input_match = re.search(r"Action Input: (.*?)(?=\Z)", response_text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else ""
        action = action_match.group(1).strip() if action_match else ""
        action_input = action_input_match.group(1).strip() if action_input_match else ""

        if action.lower() == "final_answer":
            action_type = "final_answer"
            tool_name = ""
        else:
            action_type = "tool"
            tool_name = action

        return {
            "thought": thought,
            "action_type": action_type,
            "tool_name": tool_name,
            "action_input": action_input
        }