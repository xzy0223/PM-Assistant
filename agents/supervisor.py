from typing import Dict
from .requirement_analyst import RequirementAnalyst
from .technical_analyst import TechnicalAnalyst
from .timeline_analyst import TimelineAnalyst
from langchain_aws import ChatBedrock
import os

class FeasibilityAnalysisSupervisor:
    def __init__(self, bedrock_kb):
        self.bedrock_kb = bedrock_kb
        
        # Initialize specialist agents
        self.requirement_analyst = RequirementAnalyst(bedrock_kb)
        self.technical_analyst = TechnicalAnalyst(bedrock_kb)
        self.timeline_analyst = TimelineAnalyst(bedrock_kb)
        
        # Create Bedrock chat model
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
    
    def generate_feasibility_report(self, requirement: str) -> Dict:
        """
        Coordinate the generation of a comprehensive feasibility report
        """
        # Execute requirement analysis
        requirement_analysis = self.requirement_analyst.analyze_requirement(requirement)
        
        # Execute technical analysis with requirement analysis input
        technical_analysis = self.technical_analyst.analyze_technical_feasibility(
            requirement, 
            requirement_analysis
        )
        
        # Execute timeline analysis with both previous analyses
        timeline_analysis = self.timeline_analyst.analyze_timeline(
            requirement,
            requirement_analysis,
            technical_analysis
        )
        
        # Create system prompt
        system_prompt = """You are a senior Product Strategy Manager with extensive experience in 
        coordinating cross-functional teams and synthesizing complex analyses. You excel at 
        understanding the big picture while managing detailed technical and business analyses."""
        
        # Create task prompt
        task_prompt = f"""Create a comprehensive feasibility report synthesizing all analyses:
        
        Requirement: {requirement}
        
        Analyses to synthesize:
        1. Requirement Analysis: {requirement_analysis}
        2. Technical Analysis: {technical_analysis}
        3. Timeline Analysis: {timeline_analysis}
        
        Provide a structured report with:
        1. Executive Summary
           - Overview of requirement
           - Key findings
           - Go/No-go recommendation
        
        2. Detailed Analysis
           - Business requirements and value
           - Technical feasibility
           - Timeline and resources
        
        3. Risk Assessment
           - Business risks
           - Technical risks
           - Timeline risks
           - Mitigation strategies
        
        4. Implementation Plan
           - Recommended approach
           - Key milestones
           - Resource requirements
           - Dependencies
        
        5. Next Steps
           - Immediate actions
           - Key decisions needed
           - Critical success factors
        
        Format the report in a clear, structured manner suitable for all stakeholders.
        Use markdown formatting for better readability."""
        
        # Execute the synthesis
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_prompt}
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            'response': response.content,
            'kb_chunks': [],  # The individual agents have already used KB chunks
            'raw_request': None  # Raw requests are handled by individual agents
        }
