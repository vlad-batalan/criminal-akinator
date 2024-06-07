import './App.css';
import { QuestionForm } from './components/forms/QuestionForm';
import React from 'react';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Play Anime Akinator</h1>
        <p> Think of an anime character and answer the questions:</p>
      </header>
      <QuestionForm />
    </div>
  );
}

export default App;
