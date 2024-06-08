import axios, { AxiosInstance } from "axios";

const BASE_API_URL = process.env.REACT_APP_BASE_URL || 'http://localhost:8000';

export default class ApiClient {
    readonly apiClient: AxiosInstance;

    constructor() {
        this.apiClient = axios.create({
            baseURL: BASE_API_URL,
            headers: {
                'Content-Type': 'application/json',
                // You can add other headers like authorization token here
            },
        });
    }

    // Define common API methods
    _get(url: string, config = {}) {
        return this.apiClient.get(url, config);
    };

    _delete(url: string, config = {}) {
        return this.apiClient.delete(url, config);
    };

    _put(url: string, data = {}, config = {}) {
        return this.apiClient.put(url, data, config);
    };

    _post(url: string, data = {}, config = {}) {
        return this.apiClient.post(url, data, config);
    };
}