import './App.css';
import ApiClient from './api/ApiClient';
import { QuestionPage } from './components/QuestionPage';
import React from 'react';

function App() {
  // Create a client for the API.
  const apiClient = new ApiClient();


  return (
    <div className="App">
      <header className="App-header">
        <h1>Akinator for forinsics</h1>
        <p> You play the role of a witness. Please answer the questions to find out who is the criminal:</p>
      </header>
      <QuestionPage apiClient={apiClient} />
    </div>
  );
}

export default App;
