import { test, expect } from '../fixtures/testFixtures';

test.describe('Landing Page Layout & Elements', () => {
  test.beforeEach(async ({ landingPage }) => {
    await landingPage.navigate();
  });

  test('Page loads successfully and displays branding logo', async ({ landingPage }) => {
    await expect(landingPage.logo).toBeVisible();
    await expect(landingPage.logo).toContainText('GitScope');
  });

  test('Search input field and Analyze button are visible with correct placeholders/text', async ({ landingPage }) => {
    await expect(landingPage.searchInput).toBeVisible();
    await expect(landingPage.searchInput).toHaveAttribute('placeholder', 'https://github.com/vercel/next.js');
    await expect(landingPage.analyzeButton).toBeVisible();
    await expect(landingPage.analyzeButton).toHaveText('Analyze');
  });

  test('Feature section cards render correctly', async ({ landingPage }) => {
    const cardsCount = await landingPage.featureCards.count();
    expect(cardsCount).toBe(6);
    
    // Check first card text structure
    const firstCard = landingPage.featureCards.first();
    await expect(firstCard.locator('h3')).toBeVisible();
    await expect(firstCard.locator('p')).toBeVisible();
  });

  test('Quick analysis helper buttons populate the search input field', async ({ landingPage }) => {
    // Click on vercel/next.js helper
    await landingPage.quickLinkVercel.click();
    await expect(landingPage.searchInput).toHaveValue('vercel/next.js');

    // Click on microsoft/vscode helper
    await landingPage.quickLinkVSCode.click();
    await expect(landingPage.searchInput).toHaveValue('microsoft/vscode');
  });
});
