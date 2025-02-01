# API Documentation

## Overview

The Vinco API provides programmatic access to wine production management functionality. The API follows RESTful principles and uses JSON for request and response payloads.

## Authentication

All API endpoints require authentication. Use token-based authentication by including the token in the Authorization header:

```
Authorization: Token your-api-token
```

To obtain a token, send a POST request to `/api/token/`:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

## Endpoints

### Vineyards

#### List Vineyards
```
GET /api/vineyards/
```

Query Parameters:
- `search`: Search term for filtering vineyards
- `ownership_type`: Filter by ownership type (owned/supplied)
- `grape_variety`: Filter by grape variety

Response:
```json
{
    "count": 10,
    "next": "http://api.example.com/api/vineyards/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "North Valley Vineyard",
            "location": "Napa Valley",
            "grape_variety": "Cabernet Sauvignon",
            "area": 25.5,
            "ownership_type": "owned",
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        }
    ]
}
```

#### Get Vineyard Details
```
GET /api/vineyards/{id}/
```

Response:
```json
{
    "id": 1,
    "name": "North Valley Vineyard",
    "location": "Napa Valley",
    "grape_variety": "Cabernet Sauvignon",
    "area": 25.5,
    "ownership_type": "owned",
    "supplier": null,
    "cadastral_county": "Napa",
    "arkod_id": "123456",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
}
```

### Harvests

#### List Harvests
```
GET /api/harvests/
```

Query Parameters:
- `vineyard`: Filter by vineyard ID
- `start_date`: Filter by harvest date (start)
- `end_date`: Filter by harvest date (end)
- `status`: Filter by allocation status

Response:
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "vineyard": {
                "id": 1,
                "name": "North Valley Vineyard"
            },
            "date": "2025-01-15",
            "quantity": 1000.0,
            "juice_yield": 700.0,
            "remaining_juice": 500.0,
            "notes": "Early morning harvest",
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        }
    ]
}
```

#### Get Harvest Details
```
GET /api/harvests/{id}/
```

Response:
```json
{
    "id": 1,
    "vineyard": {
        "id": 1,
        "name": "North Valley Vineyard",
        "grape_variety": "Cabernet Sauvignon"
    },
    "date": "2025-01-15",
    "quantity": 1000.0,
    "juice_yield": 700.0,
    "remaining_juice": 500.0,
    "notes": "Early morning harvest",
    "allocations": [
        {
            "id": 1,
            "tank": {
                "id": 1,
                "name": "Tank A1"
            },
            "allocated_volume": 200.0,
            "created_at": "2025-01-15T11:30:00Z"
        }
    ],
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
}
```

### Juice Allocations

#### Create Allocation
```
POST /api/harvests/{harvest_id}/allocations/
```

Request:
```json
{
    "tank": 1,
    "allocated_volume": 200.0
}
```

Response:
```json
{
    "id": 1,
    "harvest": 1,
    "tank": {
        "id": 1,
        "name": "Tank A1"
    },
    "allocated_volume": 200.0,
    "created_at": "2025-01-15T11:30:00Z"
}
```

#### Delete Allocation
```
DELETE /api/allocations/{id}/
```

### Error Responses

The API uses standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error Response Format:
```json
{
    "error": {
        "code": "validation_error",
        "message": "Invalid input data",
        "details": {
            "field_name": [
                "Error message"
            ]
        }
    }
}
```

## Rate Limiting

API requests are rate limited to:
- 100 requests per minute for authenticated users
- 1000 requests per hour per API token

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1580547930
```

## Pagination

List endpoints are paginated with 20 items per page by default. Use the `page` and `page_size` parameters to control pagination:

```
GET /api/vineyards/?page=2&page_size=10
```

## Filtering and Sorting

Most list endpoints support filtering and sorting:

```
GET /api/harvests/?vineyard=1&ordering=-date
```

Common filter parameters:
- `created_after`: Filter by creation date
- `updated_after`: Filter by update date
- `ordering`: Sort results (prefix with - for descending)

## Versioning

The API is versioned through the URL:
```
/api/v1/vineyards/
```

When making breaking changes, a new version will be released and the old version will be maintained for a deprecation period.
