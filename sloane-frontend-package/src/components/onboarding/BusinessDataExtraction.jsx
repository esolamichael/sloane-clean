import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  LinearProgress, 
  Paper, 
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Divider
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import ScheduleIcon from '@mui/icons-material/Schedule';
import LanguageIcon from '@mui/icons-material/Language';
import StorefrontIcon from '@mui/icons-material/Storefront';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import PsychologyIcon from '@mui/icons-material/Psychology';

import businessApi from '../../api/business';

// Data extraction API that uses our mock business data
const mockDataExtraction = async (url, source, businessData = null) => {
  // Simulate different data extraction durations
  const steps = [
    { id: 'connect', time: 1000, success: true },
    { id: 'metadata', time: 1500, success: true },
    { id: 'hours', time: 1200, success: true },
    { id: 'services', time: 2000, success: true },
    { id: 'faqs', time: 1800, success: true },
    { id: 'training', time: 2500, success: true }
  ];

  const results = {};

  for (const step of steps) {
    await new Promise(resolve => setTimeout(resolve, step.time));
    results[step.id] = { 
      success: step.success,
      timestamp: new Date().toISOString()
    };
  }

  // If businessData is provided (from Google Business), use that
  if (businessData) {
    return {
      steps: results,
      business: businessData
    };
  }
  
  // Otherwise use default data based on source
  let business;
  
  if (source === 'google') {
    // Simulate fetching a Google business by hardcoding a business ID
    try {
      const result = await businessApi.getGoogleBusinessDetails('business-1');
      business = result.business;
    } catch (error) {
      console.error('Failed to fetch Google business:', error);
      // Fallback to default business data
      business = {
        name: 'ABC Dental Care',
        address: '123 Main Street, Anytown, USA',
        phone: '(555) 123-4567',
        website: url || 'https://abcdentalcare.com',
        hours: {
          monday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
          tuesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
          wednesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
          thursday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
          friday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
          saturday: { isOpen: false, openTime: '', closeTime: '' },
          sunday: { isOpen: false, openTime: '', closeTime: '' }
        },
        services: [
          { name: 'Regular Checkup', description: 'Comprehensive dental examination', price: '$75' },
          { name: 'Teeth Cleaning', description: 'Professional dental cleaning', price: '$120' },
          { name: 'Tooth Filling', description: 'Dental filling procedure', price: '$150-$300' },
          { name: 'Root Canal', description: 'Root canal treatment', price: '$700-$1,500' }
        ],
        faqs: [
          { 
            question: 'Do you accept insurance?', 
            answer: 'Yes, we accept most major insurance plans. Please call our office to verify your specific coverage.' 
          },
          { 
            question: 'How often should I have a dental checkup?', 
            answer: 'We recommend visiting for a checkup and cleaning every 6 months.' 
          },
          { 
            question: 'Do you offer emergency dental services?', 
            answer: 'Yes, we provide emergency dental care. Please call our office immediately if you have a dental emergency.' 
          }
        ]
      };
    }
  } else {
    // Website-based extraction
    business = {
      name: 'Your Business Name',
      address: '123 Main Street, Anytown, USA',
      phone: '(555) 123-4567',
      website: url,
      hours: {
        monday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
        tuesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
        wednesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
        thursday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
        friday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
        saturday: { isOpen: false, openTime: '', closeTime: '' },
        sunday: { isOpen: false, openTime: '', closeTime: '' }
      },
      services: [
        { name: 'Service 1', description: 'Description of service 1', price: '$XX' },
        { name: 'Service 2', description: 'Description of service 2', price: '$XX' }
      ],
      faqs: [
        { 
          question: 'Frequently asked question 1?', 
          answer: 'Answer to question 1.' 
        },
        { 
          question: 'Frequently asked question 2?', 
          answer: 'Answer to question 2.' 
        }
      ]
    };
  }

  return {
    steps: results,
    business: business
  };
};

