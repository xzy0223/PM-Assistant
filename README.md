# Product Manager Assistant

An AI-powered assistant for product managers that leverages AWS Bedrock for intelligent product knowledge management and requirement analysis.

## ⚠️ Important Note

This application requires Python 3.8 or later. AWS SDK (boto3) will no longer support Python 3.7 after December 13, 2023.

## Features

1. **Product Knowledge Q&A**
   - Interactive Q&A system based on existing product documentation
   - Utilizes AWS Bedrock Knowledge Base for accurate responses
   - Context-aware answers from your product documentation

2. **Feasibility Report Generator**
   - Generate comprehensive feasibility reports for new requirements
   - Multi-agent system with specialized analysts:
     - Requirement Analyst: Business and stakeholder analysis
     - Technical Analyst: Technical feasibility and architecture
     - Timeline Analyst: Project planning and resource allocation
     - Supervisor: Coordination and final synthesis
   - Resource management with real-time team availability tracking
   - Analyzes technical feasibility, resources, risks, and timeline
   - Leverages existing product knowledge for context-aware analysis

3. **Document Upload**
   - Upload product documentation to the knowledge base
   - Supports text and markdown files
   - Automatically indexes content for Q&A and report generation

## Architecture

### Agent-Based System

The application uses a multi-agent architecture for comprehensive feasibility analysis:

1. **Requirement Analyst**
   - Analyzes business requirements and stakeholder needs
   - Identifies key objectives and success metrics
   - Evaluates business value and constraints

2. **Technical Analyst**
   - Assesses technical feasibility and architecture
   - Analyzes codebase and technical dependencies
   - Provides implementation recommendations
   - Integrates with GitHub for code analysis

3. **Timeline Analyst**
   - Plans project timelines and resource allocation
   - Uses real-time resource availability data
   - Estimates costs and identifies critical paths
   - Manages team capacity and skills matching

4. **Feasibility Analysis Supervisor**
   - Coordinates between specialist agents
   - Synthesizes analyses into final reports
   - Provides executive summaries and recommendations

### Resource Management

The system includes a built-in resource management tool that tracks:
- Developer availability and skills
- Team capacity and expertise
- Upcoming resource changes
- Project allocations and timelines

## Prerequisites

1. **AWS Account Setup**
   - Active AWS account with Bedrock access
   - AWS Bedrock Knowledge Base created and configured
   - IAM user with appropriate permissions for Bedrock services

2. **Local Environment**
   - Python 3.8 or higher (Required)
   - pip package manager

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd pm_assistant
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   - Copy the environment template:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your AWS credentials and Bedrock settings:
     ```
     AWS_REGION=your_region
     AWS_ACCESS_KEY_ID=your_access_key
     AWS_SECRET_ACCESS_KEY=your_secret_key
     BEDROCK_MODEL_ID=anthropic.claude-v2
     BEDROCK_KB_ID=your_knowledge_base_id
     ```

## Usage

1. **Starting the Application**
   ```bash
   streamlit run app.py
   ```
   The application will be available at `http://localhost:8501`

2. **Using Product Knowledge Q&A**
   - Select "Product Knowledge Q&A" from the sidebar
   - Enter your question about the product
   - Click "Get Answer" to receive AI-generated responses based on your knowledge base

3. **Generating Feasibility Reports**
   - Select "Feasibility Report Generator" from the sidebar
   - Enter the requirement details in the text area
   - The system will:
     1. Analyze business requirements
     2. Assess technical feasibility
     3. Plan timeline and resources
     4. Generate comprehensive report
   - Real-time status updates show progress of each analysis phase
   - Final report includes executive summary and detailed recommendations

4. **Uploading Documents**
   - Select "Document Upload" from the sidebar
   - Choose a supported file (txt, md)
   - Click "Upload to Knowledge Base" to add the document
   - Wait for confirmation of successful upload

## AWS Bedrock Setup

1. **Create a Knowledge Base**
   - Go to AWS Bedrock Console
   - Navigate to Knowledge Bases
   - Click "Create Knowledge Base"
   - Follow the setup wizard
   - Copy the Knowledge Base ID to your `.env` file

2. **Required IAM Permissions**
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "bedrock:InvokeModel",
                   "bedrock-agent:Retrieve",
                   "bedrock-agent:CreateDataSource"
               ],
               "Resource": "*"
           }
       ]
   }
   ```

## Troubleshooting

1. **Connection Issues**
   - Verify AWS credentials in `.env`
   - Check AWS region configuration
   - Ensure IAM user has required permissions

2. **Upload Errors**
   - Verify file format is supported
   - Check file encoding (UTF-8 required)
   - Ensure Knowledge Base ID is correct

3. **Response Issues**
   - Verify Knowledge Base has indexed content
   - Check query relevance to uploaded content
   - Ensure Bedrock model ID is correct

## Limitations

- Currently supports only text and markdown files
- PDF support planned for future release
- Maximum file size limit based on AWS Bedrock constraints
- Response time may vary based on query complexity

## Security Notes

- Store AWS credentials securely
- Never commit `.env` file to version control
- Regularly rotate AWS access keys
- Monitor AWS usage and costs

## Future Enhancements

- PDF document support
- Batch upload capability
- Enhanced search algorithms
- Custom report templates
- Integration with project management tools
- Real-time resource management dashboard
- Advanced team capacity planning
- Integration with more version control systems

## Support

For issues and feature requests, please:
1. Check the troubleshooting guide
2. Review AWS Bedrock documentation
3. Submit detailed bug reports with steps to reproduce
