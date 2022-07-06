from typing import Optional
from fastapi import APIRouter
from time import perf_counter
from app.models import DResponse
from app.apis import mongo, rclone


router = APIRouter(
    prefix="/browse",
    tags=["internals"],
)

unwanted_keys = {
    "_id": 0,
    "cast": 0,
    "crew": 0,
    "seasons": 0,
    "file_name": 0,
    "subtitles": 0,
    "external_ids": 0,
    "videos": 0,
    "reviews": 0,
    "collection": 0,
    "homepage": 0,
    "last_episode_to_air": 0,
    "next_episode_to_air": 0,
    "path": 0,
    "parent": 0,
    "revenue": 0,
    "tagline": 0,
    "imdb_id": 0,
}


@router.get("", response_model=dict, status_code=200)
def categories_list():
    init_time = perf_counter()

    categories = mongo.config["categories"]
    movies_categories = []
    series_categories = []
    for rclone_index, category in enumerate(categories):
        category_type = category.get("type")
        if category_type == "movies":
            movies_categories.append(
                {"name": category.get("name"), "rclone_index": rclone_index}
            )
        elif category_type == "series":
            series_categories.append(
                {"name": category.get("name"), "rclone_index": rclone_index}
            )
    result = {"movies": movies_categories, "series": series_categories}
    return DResponse(
        200, "Categories list successfully retrieved.", True, result, init_time
    ).__json__()


@router.get("/{rclone_index}/{page}", response_model=dict, status_code=200)
def browse(
    rclone_index: int,
    page: Optional[int] = 0,
    limit: Optional[int] = 20,
    query: Optional[str] = "",
    sort: Optional[str] = "title:1",
    year: Optional[int] = 0,
    genre: Optional[str] = "",
    media_type: Optional[str] = "movies",
) -> dict:
    init_time = perf_counter()

    sort_split = sort.split(":")
    sort_dict = {sort_split[0]: int(sort_split[1])}
    if rclone_index == -1:
        if media_type == "series":
            col = mongo.series_col
        elif media_type == "movies":
            col = mongo.movies_col
        else:
            return DResponse(
                400,
                "Invalid media type '%s' provided." % media_type,
                False,
                None,
                init_time,
            )
        rclone_indexes = []
        for key, category in rclone.items():
            if media_type == category.data.get("type", "movies"):
                rclone_indexes.append(category.index)
        match = {"rclone_index": {"$in": rclone_indexes}}
        if query != "":
            match["title"] = {"$regex": f".*{query}.*", "$options": "i"}
        if year != 0:
            match["year"] = year
        if genre != "":
            match["genres.name"] = genre
        result = list(
            col.aggregate(
                [
                    {"$match": match},
                    {"$sort": sort_dict},
                    {"$skip": page * 20},
                    {"$limit": limit},
                    {"$project": unwanted_keys},
                ]
            )
        )
    else:
        for key, category in rclone.items():
            if category.index == rclone_index:
                if category.data.get("type") == "series":
                    col = mongo.series_col
                else:
                    col = mongo.movies_col
        match = {"rclone_index": rclone_index}
        if year != 0:
            match["year"] = year
        if genre != "":
            match["genres.name"] = genre
        result = list(
            col.aggregate(
                [
                    {"$match": match},
                    {"$sort": sort_dict},
                    {"$skip": page * 20},
                    {"$limit": limit},
                    {"$project": unwanted_keys},
                ]
            )
        )

    message: str = "Results found: %s. Sorted by: %s %s. Page: %s. Limit: %s." % (
        len(result),
        sort_split[0],
        "negatively" if sort_split[1] == 0 else "positively",
        page,
        limit,
    )
    if query != "":
        message += f" Query: {query}."
    if year != 0:
        message += f" Year: {year}."
    if genre != "":
        message += f" Genre: {genre}."
    if rclone_index == -1:
        message += f" Media type: {media_type}."
    return DResponse(200, message, True, result, init_time).__json__()


@router.get("/categories", response_model=dict, status_code=200)
def rclone_indeces():
    init_time = perf_counter()

    result = {}
    categories = mongo.config["categories"]
    for rclone_index, category in enumerate(categories):
        result[category["name"]] = rclone_index
    return DResponse(
        200,
        "A map of categories and rclone indeces was successfully generated.",
        True,
        result,
        init_time,
    ).__json__()
