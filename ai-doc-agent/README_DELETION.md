# Document Deletion Functionality

This module provides comprehensive functionality to delete documents and references from the FAISS index and PKL metadata files.

## Features

- **Delete entire documents** by filename
- **Delete specific pages** from documents
- **Delete documents by content** (case-insensitive search)
- **Clear entire index** (delete all documents)
- **List documents** in the index
- **Get index statistics**

## Files

- `delete_from_index.py` - Core deletion functionality
- `example_deletion.py` - Interactive example script
- `api.py` - FastAPI endpoints for deletion operations

## Usage

### Command Line Interface

Run the interactive example script:

```bash
cd ai-doc-agent
python example_deletion.py
```

### Programmatic Usage

```python
from delete_from_index import (
    delete_document_by_filename,
    delete_document_by_page,
    delete_documents_by_content,
    delete_all_documents,
    list_documents_in_index,
    get_index_statistics
)

# Delete entire document
success = delete_document_by_filename("doc1.pdf")

# Delete specific page
success = delete_document_by_page("doc1.pdf", 1)

# Delete documents containing specific content
success = delete_documents_by_content("confidential")

# Clear entire index
success = delete_all_documents()

# List all documents
documents = list_documents_in_index()

# Get statistics
stats = get_index_statistics()
```

### API Endpoints

The FastAPI server provides the following endpoints:

#### DELETE `/documents`
Delete all pages from a specific document.

**Request Body:**
```json
{
    "filename": "doc1.pdf"
}
```

#### DELETE `/documents/page`
Delete a specific page from a document.

**Request Body:**
```json
{
    "filename": "doc1.pdf",
    "page_number": 1
}
```

#### DELETE `/documents/content`
Delete documents containing specific content.

**Request Body:**
```json
{
    "content_query": "confidential information"
}
```

#### DELETE `/documents/all`
Delete all documents from the index.

**No request body required.**

#### GET `/documents`
List all documents in the index.

**Response:**
```json
{
    "documents": {
        "doc1.pdf": [1, 2, 3],
        "doc2.pdf": [1, 2]
    }
}
```

#### GET `/documents/stats`
Get statistics about the current index.

**Response:**
```json
{
    "total_documents": 2,
    "total_pages": 5,
    "index_size": 5,
    "documents": {
        "doc1.pdf": [1, 2, 3],
        "doc2.pdf": [1, 2]
    }
}
```

## How It Works

The deletion process works by:

1. **Loading** the existing FAISS index and metadata
2. **Identifying** the indices to remove based on the deletion criteria
3. **Rebuilding** the index by re-embedding the remaining documents
4. **Updating** the metadata to reflect the changes
5. **Saving** the new index and metadata files

### Important Notes

- **Re-embedding Required**: Since FAISS doesn't provide a direct way to remove vectors, the system rebuilds the index by re-embedding the remaining documents. This ensures data consistency but may take longer for large indices.

- **File Path Handling**: The system automatically handles both relative and absolute paths, and will look for index files in both the current directory and the `ai-doc-agent` subdirectory.

- **Error Handling**: All functions include comprehensive error handling and will return `False` or raise appropriate HTTP exceptions if operations fail.

- **Safety**: The `delete_all_documents()` function requires explicit confirmation in the interactive script to prevent accidental data loss.

## Example Workflow

1. **Check current state:**
   ```python
   stats = get_index_statistics()
   print(f"Current documents: {stats['documents']}")
   ```

2. **Delete specific content:**
   ```python
   success = delete_documents_by_content("outdated information")
   ```

3. **Verify deletion:**
   ```python
   updated_stats = get_index_statistics()
   print(f"Updated documents: {updated_stats['documents']}")
   ```

## Dependencies

- `faiss` - For vector index operations
- `pickle` - For metadata serialization
- `numpy` - For array operations
- `langchain` - For document handling
- `text_processing` - For re-embedding documents

## Troubleshooting

### Common Issues

1. **"Index files not found"**
   - Ensure you're running from the correct directory
   - Check that `index.faiss` and `index.pkl` files exist

2. **"Document not found"**
   - Verify the filename matches exactly (including case)
   - Use `list_documents_in_index()` to see available documents

3. **"Page not found"**
   - Page numbers are 1-indexed
   - Check the document has the specified page number

4. **Performance issues with large indices**
   - Deletion operations re-embed all remaining documents
   - Consider batching operations for very large indices
