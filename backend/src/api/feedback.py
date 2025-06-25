from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
import csv
from io import StringIO
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Query
from src.config.database import get_db
from src.models.feedback_models import Feedback

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


@router.get("/export")
async def export_feedback(
    format: str = Query("json", enum=["json", "csv"]),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Feedback))
    feedbacks = result.scalars().all()
    if format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "message_id", "rating", "comment", "timestamp"])
        for fb in feedbacks:
            writer.writerow([fb.id, fb.message_id, fb.rating, fb.comment, fb.timestamp])
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=feedback_export.csv"},
        )
    else:
        data = [
            {
                "id": fb.id,
                "message_id": fb.message_id,
                "rating": fb.rating,
                "comment": fb.comment,
                "timestamp": fb.timestamp.isoformat() if fb.timestamp else None,
            }
            for fb in feedbacks
        ]
        return JSONResponse(content=data)
