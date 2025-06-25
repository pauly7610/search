from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    avatar_url: str = ""
    bio: str = ""


# In-memory mock profile
dummy_profile = UserProfile(
    id="user-1",
    name="Demo User",
    email="demo@example.com",
    avatar_url="https://api.dicebear.com/6.x/identicon/svg?seed=demo",
    bio="This is a demo user profile.",
)


@router.get("/profile", response_model=UserProfile)
def get_profile():
    return dummy_profile


@router.put("/profile", response_model=UserProfile)
def update_profile(profile: UserProfile):
    global dummy_profile
    dummy_profile = profile
    return dummy_profile
