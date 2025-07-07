import React, { useState } from 'react';
import { X, Mail, User, Copy, Check } from 'lucide-react';

const ForgotPassword = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    username_or_email: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [copiedField, setCopiedField] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
        setFormData({ username_or_email: '' });
      } else {
        setError(data.error || 'Failed to process request');
      }
    } catch (error) {
      console.error('Error:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const copyToClipboard = async (text, field) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleClose = () => {
    setFormData({ username_or_email: '' });
    setResult(null);
    setError('');
    setCopiedField(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {result ? 'Password Reset Successful' : 'Forgot Password'}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {!result ? (
          <>
            <p className="text-gray-600 mb-4">
              Enter your username or email address to request a password reset. 
              A new temporary password will be generated for the admin to share with you.
            </p>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username or Email
                </label>
                <div className="relative">
                  <input
                    type="text"
                    name="username_or_email"
                    value={formData.username_or_email}
                    onChange={handleInputChange}
                    placeholder="Enter your username or email"
                    required
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                  <User className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={handleClose}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90 disabled:opacity-50"
                >
                  {loading ? 'Processing...' : 'Reset Password'}
                </button>
              </div>
            </form>
          </>
        ) : (
          <>
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded text-green-700">
              <Mail className="h-5 w-5 inline mr-2" />
              Password reset successful! Please contact your admin for the new temporary password.
            </div>

            <div className="space-y-3">
              <div className="p-3 bg-gray-50 rounded">
                <label className="text-sm font-medium text-gray-700">User Information:</label>
                <div className="text-sm text-gray-900 mt-1">
                  <div><strong>Name:</strong> {result.user_info.first_name} {result.user_info.last_name}</div>
                  <div><strong>Username:</strong> {result.user_info.username}</div>
                  <div><strong>Email:</strong> {result.user_info.email}</div>
                </div>
              </div>

              <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                <label className="text-sm font-medium text-blue-700">Admin Message:</label>
                <div className="flex items-center justify-between mt-2">
                  <div className="text-sm text-blue-900 font-mono flex-1 mr-2">
                    {result.admin_message}
                  </div>
                  <button
                    onClick={() => copyToClipboard(result.admin_message, 'admin_message')}
                    className="text-blue-600 hover:text-blue-800 flex-shrink-0"
                    title="Copy admin message"
                  >
                    {copiedField === 'admin_message' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm text-yellow-800">
                  ⚠️ <strong>Important:</strong> Contact your admin to get the new temporary password. 
                  You should change this password immediately after logging in.
                </p>
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button
                onClick={handleClose}
                className="px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90"
              >
                Close
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ForgotPassword;

