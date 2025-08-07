#!/usr/bin/env python3
"""
Example script demonstrating how to use the document deletion functionality
"""

from delete_from_index import (
    delete_document_by_filename,
    delete_document_by_page,
    delete_documents_by_content,
    delete_all_documents,
    list_documents_in_index,
    get_index_statistics
)

def main():
    print("Document Deletion Example")
    print("=" * 50)
    
    # First, let's see what's currently in the index
    print("1. Current index statistics:")
    stats = get_index_statistics()
    if stats:
        print(f"   - Total documents: {stats['total_documents']}")
        print(f"   - Total pages: {stats['total_pages']}")
        print(f"   - Index size: {stats['index_size']}")
        
        print("\n   Documents in index:")
        for filename, pages in stats['documents'].items():
            print(f"     {filename}: {len(pages)} pages")
    else:
        print("   No index found or error loading index")
        return
    
    print("\n2. Available deletion operations:")
    print("   a) Delete entire document by filename")
    print("   b) Delete specific page from document")
    print("   c) Delete documents containing specific content")
    print("   d) Delete all documents (clear index)")
    print("   e) List all documents")
    print("   f) Show statistics")
    print("   q) Quit")
    
    while True:
        choice = input("\nEnter your choice (a-f, q): ").lower().strip()
        
        if choice == 'a':
            filename = input("Enter filename to delete (e.g., 'doc1.pdf'): ").strip()
            if filename:
                success = delete_document_by_filename(filename)
                if success:
                    print(f"Successfully deleted document: {filename}")
                else:
                    print(f"Failed to delete document: {filename}")
        
        elif choice == 'b':
            filename = input("Enter filename: ").strip()
            try:
                page_num = int(input("Enter page number: "))
                success = delete_document_by_page(filename, page_num)
                if success:
                    print(f"Successfully deleted page {page_num} from {filename}")
                else:
                    print(f"Failed to delete page {page_num} from {filename}")
            except ValueError:
                print("Invalid page number. Please enter a number.")
        
        elif choice == 'c':
            content = input("Enter content to search for: ").strip()
            if content:
                success = delete_documents_by_content(content)
                if success:
                    print(f"Successfully deleted documents containing: {content}")
                else:
                    print(f"Failed to delete documents containing: {content}")
        
        elif choice == 'd':
            confirm = input("Are you sure you want to delete ALL documents? (yes/no): ").lower().strip()
            if confirm == 'yes':
                success = delete_all_documents()
                if success:
                    print("Successfully cleared all documents from index")
                else:
                    print("Failed to clear index")
            else:
                print("Operation cancelled.")
        
        elif choice == 'e':
            documents = list_documents_in_index()
            if documents:
                print("\nDocuments in index:")
                for filename, pages in documents.items():
                    print(f"  {filename}: {len(pages)} pages")
            else:
                print("No documents found in index")
        
        elif choice == 'f':
            stats = get_index_statistics()
            if stats:
                print(f"\nCurrent index statistics:")
                print(f"- Total documents: {stats['total_documents']}")
                print(f"- Total pages: {stats['total_pages']}")
                print(f"- Index size: {stats['index_size']}")
                
                print("\nDocuments in index:")
                for filename, pages in stats['documents'].items():
                    print(f"  {filename}: {len(pages)} pages")
            else:
                print("No index found or error loading index")
        
        elif choice == 'q':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a-f or q.")

if __name__ == "__main__":
    main()
