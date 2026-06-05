# API Reference

## Create Invoice

**Endpoint:** `POST /v1/invoices`  <!-- BUG: still says v1 -->

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| user | string | Yes | Username |
| items_text | string | Yes | Items as comma-separated text |

## List Invoices

**Endpoint:** `GET /v1/invoices`

No parameters documented.  <!-- BUG: missing query params -->
