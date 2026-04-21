import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold text-blue-600">CHMS</span>
            </div>
            <div className="flex space-x-4">
              <Link 
                href="/login" 
                className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Log in
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
          <span className="block">Church Management</span>
          <span className="block text-blue-600">Made Simple</span>
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Manage your congregations, schedule events, coordinate volunteers, and connect with members all from a single platform designed specifically for ministries of all sizes.
        </p>
        <div className="mt-10 max-w-sm mx-auto sm:max-w-none sm:flex sm:justify-center">
          <div className="space-y-4 sm:space-y-0 sm:mx-auto sm:inline-grid sm:grid-cols-2 sm:gap-5">
            <Link
              href="/login"
              className="flex items-center justify-center px-4 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 sm:px-8"
            >
              Sign In
            </Link>
            <a
              href="https://church-management-app-ae98.onrender.com/admin/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center px-4 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-blue-700 bg-blue-100 hover:bg-blue-200 sm:px-8"
            >
              Admin Dashboard
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}
