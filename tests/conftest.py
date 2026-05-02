"""Shared test fixtures for TeamFlow tests."""

import pytest
from unittest.mock import MagicMock, patch

from app import create_app


class MockDocSnapshot:
    """Mock Firestore document snapshot."""
    def __init__(self, doc_id, data, exists=True):
        self.id = doc_id
        self._data = data
        self.exists = exists
        self.reference = MagicMock()

    def to_dict(self):
        return self._data.copy()


class MockCollection:
    """Mock Firestore collection."""
    def __init__(self):
        self.docs = {}
        self._counter = 0

    def document(self, doc_id=None):
        if doc_id is None:
            self._counter += 1
            doc_id = f"auto_{self._counter}"
        ref = MagicMock()
        ref.id = doc_id
        ref.get = MagicMock(return_value=MockDocSnapshot(
            doc_id, self.docs.get(doc_id, {}), doc_id in self.docs
        ))
        def set_fn(data):
            self.docs[doc_id] = data
            ref.get.return_value = MockDocSnapshot(doc_id, data, True)
        ref.set = MagicMock(side_effect=set_fn)
        ref.update = MagicMock(side_effect=lambda d: self.docs.get(doc_id, {}).update(d))
        ref.delete = MagicMock(side_effect=lambda: self.docs.pop(doc_id, None))
        return ref

    def where(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args):
        return self

    def stream(self):
        return [MockDocSnapshot(k, v) for k, v in self.docs.items()]


class MockFirestoreClient:
    """Mock Firestore client."""
    def __init__(self):
        self._collections = {}

    def collection(self, name):
        if name not in self._collections:
            self._collections[name] = MockCollection()
        return self._collections[name]


@pytest.fixture
def mock_db():
    """Provide a mock Firestore client."""
    return MockFirestoreClient()


@pytest.fixture
def app(mock_db):
    """Create a test Flask application."""
    from app.services import firestore_service
    firestore_service.set_db(mock_db)

    test_app = create_app("testing")
    test_app.config["TESTING"] = True
    return test_app


@pytest.fixture
def client(app):
    """Provide a Flask test client."""
    return app.test_client()
