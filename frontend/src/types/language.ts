export interface LanguageBreakdown {
  languages: Record<string, number>;
  total_bytes: number;
  percentages: Record<string, number>;
}
