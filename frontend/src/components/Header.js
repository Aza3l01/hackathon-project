import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-white shadow-md">
      <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-blue-600">
          LLM Job Portal
        </Link>
        <Link href="/upload" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          Upload Resume
        </Link>
      </nav>
    </header>
  );
}