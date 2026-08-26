import { defineConfig } from "allure";

const failedOrBroken = ["failed", "broken"];
const historyPath =
  process.env.ALLURE_HISTORY_PATH?.trim() ||
  "./test-results/allure-history/history.jsonl";

const minimalCharts = [
  {
    type: "currentStatus",
    title: "Joriy holat",
  },
  {
    type: "statusDynamics",
    title: "Natijalar dinamikasi",
  },
];

export default defineConfig({
  name: "Smartup test hisoboti",
  output: "./test-results/allure-report",
  historyPath,
  historyLimit: 50,
  appendHistory: true,
  hideLabels: [
    "host",
    "thread",
    "framework",
    "language",
    "package",
    "parentSuite",
    "suite",
    "subSuite",
  ],
  categories: {
    rules: [
      {
        id: "test-synchronization-defects",
        name: "Test sinxronizatsiyasi muammosi",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[TEST_SYNCHRONIZATION_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "navigation-timeouts",
        name: "Navigatsiya vaqti tugadi",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[NAVIGATION_TIMEOUT_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "locator-or-ui-state-defects",
        name: "Locator yoki UI holati muammosi",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[LOCATOR_OR_UI_STATE_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "download-defects",
        name: "Fayl yuklab olish muammosi",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[DOWNLOAD_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "verification-defects",
        name: "Natijani tekshirish muammosi",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[VERIFICATION_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "environment-or-precondition-defects",
        name: "Muhit yoki precondition muammosi",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[ENVIRONMENT_PRECONDITION_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "unclassified-test-defects",
        name: "Tasniflanmagan test muammosi",
        matchers: {
          statuses: failedOrBroken,
          message: /.*\[UNCLASSIFIED_TEST_DEFECT\].*/s,
        },
        groupByMessage: false,
      },
      {
        id: "ignored-tests",
        name: "Bajarilmagan testlar",
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
        reportName: "Smartup test hisoboti",
        reportLanguage: "en",
        theme: "light",
        groupBy: ["epic", "feature", "story"],
        filter: (testResult) => testResult.fullName !== "system.test.summary",
        defaultSection: "report",
        charts: minimalCharts,
        stepTreeExpansion: "expand_failed_only",
        defaultSortBy: "order,asc",
        singleFile: false,
      },
    },
  },
});
