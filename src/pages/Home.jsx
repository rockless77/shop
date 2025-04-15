import React, { useState, useEffect } from 'react';

const Home = () => {
  // Example of defining 's' properly
  const [s, setS] = useState('Welcome to the Home Page!');

  // Example useEffect to simulate data fetching or some other logic
  useEffect(() => {
    // Simulating a data fetch or update to 's'
    setTimeout(() => {
      setS('Hello, User! Enjoy your shopping experience.');
    }, 2000);  // Updates 's' after 2 seconds
  }, []); // Empty dependency array means it runs only once when the component mounts

  return (
    <div className="home-container">
      <h1>{s}</h1>  {/* The 's' state is now properly defined and updated */}
    </div>
  );
};

export default Home;
