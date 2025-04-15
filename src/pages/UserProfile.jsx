import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const UserProfile = () => {
  const { user } = useAuth();

  return (
    <div className="profile-page">
      <h1>Your Profile</h1>
      {user ? (
        <div className="profile-info">
          <p><strong>Name:</strong> {user.name}</p>
          <p><strong>Email:</strong> {user.email}</p>
          {/* Add more profile details as needed */}
        </div>
      ) : (
        <p>Please log in to view your profile</p>
      )}
    </div>
  );
};

export default UserProfile;