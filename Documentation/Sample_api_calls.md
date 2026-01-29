# Sample API Calls for Document Intelligence Backend

This file contains sample curl commands for testing the API.

## 1. Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## 2. Root Endpoint

```bash
curl -X GET "http://localhost:8000/"
```

## 3. Upload Document (PDF)

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf"
```

## 4. Upload Document (Image)

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.png"
```

## 5. Check Document Status

```bash
# Replace {document_id} with actual ID from upload response
curl -X GET "http://localhost:8000/documents/status/{document_id}"
```

## 6. Ask Question

```bash
curl -X POST "http://localhost:8000/documents/ask" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of the document?"
  }'
```

## 7. Ask Question with Max Sources

```bash
curl -X POST "http://localhost:8000/documents/ask" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key points?",
    "max_sources": 3
  }'
```

## Example Complete Workflow

```bash
# Step 1: Check if server is running
curl -X GET "http://localhost:8000/health"

# Step 2: Upload a document
RESPONSE=$(curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf")

echo $RESPONSE

# Extract document_id from response (requires jq)
DOCUMENT_ID=$(echo $RESPONSE | jq -r '.document_id')
echo "Document ID: $DOCUMENT_ID"

# Step 3: Check document status
curl -X GET "http://localhost:8000/documents/status/$DOCUMENT_ID"

# Step 4: Ask questions
curl -X POST "http://localhost:8000/documents/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'

curl -X POST "http://localhost:8000/documents/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main conclusions?"}'
```

## Using with Authentication (Future Enhancement)

```bash
# When authentication is added, include token in headers
TOKEN="your_auth_token"

curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

## Postman Collection

You can also import these as a Postman collection. Create a new collection with these requests:

### Request 1: Health Check
- Method: GET
- URL: `{{base_url}}/health`

### Request 2: Upload Document
- Method: POST
- URL: `{{base_url}}/documents/upload`
- Body: form-data
- Key: `file` (type: File)

### Request 3: Ask Question
- Method: POST
- URL: `{{base_url}}/documents/ask`
- Body: raw (JSON)
```json
{
  "question": "Your question here"
}
```

**Environment Variable:**
- `base_url` = `http://localhost:8000`