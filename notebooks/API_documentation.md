## API Documentation

### Endpoint: POST /search
**Description:** Takes a user query and returns the top 3 most relevant timestamps with transcript snippets.  

**Request Body (JSON):**
```json
{ "query": "machine learning" }
Response Example:

json
Copy code
{
  "results": [
    {
      "timestamp": "00:12:35",
      "text": "In this section, we discuss machine learning fundamentals",
      "similarity_score": 0.92
    },
    {
      "timestamp": "00:34:10",
      "text": "Supervised learning is a subset of machine learning",
      "similarity_score": 0.88
    },
    {
      "timestamp": "01:02:50",
      "text": "Applications of machine learning include speech recognition",
      "similarity_score": 0.85
    }
  ]
}

Endpoint: POST /upload

Description: Uploads a new lecture video or subtitle file for indexing.

Request (multipart/form-data):

file: Video file (.mp4) or subtitle file (.srt)

Response Example:

{
  "message": "Lecture uploaded successfully",
  "file_name": "lecture1.mp4"
}