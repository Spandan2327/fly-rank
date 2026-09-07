import sys
import os
import json
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from database import get_db_connection, init_db

SEED_POSTS = [
    {
        "id": "post-001",
        "title": "Understanding the Behavior of Red Foxes in the Forest",
        "category": "animal",
        "topic": "red fox",
        "content": "Red foxes (Vulpes vulpes) are agile nocturnal mammals native to temperate woodland ecosystems. Known for their distinct reddish-orange fur, bushy tail, and intelligent foraging tactics, red foxes inhabit dense forests and open meadows across Europe and North America."
    },
    {
        "id": "post-002",
        "title": "Gray Wolves: Social Dynamics and Pack Hunting",
        "category": "animal",
        "topic": "wolf",
        "content": "Gray wolves are top apex predators inhabiting northern wilderness habitats. Living in hierarchical family packs, gray wolves communicate using vocal howls and coordinate strategic pack hunting strategies."
    },
    {
        "id": "post-003",
        "title": "Domestic Dog Breeds and Companion Training",
        "category": "animal",
        "topic": "dog",
        "content": "Domestic dogs are loyal companions that thrive on human socialization, obedience training, and positive reinforcement."
    },
    {
        "id": "post-004",
        "title": "Grizzly Bears in National Parks",
        "category": "animal",
        "topic": "bear",
        "content": "Grizzly bears are massive omnivorous mammals living in mountainous wilderness areas, feeding on berries, salmon, and roots."
    },
    {
        "id": "post-005",
        "title": "White-Tailed Deer Ecosystem Role",
        "category": "animal",
        "topic": "deer",
        "content": "White-tailed deer graze in open woodlands and forest clearings, playing a pivotal role in seed dispersal and plant ecology."
    }
]

SEED_IMAGES = [
    {"filename": "fox_01.jpg", "url": "https://images.unsplash.com/photo-fox1", "subject": "red fox", "category": "animal", "attributes": ["orange fur", "wild", "forest"], "caption": "A bright orange red fox standing gracefully in a lush green forest meadow", "confidence": 0.95},
    {"filename": "fox_02.jpg", "url": "https://images.unsplash.com/photo-fox2", "subject": "red fox", "category": "animal", "attributes": ["reddish fur", "snow", "tail"], "caption": "Red fox sitting on white winter snow looking into the distance", "confidence": 0.92},
    {"filename": "wolf_01.jpg", "url": "https://images.unsplash.com/photo-wolf1", "subject": "wolf", "category": "animal", "attributes": ["gray fur", "wild", "forest"], "caption": "A majestic gray wolf standing on a rocky ledge in a pine forest", "confidence": 0.94},
    {"filename": "wolf_02.jpg", "url": "https://images.unsplash.com/photo-wolf2", "subject": "wolf", "category": "animal", "attributes": ["timber wolf", "snow", "pack"], "caption": "Timber wolf walking through deep winter snow", "confidence": 0.91},
    {"filename": "dog_01.jpg", "url": "https://images.unsplash.com/photo-dog1", "subject": "dog", "category": "animal", "attributes": ["domestic", "golden retriever", "park"], "caption": "Golden retriever dog playing with a tennis ball in a sunny park", "confidence": 0.96},
    {"filename": "dog_blur.jpg", "url": "https://images.unsplash.com/photo-dogblur", "subject": "dog", "category": "animal", "attributes": ["blurry", "unknown"], "caption": "A blurry low resolution photo of a pet animal", "confidence": 0.45},
    {"filename": "bear_01.jpg", "url": "https://images.unsplash.com/photo-bear1", "subject": "bear", "category": "animal", "attributes": ["brown fur", "river", "salmon"], "caption": "Grizzly brown bear catching salmon in a rushing river", "confidence": 0.93},
    {"filename": "deer_01.jpg", "url": "https://images.unsplash.com/photo-deer1", "subject": "deer", "category": "animal", "attributes": ["antlers", "forest", "meadow"], "caption": "White-tailed stag deer with large antlers grazing in woodland clearing", "confidence": 0.94}
]

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    for p in SEED_POSTS:
        cursor.execute("""
            INSERT OR REPLACE INTO posts (id, title, category, topic, content)
            VALUES (?, ?, ?, ?, ?);
        """, (p["id"], p["title"], p["category"], p["topic"], p["content"]))

    for idx, img in enumerate(SEED_IMAGES, 1):
        img_id = f"img-{idx:03d}"
        cursor.execute("""
            INSERT OR REPLACE INTO images (id, filename, url, subject, category, attributes, caption, confidence, status, cost_usd, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', 0.00025, ?);
        """, (
            img_id,
            img["filename"],
            img["url"],
            img["subject"],
            img["category"],
            json.dumps(img["attributes"]),
            img["caption"],
            img["confidence"],
            datetime.utcnow().isoformat() + "Z"
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database successfully seeded with posts and image library!")

if __name__ == "__main__":
    seed_database()
