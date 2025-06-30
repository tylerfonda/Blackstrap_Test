import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class Database:
    def __init__(self, db_path: str = "blackstrap.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        
        # Feeds table - user-defined topic feeds
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feeds (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                topic TEXT NOT NULL,
                guidance TEXT,
                sources TEXT, -- JSON array of source types: scholar, arxiv, rss
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Articles table - raw article metadata from sources
        conn.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                feed_id TEXT NOT NULL,
                title TEXT NOT NULL,
                abstract TEXT,
                url TEXT,
                authors TEXT, -- JSON array
                published_date TEXT,
                source_type TEXT, -- scholar, arxiv, rss
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES feeds (id)
            )
        ''')
        
        # Narratives table - synthesized content from articles
        conn.execute('''
            CREATE TABLE IF NOT EXISTS narratives (
                id TEXT PRIMARY KEY,
                feed_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                article_ids TEXT, -- JSON array of article IDs used
                synthesis_prompt TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES feeds (id)
            )
        ''')
        
        # Feedback table - user responses to narratives
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                narrative_id TEXT NOT NULL,
                rating INTEGER, -- 1-5 or thumbs up/down
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (narrative_id) REFERENCES narratives (id)
            )
        ''')
        
        # MCP (Master Context Profile) table - user context and embeddings
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mcp_entries (
                id TEXT PRIMARY KEY,
                content_type TEXT NOT NULL, -- narrative, feedback, preference
                content_text TEXT NOT NULL,
                embedding TEXT, -- JSON array of float values
                metadata TEXT, -- JSON for additional context
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

class Feed:
    @staticmethod
    def create(name: str, topic: str, guidance: str = "", sources: List[str] = None) -> str:
        feed_id = str(uuid.uuid4())
        sources = sources or ["scholar", "arxiv"]
        
        conn = Database().get_connection()
        conn.execute('''
            INSERT INTO feeds (id, name, topic, guidance, sources)
            VALUES (?, ?, ?, ?, ?)
        ''', (feed_id, name, topic, guidance, json.dumps(sources)))
        conn.commit()
        conn.close()
        return feed_id
    
    @staticmethod
    def get_all() -> List[Dict]:
        conn = Database().get_connection()
        rows = conn.execute('SELECT * FROM feeds ORDER BY created_at DESC').fetchall()
        conn.close()
        return [dict(row) for row in rows]

class Article:
    @staticmethod
    def create(feed_id: str, title: str, abstract: str = "", url: str = "", 
               authors: List[str] = None, source_type: str = "test") -> str:
        article_id = str(uuid.uuid4())
        authors = authors or []
        
        conn = Database().get_connection()
        conn.execute('''
            INSERT INTO articles (id, feed_id, title, abstract, url, authors, source_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (article_id, feed_id, title, abstract, url, json.dumps(authors), source_type))
        conn.commit()
        conn.close()
        return article_id

class Narrative:
    @staticmethod
    def create(feed_id: str, title: str, content: str, article_ids: List[str]) -> str:
        narrative_id = str(uuid.uuid4())
        
        conn = Database().get_connection()
        conn.execute('''
            INSERT INTO narratives (id, feed_id, title, content, article_ids)
            VALUES (?, ?, ?, ?, ?)
        ''', (narrative_id, feed_id, title, content, json.dumps(article_ids)))
        conn.commit()
        conn.close()
        return narrative_id
    
    @staticmethod
    def get_by_feed(feed_id: str) -> List[Dict]:
        conn = Database().get_connection()
        rows = conn.execute('''
            SELECT * FROM narratives WHERE feed_id = ? ORDER BY created_at DESC
        ''', (feed_id,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

class MCPEntry:
    @staticmethod
    def create(content_type: str, content_text: str, embedding: List[float] = None, metadata: Dict = None) -> str:
        entry_id = str(uuid.uuid4())
        embedding_json = json.dumps(embedding) if embedding else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        conn = Database().get_connection()
        conn.execute('''
            INSERT INTO mcp_entries (id, content_type, content_text, embedding, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry_id, content_type, content_text, embedding_json, metadata_json))
        conn.commit()
        conn.close()
        return entry_id

