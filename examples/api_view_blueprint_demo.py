# -*- coding: utf-8 -*-
# Example demonstrating how to register APIView with APIBlueprint

from pydantic import BaseModel, Field

from flask_openapi3 import APIBlueprint, APIView, Info, OpenAPI, Tag

# Initialize the OpenAPI app
info = Info(title="API View with Blueprint Demo", version="1.0.0")
app = OpenAPI(__name__, info=info)

# Create an APIBlueprint
api_bp = APIBlueprint("api_bp", __name__, url_prefix="/api")

# Create an APIView
api_view = APIView(url_prefix="/v1", view_tags=[Tag(name="books")])


# Define models
class BookPath(BaseModel):
    book_id: int = Field(..., description="Book ID")


class BookQuery(BaseModel):
    search: str | None = Field(None, description="Search query")


class BookBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Book title")
    author: str = Field(..., min_length=1, max_length=100, description="Book author")
    year: int = Field(..., ge=1000, le=9999, description="Publication year")


# Define API views
@api_view.route("/books")
class BookListView:
    @api_view.doc(summary="Get all books")
    def get(self, query: BookQuery):
        """Get a list of all books"""
        if query.search:
            return {"message": f"Searching for: {query.search}", "books": []}
        return {"books": [{"id": 1, "title": "Sample Book", "author": "John Doe", "year": 2023}]}

    @api_view.doc(summary="Create a new book")
    def post(self, body: BookBody):
        """Create a new book"""
        return {"message": "Book created", "book": body.model_dump()}


@api_view.route("/books/<book_id>")
class BookDetailView:
    @api_view.doc(summary="Get a book by ID")
    def get(self, path: BookPath):
        """Get details of a specific book"""
        return {"book": {"id": path.book_id, "title": "Sample Book", "author": "John Doe", "year": 2023}}

    @api_view.doc(summary="Update a book")
    def put(self, path: BookPath, body: BookBody):
        """Update an existing book"""
        return {"message": f"Book {path.book_id} updated", "book": body.model_dump()}

    @api_view.doc(summary="Delete a book")
    def delete(self, path: BookPath):
        """Delete a book"""
        return {"message": f"Book {path.book_id} deleted"}


# Register the APIView with the APIBlueprint
api_bp.register_api_view(api_view)

# Register the APIBlueprint with the app
app.register_api(api_bp)

if __name__ == "__main__":
    print("Visit http://127.0.0.1:5000/openapi for API documentation")
    app.run(debug=True)
