import React from 'react';
import Navbar from './Navbar';

const withNavbar = (Component) => {
  return (props) => (
    <>
      <Navbar />
      <Component {...props} />
    </>
  );
};

export default withNavbar;