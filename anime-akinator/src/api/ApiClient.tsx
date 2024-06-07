const BASE_API_URL = process.env.REACT_APP_BASE_API_URL;

export default class ApiClient {
    readonly base_url: string;

    constructor() {
        this.base_url = BASE_API_URL!;
    }

    
}