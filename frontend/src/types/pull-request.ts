export interface PullRequest {
  number: number;
  title: string;
  state: string;
  user_login: string;
  created_at: string;
  updated_at: string;
  html_url: string;
  labels: string[];
  merged_at: string | null;
  draft: boolean;
}
