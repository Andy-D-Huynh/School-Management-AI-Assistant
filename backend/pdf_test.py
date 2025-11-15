from dotenv import load_dotenv
import os
from openai import OpenAI
from PyPDF2 import PdfReader

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_pdf_text(pdf_path):
    """
    Extracts all text from a PDF and returns it as a string.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except FileNotFoundError:
        raise ValueError("Error: PDF file not found!")
    except Exception as e:
        raise ValueError(f"Error extracting PDF: {str(e)}")

def chunk_text(text, chunk_size=2000):
    """
    Splits a text string into chunks of roughly chunk_size characters.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        # Try to cut at the last newline or space for cleaner splits
        if end < len(text):
            split_at = text.rfind("\n", start, end)
            if split_at == -1:
                split_at = text.rfind(" ", start, end)
            if split_at == -1:
                split_at = end
            end = split_at
        chunks.append(text[start:end].strip())
        start = end
    return chunks

class PDFConversation:
    """
    Multi-turn conversation using PDF content as context.
    Dynamically handles long PDFs by chunking.
    """
    def __init__(self, pdf_path: str, system_prompt="You are a helpful study assistant."):
        self.pdf_text = extract_pdf_text(pdf_path)
        self.system_prompt = system_prompt

        # Create a conversation with initial system message
        self.convo = client.conversations.create(
            metadata={"type": "pdf_study_chat"},
            items=[]
        )
        self.id = self.convo.id

        # Feed PDF in chunks to the conversation
        chunks = chunk_text(self.pdf_text, chunk_size=2000)
        for i, chunk in enumerate(chunks):
            client.conversations.items.create(
                self.id,
                items=[
                    {
                        "type": "message",
                        "role": "system",
                        "content": [
                            {"type": "input_text", "text": f"{system_prompt} (PDF chunk {i+1}/{len(chunks)}):\n{chunk}"}
                        ]
                    }
                ]
            )

    def ask(self, user_input):
        """
        Sends a user message into the conversation, then gets the model's reply.
        """
        # Add the user message
        client.conversations.items.create(
            self.id,
            items=[
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_input}
                    ]
                }
            ]
        )

        # Generate the model response
        response = client.responses.create(
            model="gpt-5-nano",
            conversation=self.id,
            input=[{"role": "user", "content": [{"type": "input_text", "text": user_input}]}]
        )

        return response.output_text

# --- Terminal chat interface ---
if __name__ == "__main__":
    pdf_path = input("Enter path to lecture PDF: ")
    try:
        chat = PDFConversation(pdf_path)
    except ValueError as e:
        print(e)
        exit()

    print("\nPDF loaded. You can now chat with the AI.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Goodbye!")
            break

        reply = chat.ask(user_input)
        print("\nAI:", reply, "\n")
