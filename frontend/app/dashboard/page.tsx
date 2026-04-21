'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [organization, setOrganization] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch current user details
        const userRes = await api.get('/auth/users/');
        if (userRes.data.results && userRes.data.results.length > 0) {
          // DRF returns paginated results by default
          setUser(userRes.data.results[0]);
        }

        // Fetch organization details
        const orgRes = await api.get('/organizations/organizations/');
        if (orgRes.data.results && orgRes.data.results.length > 0) {
          setOrganization(orgRes.data.results[0]);
        }
      } catch (err) {
        console.error(err);
        setError('Failed to load dashboard data. Please make sure you are logged in.');
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [router]);

  const handleLogout = () => {
    // Basic logout logic: clear any stored tokens if you had them,
    // and for basic auth/session auth, hitting an invalid endpoint clears state 
    // or just redirecting to home is enough for this simple demo.
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-blue-600">CHMS Dashboard</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700 font-medium">
                {user?.first_name} {user?.last_name} ({user?.role})
              </span>
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
              >
                Log out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Welcome Banner */}
        <div className="bg-white overflow-hidden shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back to {organization?.name || 'your Organization'}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              {organization?.description}
            </p>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          
          {/* Quick Stats Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Members Directory</dt>
                    <dd className="text-lg font-medium text-gray-900">View All</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          {/* Events Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Upcoming Events</dt>
                    <dd className="text-lg font-medium text-gray-900">Manage Schedule</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          {/* Invitations Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Invitations</dt>
                    <dd className="text-lg font-medium text-gray-900">Invite Leaders</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
