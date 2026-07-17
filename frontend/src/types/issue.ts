export interface Issue {
  number: number;
  title: string;
  state: string;
  user_login: string;
  created_at: string;
  updated_at: string;
  html_url: string;
  labels: string[];
  comments: number;
}
