from pydantic import BaseModel


class RepositoryResponse(BaseModel):

    name: str

    full_name: str

    stars: int

    forks: int

    open_issues: int

    language: str | None

    watchers: int