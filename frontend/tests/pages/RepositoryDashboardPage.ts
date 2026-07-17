import { Locator, Page } from '@playwright/test';

export class RepositoryDashboardPage {
  readonly page: Page;
  readonly headerTitle: Locator;
  readonly repoCard: Locator;
  readonly chartsContainer: Locator;
  readonly sidebarToggle: Locator;

  constructor(page: Page) {
    this.page = page;
    this.headerTitle = page.locator('h2.text-surface-50').first();
    this.repoCard = page.locator('div.bg-surface-800\\/60', { hasText: 'View on GitHub' });
    this.chartsContainer = page.locator('h3', { hasText: 'Commit Activity' });
    this.sidebarToggle = page.locator('aside button').first();
  }

  getStatCard(label: string): Locator {
    return this.page.locator('div.bg-surface-800\\/60').filter({ hasText: label });
  }

  async getStatValue(label: string): Promise<string | null> {
    const card = this.getStatCard(label);
    const valueLocator = card.locator('p.text-2xl');
    await valueLocator.waitFor({ state: 'visible', timeout: 5000 });
    return valueLocator.textContent();
  }

  async navigateSidebar(itemLabel: string) {
    const sidebarLink = this.page.locator('aside nav a', { hasText: itemLabel });
    await sidebarLink.click();
  }
}
