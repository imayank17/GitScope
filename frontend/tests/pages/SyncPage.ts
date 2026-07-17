import { Locator, Page } from '@playwright/test';

export class SyncPage {
  readonly page: Page;
  readonly headerTitle: Locator;
  readonly syncCard: Locator;
  readonly refreshButton: Locator;
  readonly statusLabel: Locator;
  readonly lastSyncedLabel: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.headerTitle = page.locator('h2.text-surface-50').first();
    this.syncCard = page.locator('div.bg-surface-800\\/60', { has: page.locator('h3:has-text("Synchronization")') });
    this.refreshButton = this.syncCard.locator('button:has-text("Refresh Now"), button:has-text("Syncing...")');
    this.statusLabel = this.syncCard.locator('div.flex.items-center.gap-2 span');
    this.lastSyncedLabel = this.syncCard.locator('p:has-text("Last synced:")');
    this.errorMessage = page.locator('p.text-red-400');
  }

  async triggerRefresh() {
    await this.refreshButton.click();
  }

  async getSyncStatus(): Promise<string | null> {
    await this.statusLabel.waitFor({ state: 'visible', timeout: 5000 });
    return this.statusLabel.textContent();
  }

  async getLastSyncedTime(): Promise<string | null> {
    try {
      await this.lastSyncedLabel.waitFor({ state: 'visible', timeout: 5000 });
      return this.lastSyncedLabel.textContent();
    } catch {
      return null;
    }
  }

  async getErrorMessage(): Promise<string | null> {
    try {
      await this.errorMessage.waitFor({ state: 'visible', timeout: 5000 });
      return this.errorMessage.textContent();
    } catch {
      return null;
    }
  }
}