const BusinessDataExtraction = ({ url, source, businessData, onComplete, onError }) => {
  const [currentStep, setCurrentStep] = useState('connect');
  const [completedSteps, setCompletedSteps] = useState({});
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  
  const steps = [
    { 
      id: 'connect', 
      label: 'Connecting to your business data', 
      icon: <LanguageIcon />,
      description: 'Establishing connection to your business information'
    },
    { 
      id: 'metadata', 
      label: 'Extracting business details', 
      icon: <StorefrontIcon />,
      description: 'Getting your business name, address, and contact information'
    },
    { 
      id: 'hours', 
      label: 'Analyzing business hours', 
      icon: <AccessTimeIcon />,
      description: 'Determining when your business is open'
    },
    { 
      id: 'services', 
      label: 'Identifying services', 
      icon: <LocalOfferIcon />,
      description: 'Finding services you offer and their descriptions'
    },
    { 
      id: 'faqs', 
      label: 'Extracting FAQs', 
      icon: <QuestionAnswerIcon />,
      description: 'Collecting frequently asked questions and answers'
    },
    { 
      id: 'training', 
      label: 'Training Sloane AI', 
      icon: <PsychologyIcon />,
      description: 'Teaching Sloane how to answer calls for your specific business'
    }
  ];

  useEffect(() => {
    const fetchBusinessData = async () => {
      try {
        let result;
        let extractedBusiness;
        
        // Track progress of steps
        const updateProgress = (stepIdx) => {
          setProgress(((stepIdx + 1) / steps.length) * 100);
        };
        
        // Connect step
        setCurrentStep('connect');
        updateProgress(0);
        setCompletedSteps(prev => ({
          ...prev,
          connect: { success: true, timestamp: new Date().toISOString() }
        }));
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Extract data based on source
        if (source === 'google' && businessData) {
          // Use selected Google Business Profile data
          setCurrentStep('metadata');
          updateProgress(1);
          setCompletedSteps(prev => ({
            ...prev,
            metadata: { success: true, timestamp: new Date().toISOString() }
          }));
          
          // Use the business data that was passed in
          extractedBusiness = businessData;
          
        } else if (source === 'google' && !businessData) {
          // Use Google Business Profile API to scrape data
          setCurrentStep('metadata');
          updateProgress(1);
          
          try {
            console.log(`Attempting to scrape Google Business Profile for: ${url}`);
            
            // First check if we can reach the API at all
            console.log('Checking API health...');
            
            // Try with the same base URL as the scraper will use
            let apiBaseUrl = '';
            if (process.env.NODE_ENV === 'development') {
              apiBaseUrl = 'http://localhost:8000';
            } else {
              apiBaseUrl = '';
            }
            
            const healthEndpoint = `${apiBaseUrl}/api/health`;
            console.log(`Checking API health at: ${healthEndpoint}`);
            
            try {
              const apiCheckResponse = await fetch(healthEndpoint);
              console.log('API health check response:', apiCheckResponse);
              
              if (!apiCheckResponse.ok) {
                console.error(`API health check failed: ${apiCheckResponse.status}`);
                throw new Error('API server is not responding. Please try again later.');
              }
              
              console.log('API health check succeeded, proceeding with GBP scraping');
            } catch (healthError) {
              console.error('API health check failed:', healthError);
              throw new Error(`Cannot connect to API server: ${healthError.message}`);
            }
            
            // Validate business name is provided
            if (!url || url.trim() === '') {
              throw new Error('Please enter a valid business name');
            }
            
            // Now proceed with scraping
            result = await businessApi.scrapeGBP(url);
            
            if (result && result.data) {
              console.log('Successfully scraped GBP data:', result);
              extractedBusiness = result.data;
              
              setCompletedSteps(prev => ({
                ...prev,
                metadata: { success: true, timestamp: new Date().toISOString() }
              }));
            } else if (result && result.success === false) {
              console.error('Backend returned error:', result);
              throw new Error(result.message || 'Backend returned an error during GBP scraping');
            } else {
              console.error('Unexpected response format:', result);
              throw new Error('Unexpected response format from GBP scraping service');
            }
          } catch (error) {
            console.error('Error scraping Google Business Profile:', error);
            console.error('Error details:', {
              message: error.message,
              name: error.name,
              stack: error.stack
            });
            
            // Show error to user but still continue with mock data
            setError(`Error scraping Google Business Profile: ${error.message}. Using sample data instead.`);
            
            // Fall back to mock data
            const mockResult = await mockDataExtraction(url, source, null);
            extractedBusiness = mockResult.business;
            
            setCompletedSteps(prev => ({
              ...prev,
              metadata: { success: true, timestamp: new Date().toISOString() }
            }));
          }
        } else {
          // Use website URL to scrape data
          setCurrentStep('metadata');
          updateProgress(1);
          
          try {
            console.log(`Attempting to scrape website URL: ${url}`);
            
            // Validate URL
            if (!url) {
              throw new Error('Please enter a valid URL');
            }
            
            // First check if we can reach the API at all
            console.log('Checking API health...');
            
            // Try with the same base URL as the scraper will use
            let apiBaseUrl = '';
            if (process.env.NODE_ENV === 'development') {
              apiBaseUrl = 'http://localhost:8000';
            } else {
              apiBaseUrl = '';
            }
            
            const healthEndpoint = `${apiBaseUrl}/api/health`;
            console.log(`Checking API health at: ${healthEndpoint}`);
            
            try {
              const apiCheckResponse = await fetch(healthEndpoint);
              console.log('API health check response:', apiCheckResponse);
              
              if (!apiCheckResponse.ok) {
                console.error(`API health check failed: ${apiCheckResponse.status}`);
                throw new Error('API server is not responding. Please try again later.');
              }
              
              console.log('API health check succeeded, proceeding with scraping');
            } catch (healthError) {
              console.error('API health check failed:', healthError);
              throw new Error(`Cannot connect to API server: ${healthError.message}`);
            }
            
            // Now proceed with scraping
            result = await businessApi.scrapeWebsite(url);
            
            if (result && result.data) {
              console.log('Successfully scraped website data:', result);
              extractedBusiness = result.data;
              
              setCompletedSteps(prev => ({
                ...prev,
                metadata: { success: true, timestamp: new Date().toISOString() }
              }));
            } else if (result && result.success === false) {
              console.error('Backend returned error:', result);
              throw new Error(result.message || 'Backend returned an error during scraping');
            } else {
              console.error('Unexpected response format:', result);
              throw new Error('Unexpected response format from scraping service');
            }
          } catch (error) {
            console.error('Error scraping website:', error);
            // Add more detailed error information
            console.error('Error details:', {
              message: error.message,
              name: error.name,
              stack: error.stack
            });
            
            // Show error to user but still continue with mock data
            setError(`Error scraping website: ${error.message}. Using sample data instead.`);
            
            // Fall back to mock data
            const mockResult = await mockDataExtraction(url, source, null);
            extractedBusiness = mockResult.business;
            
            setCompletedSteps(prev => ({
              ...prev,
              metadata: { success: true, timestamp: new Date().toISOString() }
            }));
          }
        }
        
        // Process remaining steps (hours, services, faqs, training)
        const remainingSteps = ['hours', 'services', 'faqs', 'training'];
        for (let i = 0; i < remainingSteps.length; i++) {
          const step = remainingSteps[i];
          setCurrentStep(step);
          updateProgress(i + 2); // +2 because we already did 'connect' and 'metadata'
          
          // Simulate processing time
          await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
          
          setCompletedSteps(prev => ({
            ...prev,
            [step]: { success: true, timestamp: new Date().toISOString() }
          }));
        }
        
        setProgress(100);
        // Call the completion callback with the extracted data
        onComplete(extractedBusiness);
        
      } catch (err) {
        console.error('Error extracting business data:', err);
        setError('Failed to extract business data. Please try again or enter your information manually.');
        if (onError) onError(err);
      }
    };

    fetchBusinessData();
  }, [url, source, businessData, onComplete]);

  return (
    <Paper elevation={0} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Analyzing Your Business Data
      </Typography>
      
      <LinearProgress 
        variant="determinate" 
        value={progress} 
        sx={{ height: 10, borderRadius: 5, mb: 3 }} 
      />
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <List>
        {steps.map((step) => {
          const isCompleted = completedSteps[step.id]?.success;
          const isInProgress = currentStep === step.id && !isCompleted;
          const isFuture = !isCompleted && !isInProgress;
          
          return (
            <React.Fragment key={step.id}>
              <ListItem>
                <ListItemIcon>
                  {isCompleted ? (
                    <CheckCircleOutlineIcon color="success" />
                  ) : isInProgress ? (
                    <ScheduleIcon color="primary" />
                  ) : isFuture ? (
                    <ScheduleIcon color="disabled" />
                  ) : (
                    <ErrorOutlineIcon color="error" />
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary={step.label} 
                  secondary={step.description}
                  primaryTypographyProps={{
                    fontWeight: isInProgress ? 'bold' : 'normal',
                    color: isInProgress ? 'primary.main' : 'text.primary'
                  }}
                />
              </ListItem>
              {step.id !== steps[steps.length - 1].id && <Divider variant="inset" component="li" />}
            </React.Fragment>
          );
        })}
      </List>
      
      {progress === 100 && (
        <Alert severity="success" sx={{ mt: 3 }}>
          Analysis complete! Sloane has successfully learned about your business and is ready to answer calls.
        </Alert>
      )}
    </Paper>
  );
};

export default BusinessDataExtraction;
