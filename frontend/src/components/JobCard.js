export default function JobCard({ job }) {
  return (
    <div className="border p-4 rounded-lg shadow-sm bg-white">
      <h2 className="text-xl font-semibold text-blue-800">{job.title}</h2>
      <p className="text-gray-600 mt-2">{job.description}</p>
    </div>
  );
}