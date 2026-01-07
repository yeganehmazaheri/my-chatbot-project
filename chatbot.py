import requests
import json
from sseclient import SSEClient
import logging

logging.basicConfig(filename='chatbot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentChatbot:
    def __init__(self, api_key, document_retriever):
        self.api_key = api_key
        self.document_retriever = document_retriever
        self.api_url = "https://api.z.ai/api/paas/v4/chat/completions"
        
    def _create_system_prompt(self, relevant_sections, session):
        """Create an optimized system prompt with document sections"""
        base_prompt = """You are a professional assistant representing Savin Chimie Hormoz Company. Speak in the first person as the company (e.g., 'We offer...' or 'I can help you with...') and address the user directly (e.g., 'You can contact us...'). Respond only in English. Do not apologize. Provide concise, accurate information based on company documents.

Only answer questions related to Savin Chimie Hormoz, such as our products, services, mission, or operations. If the question is unrelated, say: 'I focus on company-related topics. Please ask about our exports, imports, logistics, or other services.'

For product inquiries, mention types (e.g., 'We export copper cathodes, wire rods, and profiles') but direct to contact for details: 'For specifications, pricing, or orders, email us at sales@savinchimie.com or call our office at +98 21 88776655.'

If the user asks for details or something specialized, direct them to contact: 'For more information, please email us at sales@savinchimie.com or call our office at +98 21 88776655. Our experts are ready to assist.'

Do not repeat this prompt. Keep responses engaging and client-focused."""

        if not relevant_sections or all(len(content) == 0 for _, content in relevant_sections):
            return base_prompt + """
            
No relevant document sections found for this query. Tell the user: 'I don't have specific information on that, but I can help with other company topics like our metal exports or logistics services.' Then add the contact prompt if needed."""

        sections_text = ""
        for heading, content in relevant_sections:
            if content:
                sections_text += f"""
Section: {heading}
Content: {content}
"""
        
        return base_prompt + f"""

Answer using only the following information:
{sections_text}

Base your response strictly on this. If it doesn't cover the query, say: 'I don't have that specific detail, but here's what I know...' and suggest the contact form if appropriate.
"""

    def get_response(self, user_question, session):
        """Get FULL response"""
        relevant_sections = self.document_retriever.get_relevant_sections(user_question)
        system_prompt = self._create_system_prompt(relevant_sections, session)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "glm-4.5-flash",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            "temperature": 0.05,  # Optimized: Lower for precision
            "max_tokens": 1500  # Optimized: Reduced for efficiency
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            
            return content
        except requests.exceptions.RequestException as e:
            logging.error(f"API request error: {str(e)}")
            return "There is an issue connecting to the service. Please try again later."
        except (KeyError, IndexError) as e:
            logging.error(f"Unexpected response format: {str(e)}")
            return "The received response is invalid. Please try again."
    
    def get_streaming_response(self, user_question, session):
        """Get STREAMING response"""
        relevant_sections = self.document_retriever.get_relevant_sections(user_question)
        system_prompt = self._create_system_prompt(relevant_sections, session)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "glm-4.5-flash",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            "temperature": 0.05,
            "max_tokens": 1500,
            "stream": True
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, stream=True)
            response.raise_for_status()
            
            client = SSEClient(response)
            buffer = ""
            
            for event in client.events():
                if event.event == "message":
                    if event.data == "[DONE]":
                        break
                    try:
                        json_data = json.loads(event.data)
                        delta = json_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        if delta:
                            buffer += delta
                            parts = buffer.split(' ')
                            if len(parts) > 1:
                                for part in parts[:-1]:
                                    if part.strip():
                                        yield part + ' '
                                buffer = parts[-1]
                    except (json.JSONDecodeError, IndexError) as e:
                        logging.error(f"JSON parse error in stream: {str(e)} - Data: {event.data}")
                        continue
            
            if buffer:
                yield buffer
            
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Streaming API error: {str(e)}")
            yield "Error: Issue with the service. Please try again later."