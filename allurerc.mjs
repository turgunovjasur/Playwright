import { defineConfig } from "allure";

const failedOrBroken = ["failed", "broken"];
const historyPath =
  process.env.ALLURE_HISTORY_PATH?.trim() ||
  "./test-results/allure-history/history.jsonl";

export default defineConfig({
  name: "Smartup Smoke Tests",
  output: "./test-results/allure-report",
  historyPath,
  historyLimit: 50,
  appendHistory: true,
  categories: {
    rules: [
      {
        id: "test-synchronization-defects",
        name: "Test synchronization defects",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[TEST_SYNCHRONIZATION_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "navigation-timeouts",
        name: "Navigation timeouts",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[NAVIGATION_TIMEOUT_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "locator-or-ui-state-defects",
        name: "Locator or UI state defects",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[LOCATOR_OR_UI_STATE_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "download-defects",
        name: "Download defects",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[DOWNLOAD_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "verification-defects",
        name: "Verification defects",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[VERIFICATION_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "environment-or-precondition-defects",
        name: "Environment or precondition defects",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[ENVIRONMENT_PRECONDITION_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "unclassified-test-defects",
        name: "Unclassified test defects",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[UNCLASSIFIED_TEST_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "ignored-tests",
        name: "Ignored tests",
        matchers: {
          statuses: ["skipped"],
        },
        groupByMessage: false,
      },
    ],
  },
  plugins: {
    awesome: {
      options: {
        reportName: "Smartup Smoke Tests",
        reportLanguage: "en",
        groupBy: ["epic", "feature", "story"],
        singleFile: false,
      },
    },
  },
});
