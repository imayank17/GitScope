import { Locator, Page } from '@playwright/test';

export class ContributorsPage {
  readonly page: Page;
  readonly headerTitle: Locator;
  readonly searchInput: Locator;
  readonly contributorCards: Locator;
  readonly paginationContainer: Locator;

  constructor(page: Page) {
    this.page = page;
    this.headerTitle = page.locator('h2.text-surface-50').first();
    this.searchInput = page.getByPlaceholder('Search contributors...');
    this.contributorCards = page.locator('div.grid > div:has(img)'); // ContributorCard contains avatar img
    this.paginationContainer = page.locator('nav.flex.justify-center');
  }

  async searchContributor(name: string) {
    await this.searchInput.fill(name);
  }

  getContributorCard(name: string): Locator {
    return this.page.locator('div.bg-surface-800\\/40', { has: this.page.locator('h3', { text: name }) });
  }

  async verifyContributorVisible(name: string): Promise<boolean> {
    const card = this.getContributorCard(name);
    try {
      await card.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  async getContributorContributions(name: string): Promise<string | null> {
    const card = this.getContributorCard(name);
    return card.locator('p.text-xs').textContent();
  }

  async goToNextPage() {
    const nextButton = this.paginationContainer.getByRole('button', { name: 'Next' });
    await nextButton.click();
  }
}
