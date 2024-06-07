from __future__ import annotations

from fastapi import FastAPI

from business.guess_business import post_guess_prediction
from model.dto.guess_model import GuessInput, GuessOutput
from service.find_question_service import FindStrategy

app = FastAPI()


@app.post("/guess")
async def get_guess(guess: GuessInput, strategy: str = "id3") -> GuessOutput:
    find_strategy = FindStrategy.ID3_ENTROPY
    if strategy == "cart":
        find_strategy = FindStrategy.CART
    elif strategy == "id3":
        find_strategy = FindStrategy.ID3_ENTROPY
    elif strategy == "c45":
        find_strategy = FindStrategy.C45_WIGHTED_GAIN_ALL_TREE

    return post_guess_prediction(guess, find_strategy)

