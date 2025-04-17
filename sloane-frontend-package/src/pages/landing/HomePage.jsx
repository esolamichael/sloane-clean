import React from 'react';
import { Box } from '@mui/material';
import HeroSection from '../../components/landing/HeroSection';
import FeaturesSection from '../../components/landing/FeaturesSection';
import TestimonialsSection from '../../components/landing/TestimonialsSection';
import HowItWorksSection from '../../components/landing/HowItWorksSection';
import CallToActionSection from '../../components/landing/CallToActionSection';

const HomePage = () => {
  return (
    <Box>
      <HeroSection />
      <FeaturesSection />
      <TestimonialsSection />
      <HowItWorksSection />
      <CallToActionSection />
    </Box>
  );
};

export default HomePage;
