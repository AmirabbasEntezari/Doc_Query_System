# 🔌 Smart Document Q&A System — API Documentation

This document describes all available REST API endpoints for the Smart Document Q&A System. The API enables document management, RAG-powered question answering, chat session tracking, and AI-generated tag management.

All endpoints are prefixed with:

```text
/api/
```

---

# 🔐 Base Configuration

### Base URL

```text
http://localhost:8000/api/
```

or

```text
http://127.0.0.1:8000/api/
```

### Headers

```http
Content-Type: application/json
```

### Authentication

Currently, the API is open for development and testing purposes.

Future versions may support:

```http
Authorization: Bearer <token>
```

---

# 📂 Document Management

## 📥 List Documents

Retrieve all uploaded documents.

### Endpoint

```http
GET /api/documents/
```

### Success Response

**Status:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Project Overview",
    "file": "/media/documents/project_overview.docx",
    "content": "Extracted text content from the document...",
    "created_at": "2026-06-03T14:22:00Z",
    "updated_at": "2026-06-03T14:25:00Z"
  }
]
```

---

## 📤 Upload Document

Upload a new Microsoft Word document.

### Endpoint

```http
POST /api/documents/
```

### Request Type

```text
multipart/form-data
```

### Parameters

| Field | Type       | Required | Description             |
| ----- | ---------- | -------- | ----------------------- |
| title | string     | Yes      | Document title          |
| file  | .docx file | Yes      | Microsoft Word document |

### Example Request

```text
title: Project Overview
file: project_overview.docx
```

### Success Response

**Status:** `201 Created`

```json
{
  "id": 1,
  "title": "Project Overview",
  "file": "/media/documents/project_overview.docx",
  "content": "Extracted text content...",
  "created_at": "2026-06-03T14:22:00Z",
  "updated_at": "2026-06-03T14:25:00Z"
}
```

---

## 🔍 Retrieve Single Document

Retrieve a document by ID.

### Endpoint

```http
GET /api/documents/<id>/
```

### Example

```http
GET /api/documents/1/
```

### Success Response

**Status:** `200 OK`

```json
{
  "id": 1,
  "title": "Project Overview",
  "file": "/media/documents/project_overview.docx",
  "content": "Extracted text content...",
  "created_at": "2026-06-03T14:22:00Z",
  "updated_at": "2026-06-03T14:25:00Z"
}
```

---

## 🗑 Delete Document

Delete a document permanently.

### Endpoint

```http
DELETE /api/documents/<id>/
```

### Success Response

**Status:** `204 No Content`

---

# 💬 Chat Session & Question Answering

The system uses Retrieval-Augmented Generation (RAG) to answer user questions based on uploaded documents.

---

## 📜 List Chat Sessions

Retrieve all previous chat sessions.

### Endpoint

```http
GET /api/chats/
```

### Success Response

**Status:** `200 OK`

```json
[
  {
    "id": 42,
    "query": "مدل زبان اصلی استفاده شده در این سیستم چیست؟",
    "response": "مدل پیش‌فرض سیستم Google Gemini 2.5 Flash می‌باشد.",
    "target_document": 3,
    "created_at": "2026-06-03T15:30:00Z"
  }
]
```

---

## 🤖 Create New AI Query

Submit a question and receive an AI-generated answer.

### Endpoint

```http
POST /api/chats/
```

---

### Focused Search Mode

Search within a specific document.

#### Request

```json
{
  "query": "ساختار دیتابیس پروژه به چه شکل است؟",
  "target_document": 1
}
```

---

### Global Search Mode

Search across all uploaded documents.

#### Request

```json
{
  "query": "مدل زبان اصلی استفاده شده در این سیستم چیست؟",
  "target_document": null
}
```

---

### Success Response

**Status:** `201 Created`

```json
{
  "id": 42,
  "query": "مدل زبان اصلی استفاده شده در این سیستم چیست؟",
  "response": "با توجه به مستندات، مدل پیش‌فرض سیستم Google Gemini 2.5 Flash می‌باشد.",
  "target_document": 3,
  "created_at": "2026-06-03T15:30:00Z",
  "tags": [
    {
      "id": 5,
      "name": "هوش مصنوعی"
    },
    {
      "id": 12,
      "name": "تنظیمات مدل"
    }
  ]
}
```

### Global Search Behavior

When:

```json
{
  "target_document": null
}
```

the AI automatically:

1. Searches across all indexed documents.
2. Identifies the most relevant source document.
3. Extracts the document ID.
4. Associates the chat session with that document.
5. Returns the detected document ID in the response.

---

## 🔍 Retrieve Single Chat Session

### Endpoint

```http
GET /api/chats/<id>/
```

### Success Response

```json
{
  "id": 42,
  "query": "مدل زبان اصلی استفاده شده در این سیستم چیست؟",
  "response": "مدل پیش‌فرض سیستم Google Gemini 2.5 Flash می‌باشد.",
  "target_document": 3,
  "created_at": "2026-06-03T15:30:00Z",
  "tags": [
    {
      "id": 5,
      "name": "هوش مصنوعی"
    }
  ]
}
```

---

## 🗑 Delete Chat Session

### Endpoint

```http
DELETE /api/chats/<id>/
```

### Success Response

**Status:** `204 No Content`

---

# 🏷️ Tag Management

Tags are generated automatically by the AI based on conversation context.

---

## 📋 List All Tags

Retrieve all unique tags stored in the system.

### Endpoint

```http
GET /api/tags/
```

### Success Response

**Status:** `200 OK`

```json
[
  {
    "id": 1,
    "name": "داکر"
  },
  {
    "id": 2,
    "name": "جنگو"
  },
  {
    "id": 3,
    "name": "هوش مصنوعی"
  }
]
```

---

## 🔍 Retrieve Single Tag

### Endpoint

```http
GET /api/tags/<id>/
```

### Success Response

```json
{
  "id": 1,
  "name": "داکر"
}
```

---

# ⚠️ Error Responses

## Validation Error

**Status:** `400 Bad Request`

```json
{
  "error": "Query field is required."
}
```

---

## Resource Not Found

**Status:** `404 Not Found`

```json
{
  "error": "Document not found."
}
```

---

## AI Provider Error

**Status:** `503 Service Unavailable`

```json
{
  "error": "LLM provider temporarily unavailable."
}
```

This may occur due to:

* OpenRouter rate limits
* Upstream model outages
* Network connectivity issues

---

# 📊 HTTP Status Codes

| Code | Status              | Description                       |
| ---- | ------------------- | --------------------------------- |
| 200  | OK                  | Request completed successfully    |
| 201  | Created             | Resource created successfully     |
| 204  | No Content          | Resource deleted successfully     |
| 400  | Bad Request         | Invalid or missing input data     |
| 404  | Not Found           | Requested resource does not exist |
| 503  | Service Unavailable | AI provider unavailable           |

---

# 🧠 RAG Workflow Summary

1. User uploads one or more `.docx` files.
2. The system extracts document text.
3. Documents are chunked using `RecursiveCharacterTextSplitter`.
4. Relevant chunks are retrieved based on user queries.
5. The LLM generates a Persian answer.
6. The system extracts topical tags.
7. Chat history and metadata are stored in the database.
8. Global search mode automatically identifies and links the source document.

This architecture provides accurate document-grounded responses while maintaining efficient source tracking and conversation organization.
