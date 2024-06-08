export interface GuessInput {
    questions: Question[];
    max_depth?: number;
}

export interface Question {
    name: string;
    answer?: string;
}

export interface GuessOutput {
    question?: string;
    values?: string[];
    guess?: string;
}