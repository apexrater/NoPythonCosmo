from fastapi import FastAPI, HTTPException, Path, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional

app = FastAPI()

# Connect to MongoDB Atlas asynchronously
client = AsyncIOMotorClient("<your MongoDB Atlas connection string>")
db = client["library_management"]
students_collection = db["students"]

# Sample data for testing
sample_students = [
    {"name": "John Doe", "age": 20, "address": {"city": "New York", "country": "USA"}},
    {"name": "Jane Smith", "age": 25, "address": {"city": "London", "country": "UK"}},
    {"name": "Alice Johnson", "age": 22, "address": {"city": "Paris", "country": "France"}}
]

# Initialize database with sample data if empty
async def initialize_database():
    if await students_collection.count_documents({}) == 0:
        await students_collection.insert_many(sample_students)

@app.on_event("startup")
async def startup_event():
    await initialize_database()

@app.post("/students", status_code=201)
async def create_student(student_data: dict):
    result = await students_collection.insert_one(student_data)
    return {"id": str(result.inserted_id)}

@app.get("/students", response_model=List[dict])
async def list_students(country: Optional[str] = Query(None), age: Optional[int] = Query(None)):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = await students_collection.find(query, {"_id": 0}).to_list(length=None)
    return students

@app.get("/students/{id}", response_model=dict)
async def get_student_by_id(id: str = Path(..., title="The ID of the student")):
    student = await students_collection.find_one({"_id": id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.patch("/students")
async def update_student(student_data: dict):
    student_id = student_data.get("id")
    if not student_id:
        raise HTTPException(status_code=400, detail="Student ID is required")
    
    update_data = student_data
    result = await students_collection.update_one({"_id": student_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated successfully"}

@app.delete("/students/{id}")
async def delete_student(id: str = Path(..., title="The ID of the student")):
    result = await students_collection.delete_one({"_id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
