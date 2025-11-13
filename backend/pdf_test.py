from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# For importing/using the function elsewhere
def analyze_pdf(pdf_path, question):
    """
    Uploads a PDF to OpenAI and asks a question about it.
    
    Args:
        pdf_path: Path to the PDF file
        question: Question to ask about the PDF content
        
    Returns:
        str: The AI's response text
    """
    try:
        # Upload the PDF file to OpenAI
        with open(pdf_path, "rb") as f:
            file = client.files.create(
                file=f,
                purpose="user_data"
            )
        
        # Create a response using the uploaded file
        response = client.responses.create(
            model="gpt-5-nano", 
            input=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "input_text", "text": question},
                        {"type": "input_file", "file_id": file.id},
                    ]
                }
            ]
        )
        
        return response.output_text
        
    except FileNotFoundError:
        return "Error: PDF file not found!"
    except Exception as e:
        return f"Error: {str(e)}"

# If running from file directly as a script
if __name__ == "__main__":
    # Example: Generate practice questions from a lecture PDF
    result = analyze_pdf(
        pdf_path="<Insert pdf path>",
        question="Could you generate 5 practice questions about key concepts in this lecture? Only list out the questions, JSON format"
    )
    print(result)