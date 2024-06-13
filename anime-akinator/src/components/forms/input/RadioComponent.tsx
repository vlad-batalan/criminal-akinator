import React from "react";

export interface RadioComponentProps {
    readonly value: string;
    readonly id: string;
    readonly name: string;
}

export class RadioComponent extends React.Component<RadioComponentProps> {
    render(): React.ReactNode {
        return <div className="Form-item">
            <input type="radio" value={this.props.value} name={this.props.name} id={this.props.id} />
            <label htmlFor={this.props.id}>{this.props.value}</label>
        </div>
    }
}
