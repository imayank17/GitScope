import { test, expect } from '../fixtures/testFixtures';

test.describe('Responsive Viewports Layout & Navigation', () => {
  test.beforeEach(async ({ page, mockApi }) => {
    await page.goto('/test-owner/test-repo');
  });

  test('Desktop Viewport (1280x800) displays sidebar and hides bottom nav', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });

    const sidebar = page.locator('aside');
    const bottomNav = page.locator('nav.lg\\:hidden');

    await expect(sidebar).toBeVisible();
    await expect(bottomNav).not.toBeVisible();
  });

  test('Tablet Viewport (768x1024) hides sidebar and displays bottom nav', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });

    const sidebar = page.locator('aside');
    const bottomNav = page.locator('nav.lg\\:hidden');

    await expect(sidebar).not.toBeVisible();
    await expect(bottomNav).toBeVisible();
  });

  test('Mobile Viewport (375x667) renders bottom nav and supports mobile navigation', async ({ page, contributorsPage }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    const sidebar = page.locator('aside');
    const bottomNav = page.locator('nav.lg\\:hidden');

    await expect(sidebar).not.toBeVisible();
    await expect(bottomNav).toBeVisible();

    // Verify bottom nav items are visible and clickable
    const contributorsLink = bottomNav.locator('a', { hasText: 'Contributors' });
    await expect(contributorsLink).toBeVisible();
    await contributorsLink.click();

    // Verify navigation was successful on mobile
    await page.waitForURL('**/test-owner/test-repo/contributors');
    await expect(contributorsPage.headerTitle).toContainText('Contributors');
  });
});
