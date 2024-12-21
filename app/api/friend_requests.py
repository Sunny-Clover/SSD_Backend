from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.schemas import *
from app.core.security import get_password_hash

router = APIRouter()