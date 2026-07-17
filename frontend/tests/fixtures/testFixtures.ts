import { test as base } from '@playwright/test';
import { LandingPage } from '../pages/LandingPage';
import { RepositoryDashboardPage } from '../pages/RepositoryDashboardPage';
import { ContributorsPage } from '../pages/ContributorsPage';
import { CommitsPage } from '../pages/CommitsPage';
import { IssuesPage } from '../pages/IssuesPage';
import { PullRequestsPage } from '../pages/PullRequestsPage';
import { SyncPage } from '../pages/SyncPage';
import * as mockData from './mockData';

// Helper class to manage API mocking
export class MockApiHelper {
  private page: any;
  public repoData: any = JSON.parse(JSON.stringify(mockData.mockRepository));
  public contributorsData: any = JSON.parse(JSON.stringify(mockData.mockContributors));
  public commitsData: any = JSON.parse(JSON.stringify(mockData.mockCommits));
  public languagesData: any = JSON.parse(JSON.stringify(mockData.mockLanguages));
  public pullsData: any = JSON.parse(JSON.stringify(mockData.mockPullRequests));
  public issuesData: any = JSON.parse(JSON.stringify(mockData.mockIssues));
  public syncStatusData: any = JSON.parse(JSON.stringify(mockData.mockSyncStatus));
  public metricsHistoryData: any = JSON.parse(JSON.stringify(mockData.mockMetricsHistory));

  constructor(page: any) {
    this.page = page;
  }

  async setupDefaultMocks() {
    // Mock POST /api/repositories/analyze
    await this.page.route('**/api/repositories/analyze', async (route: any) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(this.repoData),
      });
    });

    // Mock GET /api/github/*/*
    await this.page.route(/\/api\/github\/[^/]+\/[^/]+$/, async (route: any) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(this.repoData),
      });
    });

    // Mock GET /api/repositories/*/*/contributors
    await this.page.route(/\/api\/repositories\/[^/]+\/[^/]+\/contributors/, async (route: any) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(this.contributorsData),
      });
    });

    // Mock GET /api/repositories/*/*/commits
    await this.page.route(/\/api\/repositories\/[^/]+\/[^/]+\/commits/, async (route: any) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(this.commitsData),
      });
    });

    // Mock GET /api/repositories/*/*/languages
    await this.page.route(/\/api\/repositories\/[^/]+\/[^/]+\/languages/, async (route: any) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(this.languagesData),
      });
    });

    // Mock GET /api/repositories/*/*/pulls
    await this.page.route(/\/api\/repositories\/[^/]+\/[^/]+\/pulls/, async (route: any) => {
      const url = new URL(route.request().url());
      const state = url.searchParams.get('state') || 'open';
      const responseBody = this.pullsData[state] || this.pullsData.all;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(responseBody),
      });
    });

    // Mock GET /api/repositories/*/*/issues
    await this.page.route(/\/api\/repositories\/[^/]+\/[^/]+\/issues/, async (route: any) => {
      const url = new URL(route.request().url());
      const state = url.searchParams.get('state') || 'open';
      const responseBody = this.issuesData[state] || this.issuesData.all;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(responseBody),
      });
    });

    // Mock POST /api/repositories/*/refresh
    await this.page.route(/\/api\/repositories\/[^/]+\/refresh/, async (route: any) => {
      await route.fulfill({
        status: 202,
        contentType: 'application/json',
        body: JSON.stringify({
          repository_id: this.repoData.id,
          status: 'SYNCING',
          message: 'Background synchronization successfully triggered.',
        }),
      });
    });

    // Mock GET /api/repositories/*/sync-status
    await this.page.route(/\/api\/repositories\/[^/]+\/sync-status/, async (route: any) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(this.syncStatusData),
      });
    });

    // Mock GET /api/repositories/*/metrics/history
    await this.page.route(/\/api\/repositories\/[^/]+\/metrics\/history/, async (route: any) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(this.metricsHistoryData),
      });
    });
  }

  async mockError(urlPattern: string | RegExp, status: number, detailMessage: string) {
    await this.page.route(urlPattern, async (route: any) => {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify({ detail: detailMessage }),
      });
    });
  }

  async mockNetworkTimeout(urlPattern: string | RegExp) {
    await this.page.route(urlPattern, async (route: any) => {
      // Abort request to simulate network disconnect/timeout
      await route.abort('timedout');
    });
  }

  async mockDelay(urlPattern: string | RegExp, delayMs: number, responseData?: any) {
    await this.page.route(urlPattern, async (route: any) => {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
      if (responseData) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(responseData),
        });
      } else {
        // Fallback to suitable mock data based on the route pattern
        const patternStr = urlPattern.toString();
        let data = this.repoData;
        if (patternStr.includes('contributors')) data = this.contributorsData;
        else if (patternStr.includes('commits')) data = this.commitsData;
        else if (patternStr.includes('languages')) data = this.languagesData;
        else if (patternStr.includes('pulls')) data = this.pullsData.all;
        else if (patternStr.includes('issues')) data = this.issuesData.all;

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(data),
        });
      }
    });
  }
}

// Define the custom fixtures type
interface TestFixtures {
  mockApi: MockApiHelper;
  landingPage: LandingPage;
  dashboardPage: RepositoryDashboardPage;
  contributorsPage: ContributorsPage;
  commitsPage: CommitsPage;
  issuesPage: IssuesPage;
  pullRequestsPage: PullRequestsPage;
  syncPage: SyncPage;
}

// Extend base test
export const test = base.extend<TestFixtures>({
  mockApi: [async ({ page }, use) => {
    const helper = new MockApiHelper(page);
    await helper.setupDefaultMocks();
    await use(helper);
  }, { auto: true }],

  landingPage: async ({ page }, use) => {
    await use(new LandingPage(page));
  },

  dashboardPage: async ({ page }, use) => {
    await use(new RepositoryDashboardPage(page));
  },

  contributorsPage: async ({ page }, use) => {
    await use(new ContributorsPage(page));
  },

  commitsPage: async ({ page }, use) => {
    await use(new CommitsPage(page));
  },

  issuesPage: async ({ page }, use) => {
    await use(new IssuesPage(page));
  },

  pullRequestsPage: async ({ page }, use) => {
    await use(new PullRequestsPage(page));
  },

  syncPage: async ({ page }, use) => {
    await use(new SyncPage(page));
  },
});

export { expect } from '@playwright/test';
