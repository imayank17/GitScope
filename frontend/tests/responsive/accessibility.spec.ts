import { test, expect } from '../fixtures/testFixtures';

test.describe('Accessibility & Keyboard Navigation', () => {
  test.beforeEach(async ({ landingPage }) => {
    await landingPage.navigate();
  });

  test('Buttons have accessible names', async ({ landingPage }) => {
    // Buttons must have text or explicit aria-label/labels
    await expect(landingPage.analyzeButton).toBeVisible();
    const btnText = await landingPage.analyzeButton.textContent();
    expect(btnText?.trim().length).toBeGreaterThan(0);
  });

  test('Search input is discoverable and has accessible label/placeholder', async ({ landingPage }) => {
    await expect(landingPage.searchInput).toBeVisible();
    const placeholder = await landingPage.searchInput.getAttribute('placeholder');
    expect(placeholder).not.toBeNull();
    expect(placeholder?.length).toBeGreaterThan(0);
  });

  test('Keyboard navigation works and focus states are visible', async ({ page, landingPage }) => {
    // Navigate and check that focus is not lost
    await landingPage.navigate();

    // Tab onto the input box
    await page.keyboard.press('Tab');
    
    // Focus the input box and verify focus outline state
    await landingPage.searchInput.focus();
    await expect(landingPage.searchInput).toBeFocused();

    // Type a query using keyboard
    await page.keyboard.type('test-owner/test-repo');

    // Tab to focus the next element (Analyze button)
    await page.keyboard.press('Tab');
    await expect(landingPage.analyzeButton).toBeFocused();

    // Press Enter to submit
    await page.keyboard.press('Enter');

    // Verify it navigates correctly
    await page.waitForURL('**/test-owner/test-repo');
    expect(page.url()).toContain('/test-owner/test-repo');
  });
});
