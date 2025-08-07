# Knowledge Stacking with AI Document Agent

This extension allows you to add new documents to your existing FAISS index and pkl files, enabling you to build and stack knowledge incrementally without losing previous context.

## Files Created

- `add_to_index.py` - Main functionality for adding documents to existing indexes
- `example_usage.py` - **Working interactive examples** showing how to use the knowledge stacking features with a menu-driven interface
- `README_KNOWLEDGE_STACKING.md` - This documentation file

## Features

### 1. Add Single Document
Add one new document to your existing index:

```python
from add_to_index import add_document_to_index
from text_processing import model

# Add a new document to existing index
add_document_to_index("path/to/your/new_document.pdf", model)
```

### 2. Add Multiple Documents
Add multiple documents at once:

```python
from add_to_index import add_multiple_files
from text_processing import model

# List of documents to add
documents = [
    "path/to/doc1.pdf",
    "path/to/doc2.pdf",
    "path/to/doc3.pdf"
]

add_multiple_files(documents, model)
```

### 3. Create Vectorstore from Files
Load your updated index as a vectorstore object:

```python
from add_to_index import create_vectorstore_from_files

# Create vectorstore from updated index files
vectorstore = create_vectorstore_from_files()
```

## Usage Examples

### Basic Usage

1. **First, run your original main.py to create the initial index:**
   ```bash
   python main.py
   ```

2. **Use the interactive examples (recommended):**
   ```bash
   python example_usage.py
   ```
   This will present you with a menu to choose from different examples:
   - Add single document
   - Add multiple documents  
   - Query updated index
   - Incremental knowledge building
   - Run all examples

3. **Or add new documents directly:**
   ```bash
   python add_to_index.py
   ```
   (Modify the file path in the script first)

### Advanced Usage

#### Incremental Knowledge Building

```python
from add_to_index import add_document_to_index, create_vectorstore_from_files
from rag import run_rag
from text_processing import model

# Add documents over time
add_document_to_index("new_research_paper.pdf", model)
add_document_to_index("company_manual.pdf", model)
add_document_to_index("technical_specs.pdf", model)

# Query the accumulated knowledge
vectorstore = create_vectorstore_from_files()
if vectorstore:
    run_rag("What are the key findings across all documents?", model)
```

**Note**: The `example_usage.py` file includes a working example of incremental knowledge building that demonstrates adding documents in batches and querying the updated index after each batch.

#### Batch Processing

```python
from add_to_index import add_multiple_files

# Add a batch of related documents
research_papers = [
    "paper1.pdf",
    "paper2.pdf", 
    "paper3.pdf"
]

add_multiple_files(research_papers, model)
```

## How It Works

1. **Loads Existing Index**: The system first loads your existing `index.faiss` and `index.pkl` files
2. **Extracts New Content**: Processes new documents using the same text extraction pipeline
3. **Embeds New Content**: Creates embeddings for the new document chunks
4. **Updates Index**: Adds new embeddings to the existing FAISS index
5. **Updates Metadata**: Maintains document mappings and metadata
6. **Saves Updated Files**: Overwrites the existing index files with the updated version

## File Structure

After adding documents, your index files will contain:
- `index.faiss` - Updated FAISS index with all document embeddings
- `index.pkl` - Updated metadata with document mappings

## Benefits

- **Knowledge Accumulation**: Build a comprehensive knowledge base over time
- **No Data Loss**: Existing documents remain in the index
- **Efficient**: Only processes new documents, doesn't reprocess existing ones
- **Flexible**: Add documents individually or in batches
- **Compatible**: Works with your existing RAG pipeline

## Important Notes

- The system automatically handles both new index creation and existing index updates
- Document IDs are unique and include the file path to avoid conflicts
- The same embedding model is used for consistency
- Index files are automatically saved after each addition

## Troubleshooting

### File Not Found Errors
- Ensure your documents exist at the specified paths
- Check that the `ai-doc-agent` directory contains your index files

### Index Corruption
- If index files become corrupted, delete `index.faiss` and `index.pkl`
- Recreate the index using `main.py`

### Memory Issues
- For very large document collections, consider using a more efficient FAISS index type
- Monitor memory usage when adding many documents at once

## Integration with Existing Code

This extension is designed to work alongside your existing `main.py` without modifications:

1. Use `main.py` for initial index creation
2. Use `example_usage.py` for interactive examples and testing (recommended)
3. Use `add_to_index.py` for programmatic document addition
4. Use your existing `run_rag()` function with the updated index

The knowledge stacking functionality preserves all existing functionality while adding the ability to incrementally build your knowledge base. The `example_usage.py` file provides a user-friendly way to test and demonstrate all features. 