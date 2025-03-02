# app/services/llm/llm_service.py
from typing import Dict, Any, List
import json
import re
from openai import AsyncOpenAI

class LLMService:
    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client

    async def get_next_action(self, agent_state: Dict[str, Any]) -> Dict[str, Any]:
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

            # Format result for readability
            result = action.get('result', {})
            if isinstance(result, dict):
                result_str = json.dumps(result, indent=2)
            else:
                result_str = str(result)

            action_history += f"Result: {result_str}\n"

        prompt = f"""
        You are an AI assistant helping with CRM data analysis and document retrieval.
        
        USER QUERY: {agent_state['query']}
        
        AVAILABLE TOOLS:
        {tools_text}
        
        PREVIOUS ACTIONS:
        {action_history}
        
        Think step by step about how to best answer the user's query.
        You can use the available tools to gather information.
        
        After you have enough information, provide a final answer to the user's query.
        
        YOUR RESPONSE MUST BE IN THE FOLLOWING FORMAT:
        
        Thought: <your detailed reasoning about what to do next>
        
        Action: <either the name of a tool to use OR "final_answer">
        
        Action Input: <input to the tool OR your final answer to the user>
        """

        # Call the LLM
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        # Parse the response
        response_text = response.choices[0].message.content

        # Extract thought, action, and action input using regex
        thought_match = re.search(r"Thought: (.*?)(?=\n\nAction:|\Z)", response_text, re.DOTALL)
        action_match = re.search(r"Action: (.*?)(?=\n\nAction Input:|\Z)", response_text, re.DOTALL)
        action_input_match = re.search(r"Action Input: (.*?)(?=\Z)", response_text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else ""
        action = action_match.group(1).strip() if action_match else ""
        action_input = action_input_match.group(1).strip() if action_input_match else ""

        # Determine action type
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