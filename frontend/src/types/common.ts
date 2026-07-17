export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  per_page: number;
  total_pages: number;
}
