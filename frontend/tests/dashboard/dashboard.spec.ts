import { test, expect } from '../fixtures/testFixtures';

test.describe('Repository Dashboard Verification', () => {
  test.beforeEach(async ({ page, mockApi }) => {
    // Navigate directly to the repository dashboard
    await page.goto('/test-owner/test-repo');
  });

  test('Displays correct repository header and description', async ({ dashboardPage }) => {
    await expect(dashboardPage.headerTitle).toBeVisible();
    await expect(dashboardPage.headerTitle).toContainText('test-owner/test-repo');
    
    // Check repository details card is visible
    await expect(dashboardPage.repoCard).toBeVisible();
    await expect(dashboardPage.repoCard).toContainText('A gorgeous mock repository for testing GitScope frontend in isolation.');
  });

  test('Displays correct values for all stats cards', async ({ dashboardPage }) => {
    // Check Stars Card
    const starsValue = await dashboardPage.getStatValue('Stars');
    expect(starsValue?.trim()).toBe('128');

    // Check Forks Card
    const forksValue = await dashboardPage.getStatValue('Forks');
    expect(forksValue?.trim()).toBe('32');

    // Check Watchers Card
    const watchersValue = await dashboardPage.getStatValue('Watchers');
    expect(watchersValue?.trim()).toBe('64');

    // Check Open Issues Card
    const issuesValue = await dashboardPage.getStatValue('Open Issues');
    expect(issuesValue?.trim()).toBe('8');

    // Check Language Card
    const langValue = await dashboardPage.getStatValue('Language');
    expect(langValue?.trim()).toBe('TypeScript');
  });

  test('Renders analytics charts container', async ({ dashboardPage }) => {
    await expect(dashboardPage.chartsContainer).toBeVisible();
  });
});
