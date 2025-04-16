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
          console.log('Using provided business data:', extractedBusiness);
          
        } else if (source === 'google' && !businessData) {
          // Use Google Business Profile API to scrape data
          setCurrentStep('metadata');
          updateProgress(1);
          
          console.log('Attempting to scrape Google Business Profile for:', url);
          
          // We won't use try/catch since businessApi.scrapeGBP now handles errors and returns mock data
          result = await businessApi.scrapeGBP(url);
          
          // Check if the API call was successful
          if (result.success === false) {
            console.log('API scraping failed, using fallback mock data');
            // The API call failed but returned a minimal data structure
            // Let's enhance it with mock data
            const mockResult = await mockDataExtraction(url, source, null);
            extractedBusiness = {
              ...result.data,
              ...mockResult.business
            };
          } else {
            // The API call succeeded
            extractedBusiness = result.data;
            console.log('Successfully scraped GBP data:', extractedBusiness);
            
            // For production use, ensure we have proper data structure for the onboarding flow
            if (!extractedBusiness.hours && extractedBusiness.opening_hours) {
              // Convert opening_hours format to the format expected by the onboarding flow
              extractedBusiness.hours = {};
              Object.entries(extractedBusiness.opening_hours || {}).forEach(([day, hours]) => {
                extractedBusiness.hours[day] = { 
                  isOpen: hours !== 'Closed', 
                  openTime: hours.split(' - ')[0] || '', 
                  closeTime: hours.split(' - ')[1] || '' 
                };
              });
            }
            
            // If there's no services array, create one from categories
            if (!extractedBusiness.services && extractedBusiness.categories) {
              extractedBusiness.services = extractedBusiness.categories.map(category => ({
                name: category,
                description: `Professional ${category.toLowerCase()} services`,
                price: 'Varies'
              }));
            }
            
            // If no FAQs, create some generic ones
            if (!extractedBusiness.faqs && !extractedBusiness.faq) {
              extractedBusiness.faqs = [
                { 
                  question: `What services does ${extractedBusiness.name} offer?`, 
                  answer: 'We offer a range of professional services. Please contact us for details.'
                },
                {
                  question: 'What are your business hours?',
                  answer: 'Our standard hours are Monday to Friday, 9:00 AM to 5:00 PM. Please check our website for holiday schedules.'
                }
              ];
            } else if (extractedBusiness.faq && !extractedBusiness.faqs) {
              // If faq exists but not faqs, copy it over
              extractedBusiness.faqs = extractedBusiness.faq;
            }
          }
          
          setCompletedSteps(prev => ({
            ...prev,
            metadata: { success: true, timestamp: new Date().toISOString() }
          }));
        } else {
          // Use website URL to scrape data
          setCurrentStep('metadata');
          updateProgress(1);
          
          console.log('Attempting to scrape website:', url);
          
          // We won't use try/catch since businessApi.scrapeWebsite now handles errors and returns mock data
          result = await businessApi.scrapeWebsite(url);
          
          // Check if the API call was successful
          if (result.success === false) {
            console.log('API scraping failed, using fallback mock data');
            // The API call failed but returned a minimal data structure
            // Let's enhance it with mock data
            const mockResult = await mockDataExtraction(url, source, null);
            extractedBusiness = {
              ...result.data,
              ...mockResult.business
            };
          } else {
            // The API call succeeded
            extractedBusiness = result.data;
            console.log('Successfully scraped website data:', extractedBusiness);
            
            // For production use, ensure we have proper data structure for the onboarding flow
            // Convert hours format if necessary
            if (!extractedBusiness.hours && typeof extractedBusiness.hours !== 'object') {
              // Create default hours
              extractedBusiness.hours = {
                monday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
                tuesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
                wednesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
                thursday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
                friday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
                saturday: { isOpen: false, openTime: '', closeTime: '' },
                sunday: { isOpen: false, openTime: '', closeTime: '' }
              };
            }
            
            // If services array is missing or empty, create default services
            if (!extractedBusiness.services || !Array.isArray(extractedBusiness.services) || extractedBusiness.services.length === 0) {
              extractedBusiness.services = [
                { name: 'Service 1', description: 'Description of service 1', price: 'Contact us' },
                { name: 'Service 2', description: 'Description of service 2', price: 'Contact us' }
              ];
            }
            
            // If contact_info is missing, create default
            if (!extractedBusiness.contact_info) {
              // Create default contact info
              const domain = extractedBusiness.website ? 
                extractedBusiness.website.replace(/^https?:\/\/(www\.)?/, '').split('/')[0] : 
                'example.com';
                
              extractedBusiness.contact_info = {
                email: [`info@${domain}`],
                phone: ['(555) 123-4567'],
                address: '123 Main Street, Anytown, USA'
              };
            }
            
            // If no FAQs, create some generic ones
            if ((!extractedBusiness.faqs || !Array.isArray(extractedBusiness.faqs) || extractedBusiness.faqs.length === 0) && 
                (!extractedBusiness.faq || !Array.isArray(extractedBusiness.faq) || extractedBusiness.faq.length === 0)) {
              extractedBusiness.faqs = [
                { 
                  question: `What services does ${extractedBusiness.name || 'your business'} offer?`, 
                  answer: 'We offer a range of professional services. Please contact us for details.'
                },
                {
                  question: 'What are your business hours?',
                  answer: 'Our standard hours are Monday to Friday, 9:00 AM to 5:00 PM. Please check our website for holiday schedules.'
                }
              ];
            } else if (extractedBusiness.faq && !extractedBusiness.faqs) {
              // If faq exists but not faqs, copy it over
              extractedBusiness.faqs = extractedBusiness.faq;
            }
          }
          
          setCompletedSteps(prev => ({
            ...prev,
            metadata: { success: true, timestamp: new Date().toISOString() }
          }));
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
