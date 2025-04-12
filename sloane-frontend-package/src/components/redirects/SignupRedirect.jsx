import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SignupRedirect = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    console.log('Redirecting from /signup to /onboarding');
    navigate('/onboarding', { replace: true });
  }, [navigate]);
  
  return (
    <div>Redirecting to onboarding...</div>
  );
};

export default SignupRedirect;
