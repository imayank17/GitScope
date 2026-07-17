export interface SyncStatus {
  repository_id: string;
  status: string;
  last_synced_at: string | null;
  error: string | null;
}

export interface RefreshResponse {
  repository_id: string;
  status: string;
  message: string;
}
