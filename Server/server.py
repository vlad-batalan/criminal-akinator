from fastapi import FastAPI, Depends

from business.guess_business import post_guess_prediction
from model.dto.guess_model import GuessInput, GuessOutput

app = FastAPI()


@app.post("/guess")
async def get_guess(guess: GuessInput) -> GuessOutput:
    return post_guess_prediction(guess)
