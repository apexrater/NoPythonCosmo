from fastapi import FastAPI, HTTPException, Path, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Connect to MongoDB Atlas asynchronously
client = AsyncIOMotorClient("mongodb+srv://rawatkushagra252:eDxHaVhhpIEQGgV0@cluster0.mebrxua.mongodb.net/")
db = client["library_management"]
students_collection = db["students"]

# Hardcoded sample data for testing
sample_students = [
    {"name": "John Doe", "age": 20, "address": {"city": "New York", "country": "USA"}},
    {"name": "Jane Smith", "age": 25, "address": {"city": "London", "country": "UK"}},
    {"name": "Alice Johnson", "age": 22, "address": {"city": "Paris", "country": "France"}}
]

# Insert sample data into MongoDB collection during application startup
async def initialize_database():
    if await students_collection.count_documents({}) == 0:
        await students_collection.insert_many(sample_students)

@app.on_event("startup")
async def startup_event():
    await initialize_database()

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

# Create a new student
@app.post("/students", status_code=201)
async def create_student(student: Student):
    student_dict = student.dict()
    result = await students_collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}

# Get a list of students with optional filters
@app.get("/students", response_model=List[Student])
async def list_students(country: Optional[str] = Query(None), age: Optional[int] = Query(None)):
    query = {}
    if country:
        query["address.country"] = country
    if age is not None:
        query["age"] = {"$gte": age}
    students = await students_collection.find(query).to_list(length=None)
    return students

# Get a student by ID
@app.get("/students/{id}", response_model=Student)
async def get_student_by_id(id: str = Path(..., title="The ID of the student")):
    student = await students_collection.find_one({"_id": id})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Update a student by ID
@app.patch("/students/{id}")
async def update_student(id: str, student: Student):
    student_dict = student.dict()
    result = await students_collection.update_one({"_id": id}, {"$set": student_dict})
    if result.modified_count == 1:
        return {"message": "Student updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Delete a student by ID
@app.delete("/students/{id}")
async def delete_student(id: str):
    result = await students_collection.delete_one({"_id": id})
    if result.deleted_count == 1:
        return {"message": "Student deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")
