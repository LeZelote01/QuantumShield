"""
Middleware de rate limiting pour QuantumShield
Applique automatiquement les limites de taux sur toutes les requêtes
"""

import time
import logging
from typing import Callable
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware pour appliquer le rate limiting automatiquement"""
    
    def __init__(self, app: ASGIApp, api_gateway_service=None):
        super().__init__(app)
        self.api_gateway_service = api_gateway_service
        self.bypass_paths = {
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/api/health",
            "/api/api-gateway/health"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Traite chaque requête avec rate limiting"""
        start_time = time.time()
        
        try:
            # Vérifier si on doit bypass le rate limiting
            if self._should_bypass(request):
                response = await call_next(request)
                return response
            
            # Vérifier si le service est disponible
            if not self.api_gateway_service or not self.api_gateway_service.is_ready():
                # Passer la requête sans rate limiting si le service n'est pas disponible
                response = await call_next(request)
                return response
            
            # Extraire la clé API depuis les headers
            api_key = self._extract_api_key(request)
            
            # Vérifier le rate limiting
            allowed, result = await self.api_gateway_service.check_rate_limit(
                request=request,
                api_key=api_key
            )
            
            if not allowed:
                # Rate limit dépassé
                error_response = {
                    "error": result.get("error", "Rate limit exceeded"),
                    "status": result.get("status", "rate_limited"),
                    "retry_after": result.get("retry_after", 60),
                    "rate_limit_info": result.get("rate_limit_info"),
                    "timestamp": time.time()
                }
                
                # Headers de rate limiting
                headers = self._build_rate_limit_headers(result.get("rate_limit_info", {}))
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=error_response,
                    headers=headers
                )
            
            # Requête autorisée, continuer
            response = await call_next(request)
            
            # Ajouter les headers de rate limiting à la réponse
            if "rate_limit_info" in result:
                rate_limit_headers = self._build_rate_limit_headers(result["rate_limit_info"])
                for key, value in rate_limit_headers.items():
                    response.headers[key] = value
            
            # Calculer le temps de réponse
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur middleware rate limiting: {e}")
            # En cas d'erreur, passer la requête sans rate limiting
            response = await call_next(request)
            return response
    
    def _should_bypass(self, request: Request) -> bool:
        """Détermine si on doit bypasser le rate limiting"""
        path = request.url.path
        
        # Bypass pour les chemins statiques et de documentation
        if path in self.bypass_paths:
            return True
        
        # Bypass pour les fichiers statiques
        if path.startswith("/static/") or path.startswith("/assets/"):
            return True
        
        # Bypass pour les health checks internes
        if path.endswith("/health") and request.method == "GET":
            return True
        
        # Bypass pour les utilisateurs authentifiés avec JWT
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and len(auth_header) > 50:  # JWT tokens are longer
            return True
        
        # Bypass pour les endpoints publics de crypto
        public_crypto_endpoints = [
            "/api/advanced-crypto/supported-algorithms",
            "/api/advanced-crypto/performance-comparison",
            "/api/advanced-crypto/algorithm-recommendations"
        ]
        if path in public_crypto_endpoints:
            return True
        
        return False
    
    def _extract_api_key(self, request: Request) -> str:
        """Extrait la clé API de la requête (pas les JWT tokens)"""
        # Essayer l'header X-API-Key (clés API dédiées)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        
        # Essayer le paramètre de query
        api_key = request.query_params.get("api_key")
        if api_key:
            return api_key
        
        # NE PAS traiter les JWT tokens comme des clés API
        # Les JWT tokens dans Authorization: Bearer sont gérés par l'auth service
        return None
    
    def _build_rate_limit_headers(self, rate_limit_info: dict) -> dict:
        """Construit les headers de rate limiting"""
        headers = {}
        
        if not rate_limit_info:
            return headers
        
        limits = rate_limit_info.get("limits", {})
        current_usage = rate_limit_info.get("current_usage", {})
        reset_times = rate_limit_info.get("reset_times", {})
        
        # Headers standards de rate limiting
        if "per_minute" in limits:
            headers["X-RateLimit-Limit-Minute"] = str(limits["per_minute"])
            headers["X-RateLimit-Remaining-Minute"] = str(
                max(0, limits["per_minute"] - current_usage.get("per_minute", 0))
            )
            if "per_minute" in reset_times:
                headers["X-RateLimit-Reset-Minute"] = str(reset_times["per_minute"])
        
        if "per_hour" in limits:
            headers["X-RateLimit-Limit-Hour"] = str(limits["per_hour"])
            headers["X-RateLimit-Remaining-Hour"] = str(
                max(0, limits["per_hour"] - current_usage.get("per_hour", 0))
            )
            if "per_hour" in reset_times:
                headers["X-RateLimit-Reset-Hour"] = str(reset_times["per_hour"])
        
        if "per_day" in limits:
            headers["X-RateLimit-Limit-Day"] = str(limits["per_day"])
            headers["X-RateLimit-Remaining-Day"] = str(
                max(0, limits["per_day"] - current_usage.get("per_day", 0))
            )
            if "per_day" in reset_times:
                headers["X-RateLimit-Reset-Day"] = str(reset_times["per_day"])
        
        # Tier d'API
        tier = rate_limit_info.get("tier", "free")
        headers["X-RateLimit-Tier"] = tier
        
        return headers

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de sécurité pour l'API Gateway"""
    
    def __init__(self, app: ASGIApp, api_gateway_service=None):
        super().__init__(app)
        self.api_gateway_service = api_gateway_service
        self.suspicious_patterns = [
            "script",
            "javascript:",
            "<script>",
            "eval(",
            "document.cookie",
            "window.location"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Applique les vérifications de sécurité"""
        try:
            # Vérifier les patterns suspects dans l'URL
            if self._contains_suspicious_patterns(str(request.url)):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Requête suspecte détectée"}
                )
            
            # Vérifier la taille de la requête
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"error": "Requête trop volumineuse"}
                )
            
            # Ajouter des headers de sécurité
            response = await call_next(request)
            
            # Headers de sécurité
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            }
            
            for key, value in security_headers.items():
                response.headers[key] = value
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur middleware sécurité: {e}")
            response = await call_next(request)
            return response
    
    def _contains_suspicious_patterns(self, text: str) -> bool:
        """Vérifie si le texte contient des patterns suspects"""
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.suspicious_patterns)

class CORSMiddleware(BaseHTTPMiddleware):
    """Middleware CORS personnalisé avec rate limiting"""
    
    def __init__(self, app: ASGIApp, allow_origins=None, allow_methods=None, allow_headers=None):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Gère les requêtes CORS"""
        try:
            # Gérer les requêtes OPTIONS (preflight)
            if request.method == "OPTIONS":
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
                        "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
                        "Access-Control-Max-Age": "86400"
                    }
                )
            
            response = await call_next(request)
            
            # Ajouter les headers CORS
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur middleware CORS: {e}")
            response = await call_next(request)
            return response

def setup_api_gateway_middleware(app: FastAPI, api_gateway_service):
    """Configure tous les middlewares de l'API Gateway"""
    
    # Middleware de sécurité (en premier)
    app.add_middleware(SecurityMiddleware, api_gateway_service=api_gateway_service)
    
    # Middleware CORS
    app.add_middleware(CORSMiddleware)
    
    # Middleware de rate limiting (en dernier pour traiter les requêtes valides)
    app.add_middleware(RateLimitMiddleware, api_gateway_service=api_gateway_service)
    
    logger.info("Middlewares API Gateway configurés")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger toutes les requêtes"""
    
    def __init__(self, app: ASGIApp, api_gateway_service=None):
        super().__init__(app)
        self.api_gateway_service = api_gateway_service
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Logge les requêtes"""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculer le temps de traitement
            process_time = time.time() - start_time
            
            # Logger la requête si nécessaire
            if self.api_gateway_service and hasattr(self.api_gateway_service, 'log_request'):
                await self.api_gateway_service.log_request({
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "ip_address": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", ""),
                    "timestamp": time.time()
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur middleware logging: {e}")
            response = await call_next(request)
            return response