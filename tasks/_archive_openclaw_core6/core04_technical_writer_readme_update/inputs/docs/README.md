# Invoice API

## Create Invoice

Endpoint: `POST /v1/invoices`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user | string | Yes | Username |
| items_text | string | Yes | Items as text |
| amount | number | Yes | Invoice amount |

## List Invoices

Endpoint: `GET /v1/invoices`

Returns all invoices for the user.
