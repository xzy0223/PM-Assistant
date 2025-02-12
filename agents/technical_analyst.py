from langchain_aws import ChatBedrock
from .tools import ResourceQueryTool
import os

class TechnicalAnalyst:
    def __init__(self, bedrock_kb):
        self.bedrock_kb = bedrock_kb
        
        # Create Bedrock chat model
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        
        # Create GitHub search tool for the specific repository
        self.github_tool = ResourceQueryTool()
    
    def analyze_technical_feasibility(self, requirement: str, requirement_analysis: str) -> str:
        """
        Analyze technical feasibility of a requirement
        """
        # First retrieve relevant information from KB
        context, _ = self.bedrock_kb.retrieve_from_kb(requirement)
        
        # Create system prompt
        system_prompt = """You are a senior Technical Architect with extensive experience in 
        software architecture and system design. You excel at evaluating technical 
        requirements, analyzing codebases, and designing scalable solutions.
        
        You have access to a Resource Query Tool that can help you analyze the codebase.
        To use it, format your queries like this:
        - Query all developers: developers||
        - Find developers with specific skills: developers|skills|Python
        - Check team capacity: teams||
        - Find teams with specific expertise: teams|expertise|Backend
        """
        
        # Create task prompt
        task_prompt = f"""Analyze the technical feasibility of the following requirement:

        Requirement: {requirement}
        
        Business Analysis: {requirement_analysis}
        
        {f'Context from Knowledge Base: {context}' if context else ''}
        
        First, use the Resource Query Tool to analyze the codebase. Here are some suggested queries:
        1. developers|| (to see all available developers)
        2. teams|| (to check team capacities)
        3. upcoming_changes|| (to see planned resource changes)
        
        Then provide a detailed technical analysis covering:
        1. Technical Approach
           - Proposed architecture/design
           - Technology stack recommendations
           - Integration points and interfaces
        
        2. Technical Complexity
           - Implementation challenges
           - Technical dependencies
           - Required expertise/skills
        
        3. Infrastructure Requirements
           - Hosting/deployment needs
           - Scalability considerations
           - Performance requirements
        
        4. Technical Risks
           - Security considerations
           - Technical debt implications
           - Potential bottlenecks
        
        5. Implementation Strategy
           - Development approach
           - Testing requirements
           - Deployment considerations
        
        6. Code Analysis Insights
           - Current codebase structure
           - Potential impact areas
           - Refactoring needs
        
        Format your analysis in a clear, structured manner using Markdown."""
        
        # First get resource information
        developers = self.github_tool._execute("developers||")
        teams = self.github_tool._execute("teams||")
        changes = self.github_tool._execute("upcoming_changes||")
        
        # Add resource information to the prompt
        task_prompt += f"""

        Available Resources:
        
        Developers:
        {developers}
        
        Teams:
        {teams}
        
        Upcoming Changes:
        {changes}
        """
        
        # Execute the analysis
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_prompt}
        ]
        
        response = self.llm.invoke(messages)
        
        return response.content
