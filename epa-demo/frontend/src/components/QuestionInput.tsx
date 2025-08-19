import React, { useState, useEffect } from 'react';

interface QuestionInputProps {
  onSubmit: (question: string) => void;
  isAnalyzing: boolean;
  currentQuestion?: string; // New prop to sync with external question changes
}

const EXAMPLE_QUESTIONS = [
  "What violations does Cleveland water system have?",
  "Analyze EPA compliance for Miami-Dade water system", 
  "What violations does Houston water system have?",
  "Check San Diego water quality violations",
  "What EPA violations does Los Angeles water system have?",
  "Analyze Clinton Machine water system violations",
  "Show me lead contamination in major cities"
];

const QuestionInput: React.FC<QuestionInputProps> = ({ onSubmit, isAnalyzing, currentQuestion }) => {
  const [question, setQuestion] = useState('');

  // Effect to handle external question changes (from map clicks)
  useEffect(() => {
    if (currentQuestion !== undefined) {
      // Option 1: Show the new question in the input
      setQuestion(currentQuestion);
      
      // Option 2: Clear the input when analysis starts (uncomment below instead)
      // setQuestion('');
    }
  }, [currentQuestion]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isAnalyzing) {
      onSubmit(question.trim());
    }
  };

  const handleExampleClick = (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">
        💬 Ask EPA Compliance Question
      </h2>
      
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What violations does Springfield water system have?"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-epa-blue focus:border-transparent"
            disabled={isAnalyzing}
          />
          <button
            type="submit"
            disabled={!question.trim() || isAnalyzing}
            className="px-6 py-3 bg-epa-blue text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                Analyzing...
              </>
            ) : (
              <>
                🤖 Ask Question
              </>
            )}
          </button>
        </div>
      </form>

      <div className="border-t border-gray-200 pt-4">
        <p className="text-sm text-gray-600 mb-3">💡 Try these example questions:</p>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_QUESTIONS.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              disabled={isAnalyzing}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QuestionInput;