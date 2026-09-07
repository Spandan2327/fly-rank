import sqlite3
import json
import os
import sys
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "capstone.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            url TEXT NOT NULL,
            subject TEXT,
            category TEXT,
            attributes TEXT,
            caption TEXT,
            confidence REAL DEFAULT 0.0,
            status TEXT DEFAULT 'PENDING',
            cost_usd REAL DEFAULT 0.0,
            created_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL, -- 'image' or 'post'
            entity_id TEXT NOT NULL,
            vector TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            image_id TEXT,
            similarity_score REAL NOT NULL,
            status TEXT NOT NULL,
            rejection_reason TEXT,
            created_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cost_logs (
            job_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            items_processed INTEGER NOT NULL,
            tokens_used INTEGER NOT NULL,
            cost_usd REAL NOT NULL,
            timestamp TEXT NOT NULL
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
