import { test, expect } from '../fixtures/testFixtures';

test.describe('Authentication and Public Access', () => {
  test('Landing page is public and loads without login redirect', async ({ landingPage }) => {
    await landingPage.navigate();
    await expect(landingPage.searchInput).toBeVisible();
    await expect(landingPage.logo).toContainText('GitScope');
  });

  test('Dashboard links do not request authentication', async ({ page, mockApi }) => {
    // Navigate directly to a mock repo dashboard
    await page.goto(`/test-owner/test-repo`);
    
    // Check that we successfully load the main layout components instead of an auth page
    const sidebar = page.locator('aside');
    await expect(sidebar).toBeVisible();
    
    const heading = page.locator('h2.text-surface-50').first();
    await expect(heading).toContainText('test-owner/test-repo');
  });
});
