export interface Repository {
  id: string | null;
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  stars: number;
  forks: number;
  open_issues: number;
  watchers: number;
  topics: string[];
  visibility: string;
  default_branch: string;
  created_at: string;
  updated_at: string;
  html_url: string;
  clone_url: string;
  owner_login: string;
  owner_avatar_url: string;
}

export interface RepositoryAnalyzeRequest {
  repo_url: string;
}
