"""
Dependency Injection
"""

from fastapi import Depends, Request

from app.services.github_service import GitHubService
from app.repositories.github_repository import GitHubRepository


def get_github_service(request: Request) -> GitHubService:
  
    return GitHubService(client=request.app.state.http_client)


def get_github_repository(
    service: GitHubService = Depends(get_github_service),
) -> GitHubRepository:
   
    return GitHubRepository(github_service=service)
