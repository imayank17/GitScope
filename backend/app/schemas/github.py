""" GitHub Schemas """

from pydantic import BaseModel, Field


class RepositoryAnalyzeRequest(BaseModel):
    """
    Accepts either format:
   "fastapi/fastapi" or "https://github.com/fastapi/fastapi"
    """

    repo_url: str = Field(
        ...,
        min_length=3,
        examples=["fastapi/fastapi", "https://github.com/fastapi/fastapi"],
        description="GitHub repository — either 'owner/repo' or a full URL.",
    )


class RepositoryResponse(BaseModel):
   
    name: str
    full_name: str
    description: str | None = None
    language: str | None = None

    # Counts
    stars: int
    forks: int
    open_issues: int
    watchers: int

    # Metadata
    topics: list[str] = []
    visibility: str
    default_branch: str

    # Timestamps
    created_at: str
    updated_at: str

    # URLs
    html_url: str
    clone_url: str

    # Owner info
    owner_login: str
    owner_avatar_url: str