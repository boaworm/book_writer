from pydantic import BaseModel


class Scene(BaseModel):
    title: str
    description: str


class Chapter(BaseModel):
    number: int
    title: str
    summary: str
    scenes: list[Scene] = []


class Character(BaseModel):
    name: str
    alias: str | None = None
    type: str = "Central"   # Main | Central
    role: str | None = None  # narrative role e.g. protagonist, antagonist
    description: str


class StoryOutline(BaseModel):
    title: str
    author: str
    genre: str
    premise: str
    characters: list[Character]
    chapters: list[Chapter]
