# -*- coding: utf-8 -*-
# Test for registering APIView with root app, parent blueprint, and child blueprint

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import APIBlueprint, APIView, Info, OpenAPI, Tag

info = Info(title="api view blueprint test", version="1.0.0")

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True

# Create nested blueprint structure
parent_bp = APIBlueprint("parent", __name__, url_prefix="/parent")
child_bp = APIBlueprint("child", __name__, url_prefix="/child")

# Create three APIViews - one for root, one for parent, one for child
root_api_view = APIView(url_prefix="/root", view_tags=[Tag(name="root-books")])
parent_api_view = APIView(url_prefix="/v1", view_tags=[Tag(name="parent-books")])
child_api_view = APIView(url_prefix="/v2", view_tags=[Tag(name="child-books")])


class BookPath(BaseModel):
    id: int = Field(..., description="book ID")


class BookBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Book title")


# Root level APIView (registered on app)
@root_api_view.route("/books")
class RootBookListAPIView:
    @root_api_view.doc(summary="get root book list")
    def get(self):
        return {"level": "root", "books": []}

    @root_api_view.doc(summary="create root book")
    def post(self, body: BookBody):
        return {"level": "root", "book": body.model_dump()}


@root_api_view.route("/books/<id>")
class RootBookAPIView:
    @root_api_view.doc(summary="get root book")
    def get(self, path: BookPath):
        return {"level": "root", "id": path.id}


# Parent level APIView (registered on parent_bp)
@parent_api_view.route("/books")
class ParentBookListAPIView:
    @parent_api_view.doc(summary="get parent book list")
    def get(self):
        return {"level": "parent", "books": []}

    @parent_api_view.doc(summary="create parent book")
    def post(self, body: BookBody):
        return {"level": "parent", "book": body.model_dump()}


@parent_api_view.route("/books/<id>")
class ParentBookAPIView:
    @parent_api_view.doc(summary="get parent book")
    def get(self, path: BookPath):
        return {"level": "parent", "id": path.id}

    @parent_api_view.doc(summary="update parent book")
    def put(self, path: BookPath, body: BookBody):
        return {"level": "parent", "id": path.id, "book": body.model_dump()}

    @parent_api_view.doc(summary="delete parent book")
    def delete(self, path: BookPath):
        return {"level": "parent", "deleted": path.id}


# Custom error attached to the parent blueprint
class ParentBlueprintError(Exception):
    pass


@parent_bp.errorhandler(ParentBlueprintError)
def handle_parent_blueprint_error(e: ParentBlueprintError):
    return {"error": str(e)}, 418


# Route on the CHILD APIView that always raises the custom error (no child handler)
@child_api_view.route("/boom")
class ChildBoomAPIView:
    @child_api_view.doc(summary="trigger parent blueprint error from child")
    def get(self):
        raise ParentBlueprintError("broken")


# Child level APIView (registered on child_bp)
@child_api_view.route("/books")
class ChildBookListAPIView:
    @child_api_view.doc(summary="get child book list")
    def get(self):
        return {"level": "child", "books": []}

    @child_api_view.doc(summary="create child book")
    def post(self, body: BookBody):
        return {"level": "child", "book": body.model_dump()}


@child_api_view.route("/books/<id>")
class ChildBookAPIView:
    @child_api_view.doc(summary="get child book")
    def get(self, path: BookPath):
        return {"level": "child", "id": path.id}


# Register APIView with root app (existing functionality)
app.register_api_view(root_api_view)

# Register APIView with parent blueprint (NEW functionality)
parent_bp.register_api_view(parent_api_view)

# Register APIView with child blueprint (NEW functionality)
child_bp.register_api_view(child_api_view)

# Register child blueprint with parent blueprint
parent_bp.register_api(child_bp)

# Register parent blueprint with app
app.register_api(parent_bp)


@pytest.fixture
def client():
    return app.test_client()


def test_openapi_paths():
    """Test that paths exist in OpenAPI spec at all three levels"""
    spec = app.api_doc

    # Root level paths (registered on app)
    assert "/root/books" in spec["paths"]
    assert "/root/books/{id}" in spec["paths"]

    # Parent level paths (registered on parent blueprint)
    assert "/parent/v1/books" in spec["paths"]
    assert "/parent/v1/books/{id}" in spec["paths"]

    # Child level paths (registered on child blueprint, nested under parent)
    assert "/parent/child/v2/books" in spec["paths"]
    assert "/parent/child/v2/books/{id}" in spec["paths"]


