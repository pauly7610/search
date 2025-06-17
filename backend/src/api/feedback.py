from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class FeedbackSchema(BaseModel):
    conversation_id: str = None
    message_id: str
    rating: int
    comment: str = None

@router.post("/submit")
def submit_feedback(feedback: FeedbackSchema):
    # For demo, just acknowledge receipt
    return {"status": "received", "feedback": feedback}

@router.post("/")
def submit_feedback_root(feedback: FeedbackSchema):
    # For demo, just acknowledge receipt
    return {"status": "received", "feedback": feedback} 