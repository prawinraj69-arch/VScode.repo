import * as dotenv from 'dotenv';

const env = process.env.ENV || 'sit';
dotenv.config({ path: `.env.${env}` });

export const ENV = {
  baseURL:                    process.env.BASE_URL                     || 'https://app.powerbi.com',
  workspaceName:              process.env.WORKSPACE_NAME               || 'CMC SIT',
  workspaceLabel:             process.env.WORKSPACE_LABEL              || 'SIT',
  groupId:                    process.env.POWER_BI_GROUP_ID            || '',
  stabilityReportId:          process.env.STABILITY_REPORT_ID          || '',
  stabilityHomePageId:        process.env.STABILITY_HOME_PAGE_ID       || '',
  docDashboardPageId:         process.env.DOC_DASHBOARD_PAGE_ID        || '',
  p81BatchSummaryPageId:      process.env.P81_BATCH_SUMMARY_PAGE_ID    || '',
  p81ProtocolSummaryPageId:   process.env.P81_PROTOCOL_SUMMARY_PAGE_ID || '',
  p83StabilityResultsPageId:  process.env.P83_STABILITY_RESULTS_PAGE_ID || '',

  /** Stability disclaimer / landing page (first load) */
  get stabilityDisclaimerUrl(): string {
    return `${this.baseURL}/groups/${this.groupId}/reports/${this.stabilityReportId}/22bfa36c89ab9287172e?experience=power-bi`;
  },

  /** CMC Data Hub Home page (after accepting disclaimer) */
  get stabilityHomeUrl(): string {
    return `${this.baseURL}/groups/${this.groupId}/reports/${this.stabilityReportId}/${this.stabilityHomePageId}?experience=power-bi`;
  },

  /** Document Dashboard — table selector page */
  get docDashboardUrl(): string {
    return `${this.baseURL}/groups/${this.groupId}/reports/${this.stabilityReportId}/${this.docDashboardPageId}?experience=power-bi`;
  },

  /** P.8.1 Stability Batch Summary for Drug Product */
  get p81BatchSummaryUrl(): string {
    return `${this.baseURL}/groups/${this.groupId}/reports/${this.stabilityReportId}/${this.p81BatchSummaryPageId}?experience=power-bi`;
  },

  /** P.8.1 Stability Protocol Summary for Drug Product */
  get p81ProtocolSummaryUrl(): string {
    return `${this.baseURL}/groups/${this.groupId}/reports/${this.stabilityReportId}/${this.p81ProtocolSummaryPageId}?experience=power-bi`;
  },

  /** P.8.3 Stability Results for Drug Product */
  get p83StabilityResultsUrl(): string {
    return `${this.baseURL}/groups/${this.groupId}/reports/${this.stabilityReportId}/${this.p83StabilityResultsPageId}?experience=power-bi`;
  },
};
