import { Locator, Page } from '@playwright/test';

export class CommitsPage {
  readonly page: Page;
  readonly headerTitle: Locator;
  readonly commitCards: Locator;
  readonly paginationContainer: Locator;

  constructor(page: Page) {
    this.page = page;
    this.headerTitle = page.locator('h2.text-surface-50').first();
    this.commitCards = page.locator('div.space-y-3 > div');
    this.paginationContainer = page.locator('nav.flex.justify-center');
  }

  getCommitCard(message: string): Locator {
    return this.page.locator('div.bg-surface-800\\/40', { has: this.page.locator('p.text-surface-100', { text: message }) });
  }

  async verifyCommitVisible(message: string): Promise<boolean> {
    const card = this.getCommitCard(message);
    try {
      await card.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  async goToNextPage() {
    const nextButton = this.paginationContainer.getByRole('button', { name: 'Next' });
    await nextButton.click();
  }
}
