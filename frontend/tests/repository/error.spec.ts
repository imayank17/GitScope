import { test, expect } from '../fixtures/testFixtures';

test.describe('Error Handling & Resilience', () => {
  test('Handles invalid repository format error (422) on landing page', async ({ landingPage, mockApi }) => {
    await landingPage.navigate();

    // Mock 422 response
    const errorMessage = "Invalid repository format. Use 'owner/repo' or 'https://github.com/owner/repo'.";
    await mockApi.mockError('**/api/repositories/analyze', 422, errorMessage);

    await landingPage.analyzeRepository('invalid-repo-format');

    // Verify error is displayed on page
    const displayedError = await landingPage.getErrorMessage();
    expect(displayedError).toBe(errorMessage);
  });

  test('Handles repository not found error (404) on landing page', async ({ landingPage, mockApi }) => {
    await landingPage.navigate();

    // Mock 404 response
    const errorMessage = "Repository not found";
    await mockApi.mockError('**/api/repositories/analyze', 404, errorMessage);

    await landingPage.analyzeRepository('not-found/repo');

    // Verify error is displayed on page
    const displayedError = await landingPage.getErrorMessage();
    expect(displayedError).toBe(errorMessage);
  });

  test('Handles backend server or network unavailable (disconnect)', async ({ page, mockApi }) => {
    // Abort backend call to simulate server offline/network error
    await mockApi.mockNetworkTimeout(/\/api\/github\/[^/]+\/[^/]+$/);

    await page.goto('/test-owner/test-repo');

    // Verify ErrorState is rendered using container-scoped locator
    const errorText = page.locator('div.flex-col.items-center p.text-sm');
    await expect(errorText).toBeVisible();
    await expect(errorText).toContainText('Network error');
  });

  test('Recovers from failures when clicking the retry button', async ({ page, mockApi, dashboardPage }) => {
    let shouldFail = true;

    // Route GET /api/github/test-owner/test-repo
    await page.route(/\/api\/github\/[^/]+\/[^/]+$/, async (route) => {
      if (shouldFail) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal Server Error' }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockApi.repoData),
        });
      }
    });

    // Go directly to repo dashboard
    await page.goto('/test-owner/test-repo');

    // First call fails, verify the 'Try again' button is visible
    const retryButton = page.getByRole('button', { name: 'Try again', exact: true });
    await expect(retryButton).toBeVisible();

    // Toggle failure state to false before triggering retry
    shouldFail = false;

    // Click 'Try again'
    await retryButton.click();

    // Verify it recovers and loads stats card
    const starsValue = await dashboardPage.getStatValue('Stars');
    expect(starsValue?.trim()).toBe('128');
    await expect(retryButton).not.toBeVisible();
  });
});
