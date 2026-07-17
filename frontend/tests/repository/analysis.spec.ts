import { test, expect } from '../fixtures/testFixtures';

test.describe('Repository Analysis Flow', () => {
  test('Successfully analyzes a repo and navigates to the dashboard', async ({ landingPage, dashboardPage, mockApi, page }) => {
    await landingPage.navigate();

    // Setup mock API and delay it slightly to verify the loading state
    await mockApi.mockDelay('**/api/repositories/analyze', 1000);

    // Enter repository string
    await landingPage.fillSearch('test-owner/test-repo');

    // Trigger analysis
    await landingPage.analyzeButton.click();

    // Verify loading state is active on the button
    await expect(landingPage.analyzeButton).toBeDisabled();
    await expect(landingPage.analyzeButton.locator('svg.animate-spin')).toBeVisible();

    // Verify it navigates to the dashboard page URL
    await page.waitForURL('**/test-owner/test-repo');
    expect(page.url()).toContain('/test-owner/test-repo');

    // Verify dashboard renders successfully
    await expect(dashboardPage.headerTitle).toBeVisible();
    await expect(dashboardPage.headerTitle).toContainText('test-owner/test-repo');
  });

  test('Supports full GitHub URL formats', async ({ landingPage, mockApi, page }) => {
    await landingPage.navigate();

    // Input full URL
    await landingPage.fillSearch('https://github.com/test-owner/test-repo');
    await landingPage.analyzeButton.click();

    // Verify navigation works similarly
    await page.waitForURL('**/test-owner/test-repo');
    expect(page.url()).toContain('/test-owner/test-repo');
  });
});
