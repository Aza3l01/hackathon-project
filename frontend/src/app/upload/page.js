"use client";

import { useState } from 'react';
import Link from 'next/link';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [statusMessage, setStatusMessage] = useState('Select a PDF to begin.');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setStatusMessage(`Selected file: ${selectedFile.name}`);
      setError('');
      setAnalysisResult(null);
    } else {
      setFile(null);
      setError('Please select a valid PDF file.');
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a file before submitting.');
      return;
    }

    setIsProcessing(true);
    setError('');
    setAnalysisResult(null);

    try {
      // Step 1: Upload
      setStatusMessage('Step 1/3: Uploading resume...');
      const formData = new FormData();
      formData.append('file', file);
      const uploadRes = await fetch('http://127.0.0.1:8000/upload_resume', { method: 'POST', body: formData });
      if (!uploadRes.ok) throw new Error('Resume upload failed.');
      const uploadData = await uploadRes.json();
      const { candidate_id } = uploadData;

      // Step 2: Analyze
      setStatusMessage('Step 2/3: Analyzing skills...');
      const analyzeRes = await fetch(`http://127.0.0.1:8000/analyze_resume/${candidate_id}`, { method: 'POST' });
      if (!analyzeRes.ok) throw new Error('Skill analysis failed.');
      const analysisData = await analyzeRes.json();
      
      // Step 3: Generate and Save Matches (The new step)
      setStatusMessage('Step 3/3: Generating job matches...');
      const generateRes = await fetch(`http://127.0.0.1:8000/candidates/${candidate_id}/generate-matches`, { method: 'POST' });
      if (!generateRes.ok) throw new Error('Failed to generate matches.');

      // All backend work is done. Now display the results.
      setStatusMessage('Analysis complete! Ready to view matches.');
      setAnalysisResult(analysisData);

    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <main className="container mx-auto p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-center">Upload Resume</h1>
        <form onSubmit={handleSubmit} className="p-8 border rounded-lg shadow-md bg-white">
          <div className="mb-4">
            <label htmlFor="resume-upload" className="block text-lg font-medium mb-2">PDF Resume</label>
            <input id="resume-upload" type="file" accept=".pdf" onChange={handleFileChange} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
          </div>
          <button type="submit" disabled={isProcessing || !file} className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400">
            {isProcessing ? 'Processing...' : 'Analyze My Resume'}
          </button>
        </form>

        <div className="mt-4 p-4 bg-gray-100 rounded-lg text-center">
          {/* Changed text-gray-700 to text-black as requested */}
          <p className="font-mono text-sm text-black">{statusMessage}</p>
        </div>
        
        {error && <p className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg"><strong>Error:</strong> {error}</p>}
        
        {analysisResult && (
          <div className="mt-8 p-6 border rounded-lg bg-white shadow-md">
            <h2 className="text-2xl font-bold">Analysis Complete</h2>
            <div className="mt-4">
              <h3 className="font-semibold">Extracted Skills:</h3>
              <div className="flex flex-wrap gap-2 mt-2">
                {analysisResult.skills.length > 0 ? analysisResult.skills.map(skill => (
                  <span key={skill} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">{skill}</span>
                )) : <p className="text-sm text-gray-500">No specific skills extracted.</p>}
              </div>
            </div>
            <div className="mt-4">
              <h3 className="font-semibold">Resume Text Preview:</h3>
              <p className="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-md italic">{analysisResult.resume_text_preview}</p>
            </div>
            <div className="mt-6 text-center">
              <Link href={`/results/${analysisResult.candidate_id}`} className="inline-block px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700">
                See Job Matches
              </Link>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}