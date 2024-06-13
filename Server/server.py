from __future__ import annotations

import logging
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from business.guess_business import post_guess_prediction_anime, post_guess_prediction_criminals
from model.dto.guess_model import GuessInput, GuessOutput
from service.find_question_service import FindStrategy


origins = [
    "http://localhost:3000"
]

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/guess/anime")
async def get_guess_anime(guess: GuessInput, strategy: str = "information_gain") -> GuessOutput:
    find_strategy = FindStrategy.INFORMATION_GAIN
    if strategy == "information_gain":
        find_strategy = FindStrategy.INFORMATION_GAIN
    elif strategy == "gini_indicator":
        find_strategy = FindStrategy.GINI_INDICATOR
    elif strategy == "gain_ratio":
        find_strategy = FindStrategy.GAIN_RATIO

    return post_guess_prediction_anime(guess, find_strategy)


@app.post("/guess/criminals")
async def get_guess_criminals(guess: GuessInput, strategy: str = "id3"):
    find_strategy = FindStrategy.INFORMATION_GAIN
    if strategy == "information_gain":
        find_strategy = FindStrategy.INFORMATION_GAIN
    elif strategy == "gini_indicator":
        find_strategy = FindStrategy.GINI_INDICATOR
    elif strategy == "gain_ratio":
        find_strategy = FindStrategy.GAIN_RATIO

    return post_guess_prediction_criminals(guess, find_strategy)
