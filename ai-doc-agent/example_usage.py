from add_to_index import add_document_to_index, add_multiple_files, create_vectorstore_from_files
from rag import run_rag
from text_processing import model
import os
import time

def example_add_single_document():
    """
    Example: Add a single new document to the existing index
    """
    print("=== Adding Single Document ===")
    
    # Replace with the path to your new document
    new_doc_path = f"{os.getcwd()}/doc1.pdf"
    
    if os.path.exists(new_doc_path):
        add_document_to_index(new_doc_path, model)
        print("Document added successfully!")
    else:
        print(f"Document not found: {new_doc_path}")
        print("Please place your document in the ai-doc-agent folder")

def example_add_multiple_documents():
    """
    Example: Add multiple documents to the existing index
    """
    print("=== Adding Multiple Documents ===")
    
    # List of documents to add
    documents_to_add = [
        f"{os.getcwd()}/doc1.pdf",
        f"{os.getcwd()}/doc2.pdf"
    ]
    
    add_multiple_files(documents_to_add, model)

def example_query_updated_index():
    """
    Example: Query the updated index with new knowledge
    """
    print("=== Querying Updated Index ===")
    
    # Create vectorstore from updated index
    vectorstore = create_vectorstore_from_files()
    
    if vectorstore:
        # Now you can use the updated index with run_rag
        # The index now contains both original and new documents
        query = "What information is available about the new documents I just added?"
        run_rag(query, model, vectorstore)
    else:
        print("Could not load vectorstore. Make sure index files exist.")

def example_incremental_knowledge_building():
    """
    Example: Build knowledge incrementally by adding documents over time
    """
    print("=== Incremental Knowledge Building ===")
    
    # Simulate adding documents over time
    documents_batch_1 = [
        f"{os.getcwd()}/doc1.pdf",
    ]
    
    documents_batch_2 = [
        f"{os.getcwd()}/doc2.pdf",
    ]
    
    # Add first batch
    print("Adding first batch of documents...")
    add_multiple_files(documents_batch_1, model)
    
    # Small delay to ensure files are saved
    time.sleep(1)
    
    # Query after first batch
    print("Querying after first batch...")
    vectorstore = create_vectorstore_from_files()
    if vectorstore:
        run_rag("What information is available in the first batch?", model, vectorstore)
    
    # Add second batch
    print("Adding second batch of documents...")
    add_multiple_files(documents_batch_2, model)
    
    # Small delay to ensure files are saved
    time.sleep(1)
    
    # Query after second batch
    print("Querying after second batch...")
    vectorstore = create_vectorstore_from_files()
    if vectorstore:
        run_rag("What information is available in both batches?", model, vectorstore)

if __name__ == "__main__":
    print("AI Document Agent - Knowledge Stacking Examples")
    print("=" * 50)
    
    # Choose which example to run
    choice = input("""
Choose an example to run:
1. Add single document
2. Add multiple documents
3. Query updated index
4. Incremental knowledge building
5. Run all examples

Enter your choice (1-5): """)
    
    if choice == "1":
        example_add_single_document()
    elif choice == "2":
        example_add_multiple_documents()
    elif choice == "3":
        example_query_updated_index()
    elif choice == "4":
        example_incremental_knowledge_building()
    elif choice == "5":
        example_add_single_document()
        print("\n" + "="*50 + "\n")
        example_add_multiple_documents()
        print("\n" + "="*50 + "\n")
        example_query_updated_index()
        print("\n" + "="*50 + "\n")
        example_incremental_knowledge_building()
    else:
        print("Invalid choice. Please run the script again and choose 1-5.") 