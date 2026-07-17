import { test, expect } from '../fixtures/testFixtures';

test.describe('Repository Cache Synchronization', () => {
  test('Page loads and displays sync status details', async ({ page, syncPage }) => {
    await page.goto('/test-owner/test-repo/sync');
    
    await expect(syncPage.headerTitle).toBeVisible();
    await expect(syncPage.headerTitle).toContainText('Synchronization');

    const status = await syncPage.getSyncStatus();
    expect(status?.trim()).toBe('Synced'); // COMPLETED maps to 'Synced' in UI
    
    const lastSynced = await syncPage.getLastSyncedTime();
    expect(lastSynced).toContain('Last synced:');
  });

  test('Clicking refresh triggers background sync, changes state to Syncing and resolves to Synced', async ({ page, syncPage, mockApi }) => {
    // Navigate to sync page
    await page.goto('/test-owner/test-repo/sync');

    let isSyncingTriggered = false;
    let syncStatusCallCount = 0;
    // Set up a dynamic route mock for sync status polling
    await page.route(/\/api\/repositories\/[^/]+\/sync-status/, async (route) => {
      if (!isSyncingTriggered) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            repository_id: 'd3b07384-d113-4c31-92b5-e51c11005bf3',
            status: 'COMPLETED',
            last_synced_at: new Date().toISOString(),
            error: null
          }),
        });
      } else {
        syncStatusCallCount++;
        const status = syncStatusCallCount <= 2 ? 'SYNCING' : 'COMPLETED';
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            repository_id: 'd3b07384-d113-4c31-92b5-e51c11005bf3',
            status,
            last_synced_at: new Date().toISOString(),
            error: null
          }),
        });
      }
    });

    // Verify initial button is 'Refresh Now'
    await expect(syncPage.refreshButton).toHaveText('Refresh Now');

    // Enable syncing response sequence
    isSyncingTriggered = true;

    // Trigger manual refresh
    await syncPage.triggerRefresh();

    // Verify immediately changes to 'Syncing...' and gets disabled
    await expect(syncPage.refreshButton).toHaveText('Syncing...');
    await expect(syncPage.refreshButton).toBeDisabled();

    // Wait for the status text in the status indicator to update to Synced (COMPLETED)
    await expect(syncPage.statusLabel).toHaveText('Synced', { timeout: 10000 });

    // Verify the button reverts back to 'Refresh Now'
    await expect(syncPage.refreshButton).toHaveText('Refresh Now', { timeout: 5000 });
  });
});
