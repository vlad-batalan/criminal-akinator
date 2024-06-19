import React, { ChangeEvent, FormEvent, MouseEvent } from "react"
import { RadioComponent } from "./forms/input/RadioComponent";
import ApiClient from "../api/ApiClient";
import { GuessInput, GuessOutput, Question } from "../api/model/GuessModel";
import { QuestionMetadata } from "../api/model/QuestionMetadataModel";
import Modal from "./modal/Modal";


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
    gameType: string,
    questionMetadata: QuestionMetadata[];
    modalOpen: boolean
    modalUrl?: string
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
            gameType: "anime",
            questionMetadata: [],
            modalOpen: false,
            modalUrl: undefined
        }

        this.resetGame = this.resetGame.bind(this);
        this.guess = this.guess.bind(this);
        this.handleStrategyChange = this.handleStrategyChange.bind(this);
        this.handleAnimeResetGame = this.handleAnimeResetGame.bind(this);
        this.handleCriminalResetGame = this.handleCriminalResetGame.bind(this);
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
        this.fillQuestionMetadata = this.fillQuestionMetadata.bind(this);

    }

    fillQuestionMetadata(question: string) {
        // Call API to get metadata regarding the specified question.
        this.apiClient._get(`question/${this.state.gameType}/${question}`)
            .then(response => {
                if (response.data["metadata"]) {
                    const metadataComponents: QuestionMetadata[] = response.data["metadata"];
                    this.setState({ questionMetadata: metadataComponents });
                }
            });
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

                // A new question requires changing the question metadata.
                if (result.question) {
                    this.fillQuestionMetadata(result.question!);
                }

                // If a guess is provided, set the image link also.
                if (result.guess) {
                    // Remove the question details.
                    this.setState({
                        questionMetadata: []
                    });

                    const category = (this.state.gameType === "anime" ? "1" : "0");
                    this.apiClient._get(`media/${result.guess}?category=${category}`)
                        .then(response => {
                            if (response.data["files"]) {
                                console.log(`Response from GET media/${result.guess}?category=${category}: ${JSON.stringify(response.data)}`)
                                this.setState({ guessImageUrl: response.data["files"][0]["thumbnailLink"] });
                            }
                        })
                }
            });
    }

    openImageModal(imageUrl: string) {
        this.setState({
            modalOpen: true,
            modalUrl: imageUrl
        });
    }

    closeImageModal() {
        this.setState({
            modalOpen: false,
            modalUrl: undefined
        });
    }

    resetGame(gameType: string): void {
        // Reset to defaults.
        this.setState({
            questionHistory: [],
            guessImageUrl: undefined,
            questionMetadata: []
        });

        const strategy = this.state.strategy;

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
        event.preventDefault();
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

        // If a guess is made, update the main container.
        let guessDiv = null;
        if (this.state.guess) {
            const imageUrl = this.state.guessImageUrl ? this.state.guessImageUrl : "";

            guessDiv = <div>
                <h3>My guess for you is: {this.state.guess}</h3>
                <img src={imageUrl} alt={this.state.guess} />
            </div>
        }

        // Fill in the question metadata with elements.
        let questionMetadataDiv = null;
        if (this.state.questionMetadata) {
            questionMetadataDiv = <div>
                {this.state.questionMetadata.map((metadata, index) => (
                    <div className="DetailBox" key={`metadata-${index}`}>
                        <p>{metadata.description}</p>
                        {metadata.image_url && <img src={metadata.image_url!} alt={metadata.image_id!} onClick={(e: MouseEvent) => this.openImageModal(metadata.image_url!)} />}
                    </div>
                ))
                }
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
            <div className="RightContent">
                {questionMetadataDiv}
            </div>
            <Modal 
                handleClose={() => this.closeImageModal()} 
                isOpen={this.state.modalOpen}>
                <div>
                    {this.state.modalUrl && <img src={this.state.modalUrl}></img>}
                </div>
            </Modal>
        </div >;
    }
}