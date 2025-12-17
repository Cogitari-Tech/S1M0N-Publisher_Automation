
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.database import Base
from src.models.schema import Thread, Message

@pytest.fixture(scope="function")
def test_db(tmp_path):
    """Creates a temporary database for testing."""
    db_path = tmp_path / "test_history.db"
    db_url = f"sqlite:///{db_path}"
    
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_thread_and_messages(test_db):
    """Ref: 1.1 Funcionalidade: Histórico (Gestão de Estado)"""
    # 1. Create Thread
    new_thread = Thread(session_id="uuid-1234", title="Test Thread")
    test_db.add(new_thread)
    test_db.commit()
    test_db.refresh(new_thread)
    
    assert new_thread.id is not None
    assert new_thread.session_id == "uuid-1234"
    
    # 2. Add Messages
    msg1 = Message(thread_id=new_thread.id, role="user", content="Hello", tokens_count=5)
    msg2 = Message(thread_id=new_thread.id, role="assistant", content="Hi there", tokens_count=8)
    
    test_db.add_all([msg1, msg2])
    test_db.commit()
    
    # 3. Verify Retrieval
    saved_msgs = test_db.query(Message).filter_by(thread_id=new_thread.id).all()
    assert len(saved_msgs) == 2
    assert saved_msgs[0].content == "Hello"
    assert saved_msgs[1].role == "assistant"
