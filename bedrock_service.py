import boto3
import json
import os
from dotenv import load_dotenv
import uuid
import codecs

# Load environment variables
load_dotenv()

class BedrockService:
    def __init__(self):
        # Initialize Bedrock runtime client
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        
        # Initialize Bedrock KB client
        self.bedrock_kb = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        
        # Initialize S3 client
        self.s3 = boto3.client(
            service_name='s3',
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        
        # Load settings from environment
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        self.kb_id = os.getenv('BEDROCK_KB_ID')
        self.s3_bucket = os.getenv('S3_BUCKET')
        self.s3_prefix = os.getenv('S3_PREFIX', 'kb-documents/')
        self.max_tokens = 4096
        
        # Load default system prompt
        self.default_system_prompt = "You are a helpful AI assistant for product managers."
        
    def _invoke_model(self, messages: list, raw_request: bool = False) -> tuple:
        """
        Invoke AWS Bedrock model with the given messages
        Returns: (response_text, raw_request_json if raw_request=True else None)
        """
        try:
            # Convert messages to Claude format
            claude_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    # Add system message as a human message with special prefix
                    claude_messages.append({
                        "role": "user",
                        "content": f"[System: {msg['content']}]"
                    })
                elif msg["role"] == "user":
                    claude_messages.append({
                        "role": "user",
                        "content": msg["content"]
                    })
                elif msg["role"] == "assistant":
                    claude_messages.append({
                        "role": "assistant",
                        "content": msg["content"]
                    })
            
            request_body = {
                "messages": claude_messages,
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": 0.7
            }
            
            body = json.dumps(request_body)
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response.get('body').read())
            
            # Decode Unicode escape sequences in raw request JSON
            if raw_request:
                raw_json = json.dumps(request_body, indent=2, ensure_ascii=False)
            else:
                raw_json = None
                
            return response_body.get('content')[0].get('text'), raw_json
            
        except Exception as e:
            print(f"Error invoking Bedrock model: {str(e)}")
            return f"Error: {str(e)}", None
    
    def retrieve_from_kb(self, query: str) -> tuple:
        """
        Retrieve relevant information from Knowledge Base
        Returns: (combined_text, list of chunks with metadata)
        """
        try:
            response = self.bedrock_kb.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 3
                    }
                }
            )
            
            # Extract chunks with metadata
            chunks = []
            context_parts = []
            
            for result in response.get('retrievalResults', []):
                # Join characters into complete text for each passage
                text_parts = []
                for passage in result.get('content', {}).get('text', []):
                    if isinstance(passage, list):
                        text_parts.append(''.join(passage))
                    else:
                        text_parts.append(passage)
                
                # Create chunk with complete text
                text = ''.join(text_parts)
                
                # Extract location metadata
                location = result.get('location', {})
                s3_location = location.get('s3Location', {})
                uri = s3_location.get('uri', '')
                
                # Extract filename from S3 URI
                if uri.startswith('s3://'):
                    # Remove s3:// prefix and split by /
                    parts = uri.replace('s3://', '').split('/')
                    if len(parts) > 1:
                        # Join all parts after bucket name
                        key = '/'.join(parts[1:])
                        # Extract original filename from UUID-prefixed name
                        filename = '-'.join(key.split('-')[1:])
                    else:
                        filename = uri
                else:
                    filename = uri
                
                chunk = {
                    'location': {'uri': uri, 'filename': filename},
                    'score': result.get('score', 0),
                    'text': text
                }
                
                chunks.append(chunk)
                context_parts.append(text)
            
            return "\n\n".join(context_parts), chunks
            
        except Exception as e:
            print(f"Error retrieving from Knowledge Base: {str(e)}")
            return None, []
    
    def list_documents(self):
        """
        List all documents in the Knowledge Base
        """
        try:
            # List objects in S3
            response = self.s3.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=self.s3_prefix
            )
            
            documents = []
            for obj in response.get('Contents', []):
                # Extract original filename from the key
                key = obj['Key']
                if key != self.s3_prefix:  # Skip the prefix directory itself
                    # Remove prefix and UUID to get original filename
                    filename = '-'.join(key.replace(self.s3_prefix, '').split('-')[1:])
                    documents.append({
                        'key': key,
                        'filename': filename,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return documents
            
        except Exception as e:
            print(f"Error listing documents: {str(e)}")
            return []
    
    def delete_document(self, s3_key):
        """
        Delete a document from S3 and trigger KB sync
        """
        try:
            # Delete from S3
            self.s3.delete_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            
            # Note: The KB will automatically sync with S3 changes
            return True, "Document deleted successfully"
            
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False, f"Error deleting document: {str(e)}"
    
    def upload_to_kb(self, file_content, file_name):
        """
        Upload document to Knowledge Base via S3
        """
        try:
            # Generate a unique file name to avoid conflicts
            unique_id = str(uuid.uuid4())
            s3_key = f"{self.s3_prefix}{unique_id}-{file_name}"
            
            # Upload file to S3
            self.s3.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=file_content
            )
            
            print(f"File uploaded to S3: s3://{self.s3_bucket}/{s3_key}")
            
            # Note: The KB will automatically sync with S3 changes
            return True, "Document uploaded successfully"
            
        except Exception as e:
            print(f"Error uploading to Knowledge Base: {str(e)}")
            return False, f"Error uploading document: {str(e)}"
    
    def get_product_qa(self, question: str, conversation_history: list = None, system_prompt: str = None) -> dict:
        """
        Generate response for product-related questions using KB context and conversation history
        Returns: Dict containing response, retrieved context, and raw request
        """
        # First retrieve relevant information from KB
        context, kb_chunks = self.retrieve_from_kb(question)
        
        # Prepare messages for the conversation
        messages = []
        
        # Add system message with context if available
        if context:
            messages.append({
                "role": "system",
                "content": f"{system_prompt or self.default_system_prompt} Use this context to inform your responses:\n\n{context}"
            })
        else:
            messages.append({
                "role": "system",
                "content": system_prompt or self.default_system_prompt
            })
        
        # Add conversation history
        if conversation_history:
            # Convert conversation history to message format
            for i, msg in enumerate(conversation_history[:-1]):  # Exclude the current question
                role = "assistant" if i % 2 else "user"
                messages.append({"role": role, "content": msg})
        
        # Add the current question
        messages.append({"role": "user", "content": question})
        
        # Get response and raw request
        response, raw_request = self._invoke_model(messages, raw_request=True)
        
        return {
            'response': response,
            'kb_chunks': kb_chunks,
            'raw_request': raw_request
        }
    
    def generate_feasibility_report(self, requirement: str, system_prompt: str = None, report_template: str = None) -> dict:
        """
        Generate feasibility report for new requirements using KB context
        Returns: Dict containing report, retrieved context, and raw request
        """
        # Retrieve relevant product information from KB
        context, kb_chunks = self.retrieve_from_kb(requirement)
        
        messages = []
        
        # Add system message with context if available
        if context:
            messages.append({
                "role": "system",
                "content": f"{system_prompt or self.default_system_prompt} Use this context to inform your analysis:\n\n{context}"
            })
        else:
            messages.append({
                "role": "system",
                "content": system_prompt or self.default_system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": f"""Please analyze the following requirement and generate a comprehensive feasibility report:

Requirement: {requirement}

Generate a structured feasibility report that includes:
{report_template}

Please format the report in Markdown for better readability."""
        })
        
        # Get response and raw request
        response, raw_request = self._invoke_model(messages, raw_request=True)
        
        return {
            'response': response,
            'kb_chunks': kb_chunks,
            'raw_request': raw_request
        }