def test_root_level_get_list(client):
    """Test GET request to root APIView endpoint"""
    resp = client.get("/root/books")
    assert resp.status_code == 200
    assert resp.json == {"level": "root", "books": []}


def test_root_level_post(client):
    """Test POST request to root APIView endpoint"""
    resp = client.post("/root/books", json={"title": "Root Book"})
    assert resp.status_code == 200
    assert resp.json["level"] == "root"


def test_root_level_get_detail(client):
    """Test GET request with path parameter to root APIView"""
    resp = client.get("/root/books/99")
    assert resp.status_code == 200
    assert resp.json == {"level": "root", "id": 99}


def test_parent_level_get_list(client):
    """Test GET request to parent blueprint APIView endpoint"""
    resp = client.get("/parent/v1/books")
    assert resp.status_code == 200
    assert resp.json == {"level": "parent", "books": []}


def test_parent_level_post(client):
    """Test POST request to parent blueprint APIView endpoint"""
    resp = client.post("/parent/v1/books", json={"title": "Parent Book"})
    assert resp.status_code == 200
    assert resp.json["level"] == "parent"


def test_parent_level_get_detail(client):
    """Test GET request with path parameter to parent blueprint APIView"""
    resp = client.get("/parent/v1/books/123")
    assert resp.status_code == 200
    assert resp.json == {"level": "parent", "id": 123}


def test_parent_level_put(client):
    """Test PUT request to parent blueprint APIView endpoint"""
    resp = client.put("/parent/v1/books/123", json={"title": "Updated Parent Book"})
    assert resp.status_code == 200
    assert resp.json["level"] == "parent"
    assert resp.json["id"] == 123


def test_parent_level_delete(client):
    """Test DELETE request to parent blueprint APIView endpoint"""
    resp = client.delete("/parent/v1/books/123")
    assert resp.status_code == 200
    assert resp.json == {"level": "parent", "deleted": 123}


def test_child_error_bubbles_to_parent_handler(client):
    """Child-raised error should be handled by the parent blueprint error handler"""
    resp = client.get("/parent/child/v2/boom")
    assert resp.status_code == 418
    assert resp.json == {"error": "broken"}


def test_child_level_get_list(client):
    """Test GET request to child blueprint APIView endpoint"""
    resp = client.get("/parent/child/v2/books")
    assert resp.status_code == 200
    assert resp.json == {"level": "child", "books": []}


def test_child_level_post(client):
    """Test POST request to child blueprint APIView endpoint"""
    resp = client.post("/parent/child/v2/books", json={"title": "Child Book"})
    assert resp.status_code == 200
    assert resp.json["level"] == "child"


def test_child_level_get_detail(client):
    """Test GET request with path parameter to child blueprint APIView"""
    resp = client.get("/parent/child/v2/books/456")
    assert resp.status_code == 200
    assert resp.json == {"level": "child", "id": 456}


def test_tags_merged_from_all_levels():
    """Test that tags from root, parent, and child APIViews are all merged"""
    tag_names = [tag.name for tag in app.tags]
    assert "root-books" in tag_names
    assert "parent-books" in tag_names
    assert "child-books" in tag_names


def test_blueprint_paths_structure():
    """Test that blueprint paths are correctly structured at parent and child levels"""
    # Child blueprint should have its own url_prefix applied
    child_paths = list(child_bp.paths.keys())
    assert any("/child/v2/books" in path for path in child_paths)

    # Parent blueprint should have paths from both itself and nested child
    parent_paths = list(parent_bp.paths.keys())
    # Parent's own APIView paths
    assert any("/parent/v1/books" in path for path in parent_paths)
    # Nested child paths with parent prefix
    assert any("/parent/child/v2/books" in path for path in parent_paths)


# Idempotency test - same pattern as test_api_view.py and test_api_blueprint.py
# Create a view that will be registered multiple times
idempotent_view = APIView(url_prefix="/v1", view_tags=[Tag(name="test")])


@idempotent_view.route("/items")
class ItemView:
    @idempotent_view.doc(summary="get items")
    def get(self):
        return {"items": []}


def create_blueprint_with_view():
    app = OpenAPI(__name__, info=info)
    bp = APIBlueprint("test_bp", __name__, url_prefix="/test")
    bp.register_api_view(idempotent_view, url_prefix="/v2")
    app.register_api(bp)


# Invoke twice to ensure that call is idempotent
create_blueprint_with_view()
create_blueprint_with_view()


def test_register_api_view_idempotency():
    """Test that registering same APIView multiple times updates paths correctly"""
    assert list(idempotent_view.paths.keys()) == ["/v2/items"]
