import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Systemclip

app = FastAPI(title="SysTok API", description="TikTok-style learning feed for System Software")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SysTok backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# --------- API Models ---------
class LikeAction(BaseModel):
    clip_id: str
    delta: int  # +1 for like, -1 for unlike

class BookmarkAction(BaseModel):
    clip_id: str
    delta: int  # +1 for add, -1 for remove

# --------- Helper ---------

def _collection_name(model_cls) -> str:
    return model_cls.__name__.lower()

# --------- Endpoints ---------

@app.get("/api/clips", response_model=List[Systemclip])
def list_clips(topic: Optional[str] = None, tag: Optional[str] = None, limit: int = 20):
    filt = {}
    if topic:
        filt["topic"] = topic
    if tag:
        filt["tags"] = {"$in": [tag]}
    try:
        docs = get_documents(_collection_name(Systemclip), filt, limit)
        # Convert ObjectId to string for response compatibility
        sanitized = []
        for d in docs:
            d.pop("_id", None)
            sanitized.append(d)
        return sanitized
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clips", status_code=201)
def create_clip(clip: Systemclip):
    try:
        inserted_id = create_document(_collection_name(Systemclip), clip)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/like")
def like_clip(action: LikeAction):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        coll = db[_collection_name(Systemclip)]
        try:
            oid = ObjectId(action.clip_id)
            result = coll.update_one({"_id": oid}, {"$inc": {"likes": action.delta, "updated_at": 1}})
        except Exception:
            # If a direct ObjectId match fails, also allow by string id stored as field 'id'
            result = coll.update_one({"id": action.clip_id}, {"$inc": {"likes": action.delta, "updated_at": 1}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Clip not found")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bookmark")
def bookmark_clip(action: BookmarkAction):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        coll = db[_collection_name(Systemclip)]
        try:
            oid = ObjectId(action.clip_id)
            result = coll.update_one({"_id": oid}, {"$inc": {"bookmarks": action.delta, "updated_at": 1}})
        except Exception:
            result = coll.update_one({"id": action.clip_id}, {"$inc": {"bookmarks": action.delta, "updated_at": 1}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Clip not found")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Seed some example clips if collection is empty
@app.post("/api/seed")
def seed_clips():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    coll = db[_collection_name(Systemclip)]
    if coll.count_documents({}) > 0:
        return {"message": "Already seeded"}
    samples = [
        {
            "title": "What is a Kernel?",
            "topic": "OS",
            "description": "A quick primer on monolithic vs microkernels with visuals.",
            "video_url": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
            "thumbnail_url": "https://picsum.photos/seed/kernel/400/700",
            "tags": ["kernel", "os", "linux"],
            "difficulty": "beginner",
            "likes": 0,
            "bookmarks": 0,
            "author": "SysTok"
        },
        {
            "title": "Page Tables in 60s",
            "topic": "OS",
            "description": "Virtual memory, TLBs and multi-level tables.",
            "video_url": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
            "thumbnail_url": "https://picsum.photos/seed/pagetable/400/700",
            "tags": ["memory", "paging"],
            "difficulty": "intermediate",
            "likes": 0,
            "bookmarks": 0,
            "author": "SysTok"
        },
        {
            "title": "Compiler vs Interpreter",
            "topic": "Compilers",
            "description": "Key differences and when each is used.",
            "video_url": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
            "thumbnail_url": "https://picsum.photos/seed/compiler/400/700",
            "tags": ["compiler", "interpreter"],
            "difficulty": "beginner",
            "likes": 0,
            "bookmarks": 0,
            "author": "SysTok"
        },
    ]
    coll.insert_many(samples)
    return {"inserted": len(samples)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
