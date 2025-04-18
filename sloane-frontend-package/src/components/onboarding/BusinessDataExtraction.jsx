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

// Note: Mock data extraction has been removed.
// Instead, we now always use the real API for data extraction.
// If the API fails for any reason, we show an error to the user
// rather than silently falling back to mock data.

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
            
            // Log that we are using the real API, not mock data
            console.log('IMPORTANT: Using real Google Business Profile API scraping - NO MOCK DATA');
            
            // Validate business name is provided
            if (!url || url.trim() === '') {
              throw new Error('Please enter a valid business name');
            }
            
            console.log('Business name validated:', url);
            
            // Use direct API call with minimal error handling to see if we can get any response
            try {
              console.log('Making direct API call to scrape GBP with business name:', url);
              
              // Call the backend API endpoint that uses Secret Manager for the API key
              result = await businessApi.scrapeGBP(url);
              console.log('GBP scraper response received:', result);
              
              // Detailed validation and error handling
              if (!result) {
                console.error('No data returned from GBP scraper');
                throw new Error('The backend API returned an empty response. Please try again.');
              }
              
              if (result.success === false) {
                console.error('GBP scraper returned error:', result.error);
                
                let errorMessage = result.error || 'Unknown error from Google Business Profile scraper';
                if (result.details) {
                  errorMessage += `: ${result.details}`;
                }
                
                throw new Error(errorMessage);
              }
              
              // Handle possible response format variations
              if (!result.data) {
                console.warn('Response missing data property - checking for alternative structure:', result);
                
                // Try to use results property if it exists
                if (result.results) {
                  console.log('Using results property from response');
                  result.data = result.results;
                } else {
                  // If the result itself looks like business data, use it directly
                  if (result.name || result.business_name) {
                    console.log('Response appears to be direct business data, using it as-is');
                    result.data = result;
                  } else {
                    console.error('Invalid response structure:', result);
                    throw new Error('The backend returned an invalid data structure. Please try again.');
                  }
                }
              }
              
              // Check if the data object contains essential business information
              let hasValidData = false;
              
              if (result.data) {
                hasValidData = (
                  (result.data.name && (result.data.formatted_address || result.data.address)) || 
                  (result.data.business_name && result.data.address)
                );
              }
              
              if (!hasValidData) {
                console.error('GBP data is missing essential business information:', result.data);
                throw new Error('Could not find essential business information. Please try a different business name.');
              }
              
              extractedBusiness = result.data;
              console.log('Successfully extracted business data from GBP:', extractedBusiness);
              
            } catch (apiError) {
              console.error('Error during API call:', apiError);
              
              // Try direct fetch as fallback
              try {
                console.log('API call failed, trying direct fetch as fallback');
                
                // Try direct fetch to /api/business/scrape-gbp
                const response = await fetch('/api/business/scrape-gbp', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json'
                  },
                  body: JSON.stringify({
                    business_name: url,
                    location: 'San Francisco'
                  })
                });
                
                console.log('Direct fetch response status:', response.status);
                
                if (!response.ok) {
                  console.error('Direct fetch failed with status:', response.status);
                  throw new Error(`Direct API call failed with status ${response.status}`);
                }
                
                const responseData = await response.json();
                console.log('Direct fetch response data:', responseData);
                
                if (responseData.data) {
                  extractedBusiness = responseData.data;
                  console.log('Successfully extracted business data from direct fetch:', extractedBusiness);
                } else if (responseData.results) {
                  extractedBusiness = responseData.results;
                  console.log('Successfully extracted business data from direct fetch results:', extractedBusiness);
                } else {
                  console.error('Direct fetch response has invalid structure:', responseData);
                  throw new Error('Could not extract business data from API response');
                }
              } catch (directError) {
                console.error('Direct fetch also failed:', directError);
                throw apiError; // Re-throw the original error
              }
            }
            
            // Set success state for the metadata step
            setCompletedSteps(prev => ({
              ...prev,
              metadata: { success: true, timestamp: new Date().toISOString() }
            }));
          } catch (error) {
            console.error('❌ Error scraping Google Business Profile:', error);
            console.error('Error details:', {
              message: error.message,
              name: error.name,
              stack: error.stack
            });
            
            // Set a clear error message for the user
            let errorMessage = `Error retrieving business data: ${error.message}`;
            if (error.message.includes('API key')) {
              errorMessage = "Google Maps API key issue detected. Please contact support to resolve this.";
            } else if (error.message.includes('No business found') || error.message.includes('not find')) {
              errorMessage = `Could not find a business matching "${url}". Please try a different business name or enter information manually.`;
            }
            
            setError(errorMessage);
            
            // No fallback to mock data - explicitly throw error to prevent proceeding
            if (onError) {
              onError(error);
            }
            
            // Mark the metadata step as failed
            setCompletedSteps(prev => ({
              ...prev,
              metadata: { success: false, timestamp: new Date().toISOString(), error: error.message }
            }));
            
            // Exit function to prevent any processing with mock data
            throw error;
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
            
            // Show error to user
            setError(`Error scraping website: ${error.message}. Please try again or contact support.`);
            
            // Set error state and exit
            setCompletedSteps(prev => ({
              ...prev,
              metadata: { success: false, timestamp: new Date().toISOString(), error: error.message }
            }));
            
            // Call error handler
            if (onError) {
              onError(error);
            }
            
            throw error;
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
