import React, { ChangeEvent, FormEvent, MouseEvent } from "react"
import { RadioComponent } from "./input/RadioComponent";
import ApiClient from "../../api/ApiClient";
import { GuessInput, GuessOutput, Question } from "../../api/model/GuessModel";

export interface QuestionFormProps {
    apiClient: ApiClient
}

export interface QuestionPageState {
    questionHistory: Question[],
    strategy: string,
    answerValues?: string[],
    question?: string,
    guess?: string,
    guessImageUrl?: string,
    gameType: string
}

export const DONT_KNOW_VALUE = "Don't know";

export class QuestionPage extends React.Component<QuestionFormProps, QuestionPageState> {
    readonly apiClient: ApiClient;

    constructor(props: QuestionFormProps) {
        super(props);
        this.apiClient = props.apiClient;

        this.state = {
            questionHistory: [],
            strategy: "information_gain",
            answerValues: [],
            question: undefined,
            guess: undefined,
            guessImageUrl: undefined,
            gameType: "anime"
        }

        this.resetGame = this.resetGame.bind(this);
        this.guess = this.guess.bind(this);
        this.handleStrategyChange = this.handleStrategyChange.bind(this);
        this.handleAnimeResetGame = this.handleAnimeResetGame.bind(this);
        this.handleCriminalResetGame = this.handleCriminalResetGame.bind(this);
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
    }

    guess(input: GuessInput, gameType: string, strategy: string): void {
        console.log(`Get a guess for the following: ${JSON.stringify(input)}`);
        this.apiClient._post(`guess/${gameType}?strategy=${strategy}`, input)
            .then(response => {
                // Change state array.
                const result: GuessOutput = response.data;
                console.log(`Receive guess response: ${JSON.stringify(result)}`);
                this.setState({
                    answerValues: result.values,
                    question: result.question,
                    guess: result.guess
                });

                // If a guess is provided, set the image link also.
                if (result.guess) {
                    const category = (this.state.gameType === "anime" ? "1" : "0");
                    this.apiClient._get(`media/${result.guess}?category=${category}`)
                        .then(response => {
                            // ToDo: Check files are provided.
                            console.log(`Response from GET media/${result.guess}?category=${category}: ${JSON.stringify(response.data)}`)
                            this.setState({ guessImageUrl: response.data["files"][0]["thumbnailLink"] });
                        })
                }
            });
    }

    resetGame(gameType: string): void {
        // Reset question History.
        this.setState({ questionHistory: [] });

        const strategy = this.state.strategy;
        this.setState({ guessImageUrl: undefined });

        const guessInput = {
            questions: []
        } as GuessInput;
        this.guess(guessInput, gameType, strategy);
    }

    handleAnimeResetGame(event: MouseEvent) {
        event.preventDefault();
        this.setState({ gameType: "anime" });
        this.resetGame("anime");
    }

    handleCriminalResetGame(event: MouseEvent) {
        event.preventDefault();
        this.setState({ gameType: "criminal" });
        this.resetGame("criminal");
    }

    handleStrategyChange(event: ChangeEvent<HTMLInputElement>) {
        if (event.target.checked) {
            this.setState({ strategy: event.target.value });
        }
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

        const gameType = this.state.gameType;
        const strategy = this.state.strategy;

        // Call quess.
        this.guess(guessInput, gameType, strategy);
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
                        <div key={`answer${index}`} >
                            {value && <RadioComponent value={value} name={radioGroupName} id={`answer${index}`} />}
                        </div>
                    ))}
                </div>
        }

        let guessDiv = null;
        if (this.state.guess) {
            const imageUrl = this.state.guessImageUrl;

            guessDiv = <div>
                <h3>My guess for you is: {this.state.guess}</h3>
                <img src={imageUrl} alt={this.state.guess}/>
            </div>
        }


        return <div>
            <div className="LeftContent">
                <div>
                    <button className="Secondary-button" onClick={this.handleAnimeResetGame}>
                        Start new Anime game
                    </button>
                </div>
                <div>
                    <button className="Secondary-button" onClick={this.handleCriminalResetGame}>
                        Start new Criminal game
                    </button>
                </div>
                <h3> Use the following question strategy: </h3>
                <div className="Form-item">
                    <input type="radio" value="information_gain" name="Strategy" id="strategy-info-gain" onChange={this.handleStrategyChange} defaultChecked={true} />
                    <label htmlFor="strategy-info-gain">Information Gain</label>
                </div>
                <div className="Form-item">
                    <input type="radio" value="gain_ratio" name="Strategy" id="strategy-gain-ratio" onChange={this.handleStrategyChange} />
                    <label htmlFor="strategy-gain-ratio">Gain Ratio</label>
                </div>
                <div className="Form-item">
                    <input type="radio" value="gini_impurity" name="Strategy" id="strategy-gini" onChange={this.handleStrategyChange} />
                    <label htmlFor="strategy-gini">Gini Impurity</label>
                </div>
                <div className="Form-item">
                    <input type="radio" value="mr_information_gain" name="Strategy" id="strategy-mr-info-gain" onChange={this.handleStrategyChange} />
                    <label htmlFor="strategy-mr-info-gain">MapReduce: Information Gain</label>
                </div>
                <div className="Form-item">
                    <input type="radio" value="mr_gini_impurity" name="Strategy" id="strategy-mr-gini-impurity" onChange={this.handleStrategyChange} />
                    <label htmlFor="strategy-mr-gini-impurity">MapReduce: Gini Impurity</label>
                </div>
                <div className="Form-item">
                    <input type="radio" value="mr_gain_ratio" name="Strategy" id="strategy-mr-gain-ratio" onChange={this.handleStrategyChange} />
                    <label htmlFor="strategy-mr-gain-ratio">MapReduce: Gain Ratio</label>
                </div>
            </div>
            <div className="MainContent">
                <div>
                    {guessDiv}
                    {question}
                    <form onSubmit={this.handleFormSubmit}>
                        {questionValues}
                        {questionValues &&
                            <div className="Form-item">
                                <button type="submit" className="Primary-button" name="GuessNextBtn">Try to guess!</button>
                            </div>}
                    </form>
                </div>
            </div>
            <div className="RightContent"> Right </div>
        </div >;
    }
}