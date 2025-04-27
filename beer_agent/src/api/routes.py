from fastapi import FastAPI, HTTPException
from src.database.mongodb import MongoDB
from src.agent.models import Product, ProductRequest, ProductResponse

app = FastAPI()
db = MongoDB()

@app.get("/beers")
async def get_all_beers():
    try:
        beers = db.get_all_beers()
        return {"status": "success", "data": beers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/beers/{beer_id}")
async def get_beer(beer_id: str):
    try:
        beer = db.get_beer_by_id(beer_id)
        if not beer:
            raise HTTPException(status_code=404, detail="Beer not found")
        return {"status": "success", "data": beer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/beers/{beer_id}/interact")
async def interact_with_beer(beer_id: str, interaction: dict):
    try:
        db.update_beer_interaction(beer_id, interaction.get("interaction_type", "like"))
        return {"status": "success", "message": "Interaction recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))