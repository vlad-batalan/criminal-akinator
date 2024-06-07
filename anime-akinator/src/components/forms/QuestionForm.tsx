import React, { FormEvent } from "react"
import { RadioComponent } from "./input/RadioComponent";

export class QuestionForm extends React.Component {
    


    handleFormSubmit = function (event: FormEvent) {
        event.preventDefault();
        const formData = event.target;

        console.log(`Submitted: ${JSON.stringify(formData)}`);
    }


    render(): React.ReactNode {
        const radioGroupName = "answer";

        return <div>
            <h2>Question: Hair_Color?</h2>
            <form onSubmit={this.handleFormSubmit}>
                <RadioComponent value="White Hair" name={radioGroupName} id="answer01" />
                <RadioComponent value="Brown Hair" name={radioGroupName} id="answer02" />
                <RadioComponent value="Blue Hair" name={radioGroupName} id="answer03" />
                <RadioComponent value="Multicoloured Hair" name={radioGroupName} id="answer04" />
                <RadioComponent value="Pink Hair" name={radioGroupName} id="answer05" />
                <RadioComponent value="Bald" name={radioGroupName} id="answer06" />
                <RadioComponent value="Not sure" name={radioGroupName} id="answer07" />

                <div className="Form-item">
                    <button type="submit" className="Primary-button" name="GuessNextBtn">Try to guess!</button>
                </div>

                <div className="Form-item">
                    <button type="submit" className="Secondary-button" name="RestartBtn">Restart game</button>
                </div>
            </form>
        </div>;
    }
}