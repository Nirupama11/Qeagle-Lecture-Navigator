## Lecture Navigator API Documentation

### Search Lecture
**Endpoint:** `POST /search`  
**Description:** Takes a user query and returns the top 3 most relevant timestamps with transcript snippets.  

**Request Body (JSON):**
```json
{
  "query": "machine learning"
}

Response Example:

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

 Upload Lecture

Endpoint: POST /upload
Description: Uploads a lecture video link.

Response Example:

{
  "message": "Lecture uploaded successfully",
  "file_name": "lecture1.mp4"
}

