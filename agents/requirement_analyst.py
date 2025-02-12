from langchain_aws import ChatBedrock
import os

class RequirementAnalyst:
    def __init__(self, bedrock_kb):
        self.bedrock_kb = bedrock_kb
        
        # Create Bedrock chat model
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
    
    def analyze_requirement(self, requirement: str) -> str:
        """
        Analyze a business requirement
        """
        # First retrieve relevant information from KB
        context, _ = self.bedrock_kb.retrieve_from_kb(requirement)
        
        # Create system prompt
        system_prompt = """You are a senior Business Analyst with extensive experience in 
        requirement gathering and analysis. You excel at understanding business needs, 
        identifying stakeholders, and defining clear requirements."""
        
        # Create task prompt
        task_prompt = f"""Analyze the following requirement:

        Requirement: {requirement}
        
        {f'Context from Knowledge Base: {context}' if context else ''}
        
        Please provide a detailed analysis covering:
        1. Business Context
           - Problem statement
           - Business objectives
           - Expected outcomes
        
        2. Stakeholder Analysis
           - Key stakeholders
           - User personas
           - Impact assessment
        
        3. Functional Requirements
           - Core functionality
           - User interactions
           - System behaviors
        
        4. Non-functional Requirements
           - Performance needs
           - Security requirements
           - Scalability considerations
        
        5. Business Value
           - Expected benefits
           - Success metrics
           - ROI considerations
        
        6. Constraints and Assumptions
           - Business constraints
           - Technical limitations
           - Dependencies
        
        Format your analysis in a clear, structured manner using Markdown."""
        
        # Execute the analysis
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_prompt}
        ]
        
        response = self.llm.invoke(messages)
        
        return response.content
