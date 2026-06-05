# Metric Definitions

## MRR (Monthly Recurring Revenue)
Sum of all active subscription mrr values at end of week.
Active = subscription with no end_date OR end_date after week end date (2025-08-10).

## new_mrr
Sum of mrr for subscriptions that started during the week (2025-08-04 to 2025-08-10).

## churned_mrr
Sum of mrr for subscriptions that ended during the week (2025-08-04 to 2025-08-10).

## net_mrr_growth
new_mrr - churned_mrr

## Week
2025-W32 = 2025-08-04 to 2025-08-10
