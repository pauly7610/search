from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Feedback(BaseModel):
    conversation_id: str = None
    message_id: str
    rating: int
    comment: str = None

@router.post("/submit")
def submit_feedback(feedback: Feedback):
    # For demo, just acknowledge receipt
    return {"status": "received", "feedback": feedback}

@router.post("/")
def submit_feedback_root(feedback: Feedback):
    # For demo, just acknowledge receipt
    return {"status": "received", "feedback": feedback} 