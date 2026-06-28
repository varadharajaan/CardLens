// Response DTOs mirroring the CardLens backend (snake_case as returned by the API).

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages?: number;
}

export interface PortfolioCounts {
  cards: number;
  card_accounts: number;
  bank_accounts: number;
  debit_cards: number;
  statements: number;
}

export interface DashboardOverview {
  counts: PortfolioCounts;
  billing_groups: number;
  total_outstanding_due: number;
  total_minimum_due: number;
  total_reward_points: number;
  total_cashback: number;
  nearest_due_date: string | null;
  currency: string;
}

export interface RewardFormatTotal {
  reward_format: string;
  reward_points: number;
  cashback: number;
  statements: number;
}

export interface RewardsSummary {
  total_reward_points: number;
  total_cashback: number;
  estimated_value_inr: number;
  by_format: RewardFormatTotal[];
}

export interface Milestone {
  key: string;
  label: string;
  reward_format: string;
  threshold: number;
  current: number;
  progress_pct: number;
  achieved: boolean;
}

export interface Anomaly {
  rule: string;
  severity: string;
  message: string;
  card_name: string;
  last4: string;
  due_date: string | null;
  amount: number | null;
}

export interface Card {
  id: string;
  account_id: string | null;
  bank: string;
  card_name: string;
  last4: string;
  network: string | null;
  registry_key: string | null;
  reward_format: string | null;
  is_primary: boolean;
  status: string;
}

export interface CardAccount {
  id: string;
  bank: string;
  display_name: string;
  last4_primary: string | null;
  credit_limit: number | null;
  statement_day: number | null;
  status: string;
}

export interface CardAccountDetail {
  account: CardAccount;
  variants: Card[];
}

export interface DebitCard {
  id: string;
  bank_account_id: string;
  card_name: string;
  last4: string;
  network: string | null;
  reward_format: string | null;
  is_primary: boolean;
  status: string;
}

export interface BankAccount {
  id: string;
  bank: string;
  account_type: string;
  display_name: string;
  last4: string | null;
  ifsc: string | null;
  balance: number | null;
  status: string;
}

export interface BankAccountDetail {
  account: BankAccount;
  debit_cards: DebitCard[];
}

export interface Statement {
  id: string;
  card_id: string | null;
  account_id: string | null;
  bank: string;
  card_name: string;
  last4: string;
  statement_date: string | null;
  due_date: string | null;
  total_due: number | null;
  minimum_due: number | null;
  reward_points_closing: number | null;
  cashback_earned: number | null;
  reward_type: string | null;
  reward_parse_status: string;
}
