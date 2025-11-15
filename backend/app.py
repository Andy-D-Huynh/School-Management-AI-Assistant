from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import os
import uuid
from pdf_test import PDFConversation

class QuestionRequest(BaseModel):
    question: str
    conversation_id: str

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for conversations (session_id -> PDFConversation)
conversations = {}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file upload, processes it, and creates a conversation.
    Returns conversation_id for subsequent questions.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Create PDFConversation instance
        conversation = PDFConversation(temp_path)
        
        # Store conversation
        conversations[session_id] = conversation
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return JSONResponse({
            "success": True,
            "conversation_id": session_id,
            "message": "PDF processed successfully"
        })
    
    except ValueError as e:
        # Clean up temp file if it exists
        if temp_file and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Clean up temp file if it exists
        if temp_file and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Accepts a question and conversation_id, returns AI response.
    """
    if request.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        conversation = conversations[request.conversation_id]
        response = conversation.ask(request.question)
        
        return JSONResponse({
            "success": True,
            "response": response
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting response: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

