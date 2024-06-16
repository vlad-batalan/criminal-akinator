from __future__ import annotations

import logging
from typing import Annotated

import fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from business.business import post_guess_prediction_anime, post_guess_prediction_criminals, retrieve_file_drive, \
    retrieve_question
from model.dto.guess_model import GuessInput, GuessOutput
from service.find_question_service import FindStrategy
from service.google_drive_service import MediaCategory

origins = [
    "http://localhost:3000"
]

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

strategy_map = {
    "information_gain": FindStrategy.INFORMATION_GAIN,
    "gini_impurity": FindStrategy.GINI_IMPURITY,
    "gain_ratio": FindStrategy.GAIN_RATIO,
    "mr_information_gain": FindStrategy.INFORMATION_GAIN_MR,
    "mr_gini_impurity": FindStrategy.GINI_IMPURITY_MR,
    "mr_gain_ratio": FindStrategy.GAIN_RATIO_MR
}


@app.post("/guess/anime")
async def get_guess_anime(guess: GuessInput, strategy: str = "information_gain") -> GuessOutput:
    if strategy in strategy_map:
        find_strategy = strategy_map[strategy]
        return post_guess_prediction_anime(guess, find_strategy)
    else:
        raise fastapi.HTTPException(status_code=400, detail=f"Not supported strategy: {strategy}")


@app.post("/guess/criminal")
async def get_guess_criminals(guess: GuessInput, strategy: str = "information_gain"):
    if strategy in strategy_map:
        find_strategy = strategy_map[strategy]
        return post_guess_prediction_criminals(guess, find_strategy)
    else:
        raise fastapi.HTTPException(status_code=400, detail=f"Not supported strategy: {strategy}")


@app.get("/media/{media_id}")
async def get_media(media_id: str, category: int):
    return retrieve_file_drive(media_id, MediaCategory(category))


@app.get("/question/anime/{question}")
async def get_question_anime(question: str):
    return retrieve_question(question, "anime")


@app.get("/question/criminal/{question}")
async def get_question_criminal(question: str):
    return retrieve_question(question, "criminal")
