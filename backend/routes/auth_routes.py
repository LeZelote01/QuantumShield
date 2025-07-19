"""
Routes d'authentification
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

from models.quantum_models import User, UserCreate, UserLogin
from services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()

# Dependency pour l'authentification
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Récupère l'utilisateur actuel depuis le token"""
    from server import auth_service
    
    token = credentials.credentials
    auth_result = await auth_service.verify_token(token)
    
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )
    
    return auth_result["user"]

# Modèles de requête
class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class ProfileUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None

# Routes
@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """Enregistre un nouvel utilisateur"""
    from server import auth_service
    
    try:
        user = await auth_service.register_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login")
async def login(login_data: UserLogin):
    """Connecte un utilisateur"""
    from server import auth_service
    
    auth_result = await auth_service.authenticate_user(login_data)
    
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects"
        )
    
    return {
        "user": auth_result["user"],
        "token": auth_result["token"],
        "expires_at": auth_result["expires_at"]
    }

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Déconnecte un utilisateur"""
    from server import auth_service
    
    token = credentials.credentials
    success = await auth_service.logout_user(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de déconnecter"
        )
    
    return {"message": "Déconnecté avec succès"}

@router.get("/profile", response_model=User)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Récupère le profil de l'utilisateur actuel"""
    return current_user

@router.put("/profile", response_model=User)
async def update_profile(profile_data: ProfileUpdate, current_user: User = Depends(get_current_user)):
    """Met à jour le profil de l'utilisateur"""
    from server import auth_service
    
    updated_user = await auth_service.update_user_profile(
        current_user.id, 
        profile_data.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de mettre à jour le profil"
        )
    
    return updated_user

@router.post("/change-password")
async def change_password(password_data: PasswordChange, current_user: User = Depends(get_current_user)):
    """Change le mot de passe de l'utilisateur"""
    from server import auth_service
    
    success = await auth_service.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de changer le mot de passe"
        )
    
    return {"message": "Mot de passe changé avec succès"}

@router.get("/stats")
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """Récupère les statistiques de l'utilisateur"""
    from server import auth_service
    
    stats = await auth_service.get_user_stats(current_user.id)
    return stats

@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Vérifie la validité du token"""
    return {"valid": True, "user": current_user}