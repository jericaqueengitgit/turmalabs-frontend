import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Clock,
  FileText,
  BookOpen,
  FileCheck,
  Calendar,
  Megaphone,
  Users,
  Settings,
  LogOut
} from 'lucide-react';
import turmaLogo from '../assets/turma-labs-logo.png';

const Navigation = ({ userRole, onLogout }) => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/time-logs', icon: Clock, label: 'Time Logs' },
    { path: '/eod-reports', icon: FileText, label: 'EOD Reports' },
    { path: '/trainings', icon: BookOpen, label: 'Trainings' },
    { path: '/sops', icon: FileCheck, label: 'SOPs' },
    { path: '/leave-requests', icon: Calendar, label: 'Leave Requests' },
    { path: '/announcements', icon: Megaphone, label: 'Announcements' },
  ];

  // Add Manage Users only for admin
  if (userRole === 'admin') {
    navItems.splice(1, 0, { path: '/users', icon: Users, label: 'Manage Users' });
  }

  return (
    <nav className="bg-white border-r border-gray-200 w-64 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <img src={turmaLogo} alt="Turma Labs" className="turma-logo" />
      </div>

      {/* Navigation Items */}
      <div className="flex-1 py-6">
        <ul className="space-y-2 px-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-accent text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      {/* User Actions */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onLogout}
          className="flex items-center w-full px-4 py-3 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <LogOut className="mr-3 h-5 w-5" />
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navigation;


