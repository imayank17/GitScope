// Mock Data for GitScope E2E Tests

export const mockRepository = {
  id: "d3b07384-d113-4c31-92b5-e51c11005bf3",
  name: "test-repo",
  full_name: "test-owner/test-repo",
  description: "A gorgeous mock repository for testing GitScope frontend in isolation.",
  owner_login: "test-owner",
  owner_avatar_url: "https://avatars.githubusercontent.com/u/9919?v=4",
  html_url: "https://github.com/test-owner/test-repo",
  clone_url: "https://github.com/test-owner/test-repo.git",
  language: "TypeScript",
  default_branch: "main",
  visibility: "public",
  stars: 128,
  forks: 32,
  open_issues: 8,
  watchers: 64,
  topics: ["react", "vite", "playwright", "typescript"],
  created_at: "2026-01-01T12:00:00Z",
  updated_at: "2026-07-01T12:00:00Z"
};

export const mockContributors = {
  items: [
    {
      login: "developer-alice",
      avatar_url: "https://avatars.githubusercontent.com/u/101?v=4",
      html_url: "https://github.com/developer-alice",
      contributions: 150
    },
    {
      login: "developer-bob",
      avatar_url: "https://avatars.githubusercontent.com/u/102?v=4",
      html_url: "https://github.com/developer-bob",
      contributions: 45
    },
    {
      login: "developer-charlie",
      avatar_url: "https://avatars.githubusercontent.com/u/103?v=4",
      html_url: "https://github.com/developer-charlie",
      contributions: 12
    }
  ],
  page: 1,
  per_page: 30,
  total_pages: 1
};

export const mockCommits = {
  items: [
    {
      sha: "c0ffee112233445566778899aabbccddeeff0011",
      message: "feat: add interactive charts to dashboard layout",
      author_name: "Alice Smith",
      author_email: "alice@example.com",
      author_date: "2026-07-16T15:30:00Z",
      committer_name: "Alice Smith",
      html_url: "https://github.com/test-owner/test-repo/commit/c0ffee112233"
    },
    {
      sha: "deadbeef445566778899aabbccddeeff00112233",
      message: "fix: resolve re-render cycle on filter change",
      author_name: "Bob Jones",
      author_email: "bob@example.com",
      author_date: "2026-07-15T11:20:00Z",
      committer_name: "Bob Jones",
      html_url: "https://github.com/test-owner/test-repo/commit/deadbeef4455"
    },
    {
      sha: "bada550066778899aabbccddeeff001122334455",
      message: "docs: update API endpoints in readme",
      author_name: "Charlie Brown",
      author_email: "charlie@example.com",
      author_date: "2026-07-14T09:15:00Z",
      committer_name: "Charlie Brown",
      html_url: "https://github.com/test-owner/test-repo/commit/bada55006677"
    }
  ],
  page: 1,
  per_page: 20,
  total_pages: 1
};

export const mockLanguages = {
  languages: {
    TypeScript: 85000,
    CSS: 12000,
    HTML: 3000
  },
  total_bytes: 100000,
  percentages: {
    TypeScript: 85.0,
    CSS: 12.0,
    HTML: 3.0
  }
};

export const mockPullRequests = {
  open: {
    items: [
      {
        number: 4,
        title: "feat: implement real-time alerts",
        state: "open",
        user_login: "developer-alice",
        created_at: "2026-07-16T18:00:00Z",
        updated_at: "2026-07-17T09:00:00Z",
        html_url: "https://github.com/test-owner/test-repo/pull/4",
        labels: ["enhancement", "ui"],
        merged_at: null,
        draft: false
      }
    ],
    page: 1,
    per_page: 20,
    total_pages: 1
  },
  closed: {
    items: [
      {
        number: 2,
        title: "refactor: optimize rendering loop in charts",
        state: "closed",
        user_login: "developer-bob",
        created_at: "2026-07-10T10:00:00Z",
        updated_at: "2026-07-12T14:30:00Z",
        html_url: "https://github.com/test-owner/test-repo/pull/2",
        labels: ["performance"],
        merged_at: "2026-07-12T14:30:00Z",
        draft: false
      }
    ],
    page: 1,
    per_page: 20,
    total_pages: 1
  },
  all: {
    items: [
      {
        number: 4,
        title: "feat: implement real-time alerts",
        state: "open",
        user_login: "developer-alice",
        created_at: "2026-07-16T18:00:00Z",
        updated_at: "2026-07-17T09:00:00Z",
        html_url: "https://github.com/test-owner/test-repo/pull/4",
        labels: ["enhancement", "ui"],
        merged_at: null,
        draft: false
      },
      {
        number: 2,
        title: "refactor: optimize rendering loop in charts",
        state: "closed",
        user_login: "developer-bob",
        created_at: "2026-07-10T10:00:00Z",
        updated_at: "2026-07-12T14:30:00Z",
        html_url: "https://github.com/test-owner/test-repo/pull/2",
        labels: ["performance"],
        merged_at: "2026-07-12T14:30:00Z",
        draft: false
      }
    ],
    page: 1,
    per_page: 20,
    total_pages: 1
  }
};

export const mockIssues = {
  open: {
    items: [
      {
        number: 12,
        title: "bug: tooltips clipping on small screens",
        state: "open",
        user_login: "developer-charlie",
        created_at: "2026-07-15T20:00:00Z",
        updated_at: "2026-07-16T11:00:00Z",
        html_url: "https://github.com/test-owner/test-repo/issues/12",
        labels: ["bug", "css"],
        comments: 3
      }
    ],
    page: 1,
    per_page: 20,
    total_pages: 1
  },
  closed: {
    items: [
      {
        number: 5,
        title: "build: update vite dependencies",
        state: "closed",
        user_login: "developer-alice",
        created_at: "2026-07-02T08:00:00Z",
        updated_at: "2026-07-03T16:00:00Z",
        html_url: "https://github.com/test-owner/test-repo/issues/5",
        labels: ["dependencies"],
        comments: 1
      }
    ],
    page: 1,
    per_page: 20,
    total_pages: 1
  },
  all: {
    items: [
      {
        number: 12,
        title: "bug: tooltips clipping on small screens",
        state: "open",
        user_login: "developer-charlie",
        created_at: "2026-07-15T20:00:00Z",
        updated_at: "2026-07-16T11:00:00Z",
        html_url: "https://github.com/test-owner/test-repo/issues/12",
        labels: ["bug", "css"],
        comments: 3
      },
      {
        number: 5,
        title: "build: update vite dependencies",
        state: "closed",
        user_login: "developer-alice",
        created_at: "2026-07-02T08:00:00Z",
        updated_at: "2026-07-03T16:00:00Z",
        html_url: "https://github.com/test-owner/test-repo/issues/5",
        labels: ["dependencies"],
        comments: 1
      }
    ],
    page: 1,
    per_page: 20,
    total_pages: 1
  }
};

export const mockSyncStatus = {
  repository_id: "d3b07384-d113-4c31-92b5-e51c11005bf3",
  status: "COMPLETED",
  last_synced_at: "2026-07-17T06:00:00Z",
  error: null
};

export const mockMetricsHistory = [
  {
    date: "2026-07-10",
    stars: 120,
    forks: 30,
    open_issues: 10,
    watchers: 60,
    commit_count: 85,
    pull_request_count: 8
  },
  {
    date: "2026-07-17",
    stars: 128,
    forks: 32,
    open_issues: 8,
    watchers: 64,
    commit_count: 102,
    pull_request_count: 10
  }
];
