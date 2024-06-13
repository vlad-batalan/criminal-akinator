import React from "react";

export interface RadioComponentProps {
    readonly value: string;
    readonly label?: string;
    readonly id: string;
    readonly name: string;
}

export class RadioComponent extends React.Component<RadioComponentProps> {

    render(): React.ReactNode {
        const labelValue = this.props.label ? this.props.label : this.props.value;

        return <div className="Form-item">
            <input type="radio" value={this.props.value} name={this.props.name} id={this.props.id}/>
            <label htmlFor={this.props.id}>{labelValue}</label>
        </div>
    }
}
