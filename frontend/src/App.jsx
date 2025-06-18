import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [questionText, setQuestionText] = useState('');
  const [choices, setChoices] = useState([]);
  const [correctAnswer, setCorrectAnswer] = useState('');
  const [selected, setSelected] = useState('');
  const [feedback, setFeedback] = useState('');

  // Fetch trivia from backend
  const fetchTrivia = async () => {
    const res = await fetch('http://localhost:8000/trivia'); // use your IP if needed
    const data = await res.json();

    // You’ll want your backend to return structured JSON like this:
    // {
    //   question: "What is the capital of France?",
    //   choices: ["A. Paris", "B. Berlin", "C. Rome", "D. Madrid"],
    //   answer: "A"
    // }

    setQuestionText(data.question);
    setChoices(data.choices);
    setCorrectAnswer(data.answer);
    setSelected('');
    setFeedback('');
  };

  useEffect(() => {
    fetchTrivia();
  }, []);

  const handleChoice = (choice) => {
    setSelected(choice);
    if (choice.startsWith(correctAnswer)) {
      setFeedback("✅ Correct!");
    } else {
      setFeedback("❌ Wrong. The correct answer was: " + correctAnswer);
    }
  };

  return (
    <div className="App">
      <h1>Trivia Time!</h1>
      <p>{questionText}</p>
      {choices.map((choice, idx) => (
        <button key={idx} onClick={() => handleChoice(choice)}>
          {choice}
        </button>
      ))}
      {feedback && <p>{feedback}</p>}
      <button onClick={fetchTrivia} style={{ marginTop: '1rem' }}>Next Question</button>
    </div>
  );
}

export default App;
