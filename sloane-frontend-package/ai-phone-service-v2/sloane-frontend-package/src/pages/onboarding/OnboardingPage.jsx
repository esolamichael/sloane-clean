import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper, 
  Stepper, 
  Step, 
  StepLabel, 
  Button,
  CircularProgress
} from '@mui/material';
import BusinessInfoForm from '../../components/onboarding/BusinessInfoForm';
import BusinessHoursForm from '../../components/onboarding/BusinessHoursForm';
import ServicesForm from '../../components/onboarding/ServicesForm';
import TwilioSetupForm from '../../components/onboarding/TwilioSetupForm';
import CalendarIntegrationForm from '../../components/onboarding/CalendarIntegrationForm';
import { useNavigate } from 'react-router-dom';

const OnboardingPage = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    businessInfo: {},
    businessHours: {},
    services: {},
    twilioSetup: {},
    calendarIntegration: {}
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const steps = [
    'Business Information',
    'Business Hours',
    'Services',
    'Phone Setup',
    'Calendar Integration'
  ];

  const handleNext = (stepData) => {
    setFormData(prevData => ({
      ...prevData,
      [getStepKey(activeStep)]: stepData
    }));
    
    if (activeStep === steps.length - 1) {
      handleSubmit();
    } else {
      setActiveStep(prevStep => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(prevStep => prevStep - 1);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Here we would submit all the collected data to the backend
      // For now, we'll just simulate a delay and redirect to dashboard
      await new Promise(resolve => setTimeout(resolve, 1500));
      navigate('/dashboard');
    } catch (error) {
      console.error('Error submitting onboarding data:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStepKey = (step) => {
    switch (step) {
      case 0: return 'businessInfo';
      case 1: return 'businessHours';
      case 2: return 'services';
      case 3: return 'twilioSetup';
      case 4: return 'calendarIntegration';
      default: return '';
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <BusinessInfoForm 
            initialData={formData.businessInfo} 
            onSubmit={handleNext} 
          />
        );
      case 1:
        return (
          <BusinessHoursForm 
            initialData={formData.businessHours} 
            onSubmit={handleNext} 
            onBack={handleBack} 
          />
        );
      case 2:
        return (
          <ServicesForm 
            initialData={formData.services} 
            onSubmit={handleNext} 
            onBack={handleBack} 
          />
        );
      case 3:
        return (
          <TwilioSetupForm 
            initialData={formData.twilioSetup} 
            onSubmit={handleNext} 
            onBack={handleBack} 
          />
        );
      case 4:
        return (
          <CalendarIntegrationForm 
            initialData={formData.calendarIntegration} 
            onSubmit={handleNext} 
            onBack={handleBack} 
            isSubmitting={isSubmitting}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Set Up Your Sloane AI Phone Service
          </Typography>
          
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
            Complete these steps to get your AI phone answering service up and running
          </Typography>
          
          <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 5 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          {getStepContent(activeStep)}
          
          {isSubmitting && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <CircularProgress />
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default OnboardingPage;
