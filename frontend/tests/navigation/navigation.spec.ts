import { test, expect } from '../fixtures/testFixtures';

test.describe('Sidebar Navigation & Routing', () => {
  test.beforeEach(async ({ page, mockApi }) => {
    await page.goto('/test-owner/test-repo');
  });

  test('Seamlessly navigates between sub-pages via sidebar links', async ({ page, dashboardPage, contributorsPage, commitsPage, issuesPage, pullRequestsPage, syncPage }) => {
    // 1. Navigate to Contributors
    await dashboardPage.navigateSidebar('Contributors');
    await page.waitForURL('**/test-owner/test-repo/contributors');
    await expect(contributorsPage.headerTitle).toContainText('Contributors');
    await expect(contributorsPage.contributorCards.first()).toBeVisible();

    // 2. Navigate to Commits
    await dashboardPage.navigateSidebar('Commits');
    await page.waitForURL('**/test-owner/test-repo/commits');
    await expect(commitsPage.headerTitle).toContainText('Commits');
    await expect(commitsPage.commitCards.first()).toBeVisible();

    // 3. Navigate to Issues
    await dashboardPage.navigateSidebar('Issues');
    await page.waitForURL('**/test-owner/test-repo/issues');
    await expect(issuesPage.headerTitle).toContainText('Issues');
    await expect(issuesPage.issueCards.first()).toBeVisible();

    // 4. Navigate to Pull Requests
    await dashboardPage.navigateSidebar('Pull Requests');
    await page.waitForURL('**/test-owner/test-repo/pulls');
    await expect(pullRequestsPage.headerTitle).toContainText('Pull Requests');
    await expect(pullRequestsPage.prCards.first()).toBeVisible();

    // 5. Navigate to Sync
    await dashboardPage.navigateSidebar('Sync');
    await page.waitForURL('**/test-owner/test-repo/sync');
    await expect(syncPage.headerTitle).toContainText('Synchronization');

    // 6. Navigate back to Overview
    await dashboardPage.navigateSidebar('Overview');
    await page.waitForURL(/\/test-owner\/test-repo\/?$/);
    await expect(dashboardPage.headerTitle).toContainText('test-owner/test-repo');
  });
});
