"""
Database Models
Defines SQLAlchemy models for document metadata storage
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    """
    Stores metadata about uploaded documents
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(50), default="processing")  # processing, indexed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    indexed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Document(id={self.id}, document_id={self.document_id}, filename={self.filename})>"


class DocumentChunk(Base):
    """
    Stores individual text chunks from documents for retrieval
    """
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(255), unique=True, index=True, nullable=False)
    document_id = Column(String(255), index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_index = Column(Integer, nullable=True)  # Index in FAISS
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"