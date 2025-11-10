import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from database import db, create_document, get_documents
from schemas import Device, QuoteRequest, QuoteResponse

app = FastAPI(title="The Fone Buyers API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "The Fone Buyers API is running"}

@app.get("/api/devices", response_model=List[Device])
def list_devices():
    try:
        docs = get_documents("device")
        # Fallback sample devices if DB not configured
        if not docs:
            return [
                Device(brand="Apple", model="iPhone 14 Pro", storages=[128,256,512,1024], base_price=650, image="https://images.unsplash.com/photo-1677050319876-1a6d61dc0f7b?q=80&w=1200&auto=format&fit=crop"),
                Device(brand="Samsung", model="Galaxy S23", storages=[128,256,512], base_price=500, image="https://images.unsplash.com/photo-1610945265561-a34f84a20a9a?q=80&w=1200&auto=format&fit=crop"),
                Device(brand="Google", model="Pixel 7", storages=[128,256], base_price=380, image="https://images.unsplash.com/photo-1609250291996-fdebe6020a3a?q=80&w=1200&auto=format&fit=crop"),
            ]
        # Convert Mongo docs to Device models
        devices = []
        for d in docs:
            devices.append(Device(
                brand=d.get("brand"),
                model=d.get("model"),
                storages=d.get("storages", []),
                base_price=float(d.get("base_price", 0)),
                image=d.get("image")
            ))
        return devices
    except Exception:
        # Graceful fallback if database unavailable
        return [
            Device(brand="Apple", model="iPhone 14 Pro", storages=[128,256,512,1024], base_price=650, image="https://images.unsplash.com/photo-1677050319876-1a6d61dc0f7b?q=80&w=1200&auto=format&fit=crop"),
            Device(brand="Samsung", model="Galaxy S23", storages=[128,256,512], base_price=500, image="https://images.unsplash.com/photo-1610945265561-a34f84a20a9a?q=80&w=1200&auto=format&fit=crop"),
            Device(brand="Google", model="Pixel 7", storages=[128,256], base_price=380, image="https://images.unsplash.com/photo-1609250291996-fdebe6020a3a?q=80&w=1200&auto=format&fit=crop"),
        ]

@app.post("/api/quote", response_model=QuoteResponse)
def get_quote(payload: QuoteRequest):
    # Simple pricing logic: start with base price from device, adjust by storage and condition
    devices = list_devices()
    match = next((d for d in devices if d.brand == payload.brand and d.model == payload.model), None)
    if not match:
        raise HTTPException(status_code=404, detail="Device not found")

    offer = match.base_price
    # Storage adjustment: +$40 per step above minimum
    if payload.storage in match.storages:
        min_storage = min(match.storages)
        steps = (payload.storage - min_storage) // 128
        offer += max(0, steps) * 40
    # Condition multipliers
    multipliers = {
        "Like New": 1.0,
        "Good": 0.85,
        "Fair": 0.7,
        "Broken": 0.35,
    }
    offer *= multipliers.get(payload.condition, 0.8)
    offer = round(max(20, offer), 2)

    # Record the quote request
    try:
        create_document("quote", {
            "brand": payload.brand,
            "model": payload.model,
            "storage": payload.storage,
            "condition": payload.condition,
            "offer": offer,
        })
    except Exception:
        pass

    return QuoteResponse(
        brand=payload.brand,
        model=payload.model,
        storage=payload.storage,
        condition=payload.condition,
        offer=offer,
    )

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
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
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

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
