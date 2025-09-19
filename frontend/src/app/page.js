"use client";

import { useState, useEffect } from 'react';
import JobCard from '../components/JobCard';
import SearchBar from '../components/SearchBar';

export default function HomePage() {
  const [allJobs, setAllJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);

  // Fetch jobs from the backend when the component loads
  useEffect(() => {
    async function fetchJobs() {
      try {
        const res = await fetch('http://127.0.0.1:8000/jobs');
        const data = await res.json();
        setAllJobs(data);
        setFilteredJobs(data);
      } catch (error) {
        console.error("Failed to fetch jobs:", error);
      }
    }
    fetchJobs();
  }, []);

  // Handle the search functionality
  const handleSearch = (query) => {
    if (!query) {
      setFilteredJobs(allJobs);
      return;
    }
    const lowercasedQuery = query.toLowerCase();
    const filtered = allJobs.filter(job =>
      job.title.toLowerCase().includes(lowercasedQuery)
    );
    setFilteredJobs(filtered);
  };

  return (
    <main className="container mx-auto p-4 md:p-8">
      <h1 className="text-4xl font-bold mb-6 text-center">Job Listings</h1>
      <SearchBar onSearch={handleSearch} />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredJobs.length > 0 ? (
          filteredJobs.map((job) => <JobCard key={job.id} job={job} />)
        ) : (
          <p className="col-span-full text-center text-gray-500">No jobs found.</p>
        )}
      </div>
    </main>
  );
}