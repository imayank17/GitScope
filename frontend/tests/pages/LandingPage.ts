import { Locator, Page } from '@playwright/test';

export class LandingPage {
  readonly page: Page;
  readonly logo: Locator;
  readonly searchInput: Locator;
  readonly analyzeButton: Locator;
  readonly errorMessage: Locator;
  readonly featureCards: Locator;
  readonly quickLinkVercel: Locator;
  readonly quickLinkVSCode: Locator;

  constructor(page: Page) {
    this.page = page;
    this.logo = page.locator('a:has-text("GitScope")').first();
    this.searchInput = page.getByPlaceholder('https://github.com/vercel/next.js');
    this.analyzeButton = page.getByRole('button', { name: 'Analyze', exact: true });
    this.errorMessage = page.locator('p.text-red-400');
    this.featureCards = page.locator('#features div.grid > div');
    this.quickLinkVercel = page.getByRole('button', { name: 'vercel/next.js', exact: true });
    this.quickLinkVSCode = page.getByRole('button', { name: 'microsoft/vscode', exact: true });
  }

  async navigate() {
    await this.page.goto('/');
  }

  async fillSearch(url: string) {
    await this.searchInput.fill(url);
  }

  async analyzeRepository(url: string) {
    await this.fillSearch(url);
    await this.analyzeButton.click();
  }

  async getErrorMessage(): Promise<string | null> {
    await this.errorMessage.waitFor({ state: 'visible', timeout: 5000 });
    return this.errorMessage.textContent();
  }
}
