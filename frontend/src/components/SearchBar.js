"use client";

export default function SearchBar({ onSearch }) {
  return (
    <div className="mb-8">
      <input
        type="text"
        placeholder="Search by job title..."
        onChange={(e) => onSearch(e.target.value)}
        className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}