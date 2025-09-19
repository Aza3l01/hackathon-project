import Link from 'next/link';

// Helper function to fetch match data from the backend
async function getMatches(candidateId) {
  try {
    // Ensure the backend URL is correct
    const res = await fetch(`http://127.0.0.1:8000/candidates/${candidateId}/matches`, {
      cache: 'no-store', // Always fetch fresh data for this page
    });

    if (!res.ok) {
      // This happens if the backend returns an error (e.g., 4xx, 5xx)
      throw new Error('Failed to fetch matches from the server.');
    }

    return res.json();
  } catch (error) {
    // This happens if there's a network issue or the above error is thrown
    console.error('Error in getMatches:', error);
    return { error: error.message }; // Return an object with an error key
  }
}

// The main page component
export default async function ResultsPage({ params }) {
  const { candidateId } = params;
  const matches = await getMatches(candidateId);

  // 1. Handle API or Network Errors
  if (matches.error) {
    return (
      <main className="container mx-auto p-8 text-center">
        <h1 className="text-3xl font-bold text-red-600">An Error Occurred</h1>
        <p className="mt-2 text-gray-600">{matches.error}</p>
        <Link href="/upload" className="mt-6 inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          Try Again
        </Link>
      </main>
    );
  }

  // 2. Handle the case where no matches are found
  if (matches.length === 0) {
    return (
      <main className="container mx-auto p-8 text-center">
        <h1 className="text-3xl font-bold">No Suitable Matches Found</h1>
        <p className="mt-2 text-gray-600">We couldn't find any jobs that strongly matched the skills in this resume.</p>
        <Link href="/upload" className="mt-6 inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          Upload Another Resume
        </Link>
      </main>
    );
  }

  // 3. Display the matches successfully
  return (
    <main className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-6 text-center">Your Top Job Matches</h1>
      <div className="space-y-6 max-w-4xl mx-auto">
        {matches.map((match) => (
          <div key={match.job_id} className="border p-6 rounded-lg shadow-sm bg-white">
            <div className="flex justify-between items-center flex-wrap gap-4">
              <h2 className="text-2xl font-semibold text-blue-800">{match.job_title}</h2>
              <span className="text-xl font-bold text-green-700 bg-green-100 px-4 py-1 rounded-full">
                {match.score}% Match
              </span>
            </div>
            <div className="mt-4">
              <h3 className="font-semibold text-gray-800">Matching Skills:</h3>
              <div className="flex flex-wrap gap-2 mt-2">
                {match.matched_skills.map(skill => (
                  <span key={skill} className="bg-green-100 text-green-800 text-sm px-3 py-1 rounded-full">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-4">
              <h3 className="font-semibold text-gray-800">Missing Skills:</h3>
              <div className="flex flex-wrap gap-2 mt-2">
                {match.missing_skills.map(skill => (
                  <span key={skill} className="bg-red-100 text-red-800 text-sm px-3 py-1 rounded-full">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}