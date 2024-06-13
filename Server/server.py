from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from business.guess_business import post_guess_prediction
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
async def get_guess_anime(guess: GuessInput, strategy: str = "id3") -> GuessOutput:
    find_strategy = FindStrategy.ID3_ENTROPY
    if strategy == "cart":
        find_strategy = FindStrategy.CART
    elif strategy == "id3":
        find_strategy = FindStrategy.ID3_ENTROPY
    elif strategy == "c45":
        find_strategy = FindStrategy.C45_WIGHTED_GAIN_ALL_TREE

    return post_guess_prediction(guess, find_strategy)


@app.post("/guess/criminals")
async def get_guess_criminals(guess: GuessInput, strategy: str = "id3"):
    pass
