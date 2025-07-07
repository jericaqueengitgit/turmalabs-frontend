import React from 'react';
import Navigation from './Navigation';

const Layout = ({ children, userRole, onLogout }) => {
  return (
    <div className="flex min-h-screen bg-background flex-col">
      <div className="flex flex-1">
        <Navigation userRole={userRole} onLogout={onLogout} />
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
      <footer className="text-right p-4 text-sm text-gray-500">
        Turma Labs — Powered by JCORP
      </footer>
    </div>
  );
};

export default Layout;

