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
        <h1>Play Anime Akinator</h1>
        <p> Think of an anime character and answer the questions:</p>
      </header>
      <QuestionPage apiClient={apiClient} />
    </div>
  );
}

export default App;
