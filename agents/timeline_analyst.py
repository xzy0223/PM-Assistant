from langchain_aws import ChatBedrock
from .tools import ResourceQueryTool
import os

class TimelineAnalyst:
    def __init__(self, bedrock_kb):
        self.bedrock_kb = bedrock_kb
        
        # Create Bedrock chat model
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        
        # Create resource query tool
        self.resource_tool = ResourceQueryTool()
    
    def analyze_timeline(self, requirement: str, requirement_analysis: str, technical_analysis: str) -> str:
        """
        Analyze project timeline and resource requirements
        """
        # First retrieve relevant information from KB
        context, _ = self.bedrock_kb.retrieve_from_kb(requirement)
        
        # Create system prompt
        system_prompt = """You are a senior Project Manager with extensive experience in 
        software development projects. You excel at estimating timelines, identifying 
        dependencies, and planning resource allocations.
        
        You have access to a Resource Query Tool that can help you analyze team availability.
        To use it, format your queries like this:
        - Query all developers: developers||
        - Find developers with specific skills: developers|skills|Python
        - Check team capacity: teams||
        - Find teams with specific expertise: teams|expertise|Backend
        """
        
        # First get resource information
        developers = self.resource_tool._execute("developers||")
        teams = self.resource_tool._execute("teams||")
        changes = self.resource_tool._execute("upcoming_changes||")
        
        # Create task prompt
        task_prompt = f"""Analyze the project timeline and resource requirements for:

        Requirement: {requirement}
        
        Business Analysis: {requirement_analysis}
        
        Technical Analysis: {technical_analysis}
        
        {f'Context from Knowledge Base: {context}' if context else ''}
        
        Available Resources:
        
        Developers:
        {developers}
        
        Teams:
        {teams}
        
        Upcoming Changes:
        {changes}
        
        Based on the available resources and analyses, provide a detailed timeline analysis covering:
        1. Project Phases
           - Major development phases
           - Key milestones and deliverables
           - Dependencies between phases
        
        2. Resource Requirements
           - Team composition and roles needed
           - Required skill sets
           - Resource allocation plan based on current availability
        
        3. Timeline Estimates
           - Duration for each phase
           - Critical path activities
           - Buffer/contingency time
        
        4. Risk Factors
           - Potential timeline risks
           - Resource constraints and mitigation plans
           - External dependencies
        
        5. Implementation Planning
           - Development methodology
           - Team onboarding needs
           - Knowledge transfer requirements
        
        6. Cost Implications
           - Resource costs
           - Infrastructure costs
           - Third-party service costs
        
        Format your analysis in a clear, structured manner using Markdown. Include:
        - A high-level project timeline with major milestones
        - Resource allocation plan based on current team availability
        - Recommendations for addressing any resource gaps"""
        
        # Execute the analysis
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_prompt}
        ]
        
        response = self.llm.invoke(messages)
        
        return response.content
