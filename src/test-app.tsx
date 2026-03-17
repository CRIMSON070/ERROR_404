import React from 'react';

const TestApp: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold text-cyan-400">IPL Auction Dashboard - Test</h1>
      <p className="mt-4 text-gray-300">Dashboard is working!</p>
      <div className="mt-6 p-4 bg-gray-800 rounded-lg">
        <h2 className="text-xl font-semibold text-green-400">Test Components:</h2>
        <ul className="mt-2 space-y-2">
          <li className="text-gray-300">✓ React is working</li>
          <li className="text-gray-300">✓ Tailwind CSS is working</li>
          <li className="text-gray-300">✓ Dark theme is active</li>
        </ul>
      </div>
    </div>
  );
};

export default TestApp;