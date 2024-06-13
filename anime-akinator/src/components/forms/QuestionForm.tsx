import React, { FormEvent, MouseEvent } from "react"
import { RadioComponent } from "./input/RadioComponent";
import ApiClient from "../../api/ApiClient";
import { GuessInput, GuessOutput, Question } from "../../api/model/GuessModel";

export interface QuestionFormProps {
    apiClient: ApiClient,
    endpoint: string
}

export interface QuestionFormState {
    questionHistory: Question[],
    answerValues?: string[],
    question?: string,
    guess?: string
}

export const DONT_KNOW_VALUE = "Don't know";

export class QuestionForm extends React.Component<QuestionFormProps, QuestionFormState> {
    readonly apiClient: ApiClient;

    constructor(props: QuestionFormProps) {
        super(props);
        this.apiClient = props.apiClient;

        this.state = {
            questionHistory: [],
            answerValues: [],
            question: undefined,
            guess: undefined
        }

        this.resetGame = this.resetGame.bind(this);
        this.guess = this.guess.bind(this);
        this.getCharacterImage = this.getCharacterImage.bind(this);
        this.handleResetGame = this.handleResetGame.bind(this);
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
    }

    guess(input: GuessInput): void {
        console.log(`Get a guess for the following: ${JSON.stringify(input)}`);
        this.apiClient._post('guess/anime?strategy=cart', input)
            .then(response => {
                // Change state array.
                const result: GuessOutput = response.data;
                console.log(`Receive guess response: ${JSON.stringify(result)}`);
                this.setState({
                    answerValues: result.values,
                    question: result.question,
                    guess: result.guess
                });
            });
    }

    resetGame(): void {
        // Reset question History.
        this.setState({ questionHistory: [] });

        const guessInput = {
            questions: []
        } as GuessInput;
        this.guess(guessInput);
    }

    getCharacterImage(query: string): string {
        return process.env.PUBLIC_URL + `/characters/${query}.png`;
    }

    handleResetGame(event: MouseEvent) {
        event.preventDefault();
        this.resetGame();
    }

    handleFormSubmit(event: FormEvent) {
        event.preventDefault();
        const formData = new FormData(event.target as HTMLFormElement);
        const answer = formData.get("answer")?.toString();

        // Add answer to question history.
        const newQuestion: Question = {
            name: this.state.question!,
            answer: answer === DONT_KNOW_VALUE ? undefined : answer
        };
        const updatedHistory = [...this.state.questionHistory, newQuestion];
        console.log(`Update history to: ${JSON.stringify(updatedHistory)}}`)
        this.setState({
            questionHistory: updatedHistory
        });

        // Create guess input.
        const guessInput: GuessInput = {
            questions: updatedHistory
        };

        // Call quess.
        this.guess(guessInput);
    }


    render(): React.ReactNode {
        const radioGroupName = "answer";

        // Display question if there is any.
        let question;
        if (this.state.question) {
            question = <h2>Question: {this.state.question}?</h2>
        } else {
            question = <div></div>
        }

        // Display the list of question values if there is any.
        let questionValues = null;
        if (this.state.answerValues && this.state.answerValues.length) {
            // Add also Don't know answer.
            let answerValues = [...this.state.answerValues.sort(), DONT_KNOW_VALUE];

            // Foreach value add a variant.
            questionValues =
                <div>
                    {answerValues.map((value, index) => (
                        <RadioComponent value={value} name={radioGroupName} id={`answer${index}`} key={`answer${index}`} />
                    ))}
                </div>
        }

        let guessDiv = null;
        if (this.state.guess) {
            const imageUrl = this.getCharacterImage(this.state.guess!)

            guessDiv = <div>
                <p>My guess for you is: {this.state.guess}</p>
                <img src={imageUrl} alt={`${this.state.guess}.png`}/>
            </div>
        }


        return <div>
            <div>
                <button className="Secondary-button" onClick={this.handleResetGame}>
                    Start new game
                </button>
            </div>

            {guessDiv}



            {question}
            <form onSubmit={this.handleFormSubmit}>
                {questionValues}
                {questionValues &&
                    <div className="Form-item">
                        <button type="submit" className="Primary-button" name="GuessNextBtn">Try to guess!</button>
                    </div>}
            </form>
        </div>;
    }
}