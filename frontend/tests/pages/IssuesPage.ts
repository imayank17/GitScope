import { Locator, Page } from '@playwright/test';

export class IssuesPage {
  readonly page: Page;
  readonly headerTitle: Locator;
  readonly stateTabs: Locator;
  readonly issueCards: Locator;
  readonly paginationContainer: Locator;

  constructor(page: Page) {
    this.page = page;
    this.headerTitle = page.locator('h2.text-surface-50').first();
    this.stateTabs = page.locator('div.flex.gap-1 button');
    this.issueCards = page.locator('div.space-y-3 > div');
    this.paginationContainer = page.locator('nav.flex.justify-center');
  }

  async switchTab(tab: 'open' | 'closed' | 'all') {
    const tabButton = this.page.locator('div.flex.gap-1 button', { text: tab });
    await tabButton.click();
  }

  getIssueCard(title: string): Locator {
    return this.page.locator('div.bg-surface-800\\/40', { has: this.page.locator('h3.font-semibold', { text: title }) });
  }

  async verifyIssueVisible(title: string): Promise<boolean> {
    const card = this.getIssueCard(title);
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
