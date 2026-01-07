import sys
import codecs
from document_database import DocumentDatabase
from document_retriever import DocumentRetriever
from chatbot import DocumentChatbot

def main():
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if sys.stdin.encoding != 'utf-8':
        sys.stdin = codecs.getreader('utf-8')(sys.stdin.buffer, 'strict')
    
    document_db = DocumentDatabase('answers.txt')
    document_retriever = DocumentRetriever(document_db)
    
    API_KEY = "c35654cc6502485eb24b3d2b47a0946a.n3eGF4CnOUS8YRKF"
    
    chatbot = DocumentChatbot(API_KEY, document_retriever)
    
    print("Savin Chimie Hormoz Company Chatbot is ready! Type 'quit' or 'exit' to leave.")
    print("Document includes sections:")
    for heading, _ in document_db.get_all_sections():
        print(f"- {heading}")
    
    while True:
        try:
            user_input = input("Ask: ")
        except UnicodeDecodeError:
            print("Input error. Please use standard characters.")
            continue
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        print("Bot: ", end='', flush=True)
        for response in chatbot.get_streaming_response(user_input, {}):  # Pass dummy session for main.py
            print(response, end=' ', flush=True)
        print("\n")

if __name__ == "__main__":
    main()