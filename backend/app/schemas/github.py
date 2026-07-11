"""
GitHub Schemas

Pydantic models for request validation and response serialization.
  RepositoryAnalyzeRequest  — POST body for /repositories/analyze
  RepositoryResponse        — repository metadata response
  PaginatedResponse         — generic pagination wrapper
  ContributorResponse       — contributor info
  CommitResponse            — commit info
  LanguageResponse          — language breakdown with percentages
  PullRequestResponse       — pull request info
  IssueResponse             — issue info
"""

from pydantic import BaseModel, Field


#Existing schemas (unchanged)

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




# Generic pagination wrapper

class PaginatedResponse(BaseModel):
    """
    Wraps any paginated list endpoint.

    Every list endpoint returns this same shape, so API consumers
    always know: items are in "items", pagination info is in the
    top-level fields.
    """
    items: list = Field(
        ...,
        description="List of results for this page.",
    )
    page: int = Field(
        ...,
        description="Current page number (1-indexed).",
    )
    per_page: int = Field(
        ...,
        description="Number of results requested per page.",
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages available.",
    )


# Contributors

class ContributorResponse(BaseModel):
    """
    A repository contributor.

    Maps from GitHub's /repos/{owner}/{repo}/contributors response.
    """
    login: str = Field(..., description="GitHub username.")
    avatar_url: str = Field(..., description="Avatar image URL.")
    contributions: int = Field(..., description="Number of commits by this user.")
    html_url: str = Field(..., description="Profile URL on GitHub.")


# Commits

class CommitResponse(BaseModel):
    """
    A single commit.

    GitHub nests commit data deeply — this schema flattens it:
      data["sha"]                          → sha
      data["commit"]["message"]            → message
      data["commit"]["author"]["name"]     → author_name
      data["commit"]["author"]["email"]    → author_email
      data["commit"]["author"]["date"]     → author_date
      data["commit"]["committer"]["name"]  → committer_name
      data["html_url"]                     → html_url
    """
    sha: str = Field(..., description="Full commit SHA hash.")
    message: str = Field(..., description="Commit message.")
    author_name: str = Field(..., description="Author's display name.")
    author_email: str = Field(..., description="Author's email address.")
    author_date: str = Field(..., description="When the commit was authored (ISO 8601).")
    committer_name: str = Field(..., description="Committer's display name.")
    html_url: str = Field(..., description="URL to view this commit on GitHub.")


# Languages

class LanguageResponse(BaseModel):
    """
    Language breakdown for a repository.

    GitHub returns raw bytes: {"Python": 150234, "JavaScript": 48012}
    We add total_bytes and percentages so this is chart-ready.
    """
    languages: dict[str, int] = Field(
        ...,
        description="Map of language name → bytes of code.",
    )
    total_bytes: int = Field(
        ...,
        description="Sum of all language byte counts.",
    )
    percentages: dict[str, float] = Field(
        ...,
        description="Map of language name → percentage of codebase (rounded to 2 decimals).",
    )


# Pull Requests

class PullRequestResponse(BaseModel):
    """
    A pull request.

    Maps from GitHub's /repos/{owner}/{repo}/pulls response.
    """
    number: int = Field(..., description="PR number.")
    title: str = Field(..., description="PR title.")
    state: str = Field(..., description="State: 'open' or 'closed'.")
    user_login: str = Field(..., description="Username of the PR author.")
    created_at: str = Field(..., description="When the PR was created (ISO 8601).")
    updated_at: str = Field(..., description="When the PR was last updated (ISO 8601).")
    html_url: str = Field(..., description="URL to view this PR on GitHub.")
    labels: list[str] = Field(
        default=[],
        description="List of label names attached to this PR.",
    )
    merged_at: str | None = Field(
        default=None,
        description="When the PR was merged (null if not merged).",
    )
    draft: bool = Field(
        default=False,
        description="Whether this is a draft PR.",
    )


# Issues

class IssueResponse(BaseModel):
    """
    An issue (not a pull request).

    GitHub's Issues API returns both issues and PRs.
    The service layer filters out PRs before this schema is used.
    """
    number: int = Field(..., description="Issue number.")
    title: str = Field(..., description="Issue title.")
    state: str = Field(..., description="State: 'open' or 'closed'.")
    user_login: str = Field(..., description="Username of the issue author.")
    created_at: str = Field(..., description="When the issue was created (ISO 8601).")
    updated_at: str = Field(..., description="When the issue was last updated (ISO 8601).")
    html_url: str = Field(..., description="URL to view this issue on GitHub.")
    labels: list[str] = Field(
        default=[],
        description="List of label names attached to this issue.",
    )
    comments: int = Field(
        default=0,
        description="Number of comments on this issue.",
    )