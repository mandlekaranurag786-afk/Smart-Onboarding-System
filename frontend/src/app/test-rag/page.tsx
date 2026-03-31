"use client";

import { useState } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function TestRAG() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const testAPI = async () => {
    setLoading(true);
    setError('');
    setResponse(null);

    console.log('Testing API:', API_BASE_URL);
    console.log('Question:', question);

    try {
      const res = await fetch(`${API_BASE_URL}/api/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          top_k: 5,
          include_sources: true,
        }),
      });

      console.log('Response status:', res.status);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      console.log('Response data:', data);
      setResponse(data);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">RAG API Test</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Test Query</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">API URL:</label>
            <input
              type="text"
              value={API_BASE_URL}
              disabled
              className="w-full px-4 py-2 border rounded bg-gray-50"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Question:</label>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What is the password policy?"
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <button
            onClick={testAPI}
            disabled={!question || loading}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Testing...' : 'Test API'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-red-800 mb-2">Error:</h3>
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {response && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Response</h2>
            
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Answer:</h3>
              <p className="text-gray-700 whitespace-pre-wrap">{response.answer}</p>
            </div>

            <div className="mb-4">
              <h3 className="font-semibold mb-2">Confidence:</h3>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                response.confidence === 'high' ? 'bg-green-100 text-green-800' :
                response.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {response.confidence?.toUpperCase()}
              </span>
            </div>

            {response.sources && response.sources.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Sources:</h3>
                <div className="space-y-2">
                  {response.sources.map((source: any, idx: number) => (
                    <div key={idx} className="border rounded p-3 bg-gray-50">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-blue-600">{source.policy_name}</span>
                        <span className="text-sm text-gray-500">
                          {(source.similarity_score * 100).toFixed(1)}% match
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{source.excerpt}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 mb-2">Instructions:</h3>
          <ol className="list-decimal list-inside space-y-1 text-blue-700 text-sm">
            <li>Make sure backend is running on port 8000</li>
            <li>Enter a question (or use: "What is the password policy?")</li>
            <li>Click "Test API"</li>
            <li>Check browser console (F12) for detailed logs</li>
            <li>If it works here but not in main chat, there's a UI issue</li>
            <li>If it doesn't work here, there's an API/backend issue</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
