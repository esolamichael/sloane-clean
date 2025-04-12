import React from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Grid, 
  Paper,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  Alert,
  Card,
  CardContent,
  CardMedia,
  Divider
} from '@mui/material';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import GoogleIcon from '@mui/icons-material/Google';
import EventIcon from '@mui/icons-material/Event';
import AppleIcon from '@mui/icons-material/Apple';
import MicrosoftIcon from '@mui/icons-material/Microsoft';

const CalendarIntegrationSchema = Yup.object().shape({
  calendarProvider: Yup.string()
});

const CalendarIntegrationForm = ({ initialData = {}, onSubmit, onBack, isSubmitting }) => {
  // Direct continuation function that bypasses form validation
  const handleForceContinue = (values) => {
    console.log('Force continuing with calendar integration values:', values);
    
    // Process values to ensure they're valid
    const processedValues = { ...values };
    
    // Ensure we have a default value
    if (!processedValues.calendarProvider) {
      processedValues.calendarProvider = 'none';
    }
    
    // Call the parent component's onSubmit directly
    onSubmit(processedValues);
  };
  return (
    <Formik
      initialValues={{
        calendarProvider: initialData.calendarProvider || ''
      }}
      validationSchema={CalendarIntegrationSchema}
      onSubmit={(values) => {
        onSubmit(values);
      }}
    >
      {({ values, handleChange }) => (
        <Form noValidate>
          {/* Hidden submit button that can be triggered programmatically if needed */}
          <button type="submit" style={{ display: 'none' }} />
          <Paper elevation={0} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Calendar Integration (Optional)
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Connect your calendar so Sloane can schedule appointments for you. You can also set this up later.
            </Typography>
            
            <Alert severity="info" sx={{ mb: 4 }}>
              Calendar integration allows Sloane to check your availability and schedule appointments directly on your calendar.
            </Alert>
            
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Select Calendar Provider
              </Typography>
              
              <FormControl component="fieldset" fullWidth sx={{ mb: 3 }}>
                <RadioGroup
                  name="calendarProvider"
                  value={values.calendarProvider}
                  onChange={handleChange}
                >
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Card 
                        sx={{ 
                          mb: 2, 
                          cursor: 'pointer',
                          border: values.calendarProvider === 'google' ? '2px solid' : '1px solid',
                          borderColor: values.calendarProvider === 'google' ? 'primary.main' : 'divider',
                        }}
                        onClick={() => handleChange({ target: { name: 'calendarProvider', value: 'google' } })}
                      >
                        <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                          <GoogleIcon color="error" sx={{ fontSize: 32, mr: 2 }} />
                          <Box>
                            <Typography variant="subtitle1">Google Calendar</Typography>
                            <Typography variant="body2" color="text.secondary">
                              Connect with your Google account
                            </Typography>
                          </Box>
                          <Radio 
                            checked={values.calendarProvider === 'google'} 
                            value="google"
                            name="calendarProvider"
                            sx={{ ml: 'auto' }}
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Card 
                        sx={{ 
                          mb: 2, 
                          cursor: 'pointer',
                          border: values.calendarProvider === 'outlook' ? '2px solid' : '1px solid',
                          borderColor: values.calendarProvider === 'outlook' ? 'primary.main' : 'divider',
                        }}
                        onClick={() => handleChange({ target: { name: 'calendarProvider', value: 'outlook' } })}
                      >
                        <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                          <MicrosoftIcon color="primary" sx={{ fontSize: 32, mr: 2 }} />
                          <Box>
                            <Typography variant="subtitle1">Outlook Calendar</Typography>
                            <Typography variant="body2" color="text.secondary">
                              Connect with your Microsoft account
                            </Typography>
                          </Box>
                          <Radio 
                            checked={values.calendarProvider === 'outlook'} 
                            value="outlook"
                            name="calendarProvider"
                            sx={{ ml: 'auto' }}
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Card 
                        sx={{ 
                          mb: 2, 
                          cursor: 'pointer',
                          border: values.calendarProvider === 'apple' ? '2px solid' : '1px solid',
                          borderColor: values.calendarProvider === 'apple' ? 'primary.main' : 'divider',
                        }}
                        onClick={() => handleChange({ target: { name: 'calendarProvider', value: 'apple' } })}
                      >
                        <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                          <AppleIcon sx={{ fontSize: 32, mr: 2 }} />
                          <Box>
                            <Typography variant="subtitle1">Apple Calendar</Typography>
                            <Typography variant="body2" color="text.secondary">
                              Connect with your Apple account
                            </Typography>
                          </Box>
                          <Radio 
                            checked={values.calendarProvider === 'apple'} 
                            value="apple"
                            name="calendarProvider"
                            sx={{ ml: 'auto' }}
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Card 
                        sx={{ 
                          mb: 2, 
                          cursor: 'pointer',
                          border: values.calendarProvider === 'none' ? '2px solid' : '1px solid',
                          borderColor: values.calendarProvider === 'none' ? 'primary.main' : 'divider',
                        }}
                        onClick={() => handleChange({ target: { name: 'calendarProvider', value: 'none' } })}
                      >
                        <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                          <EventIcon sx={{ fontSize: 32, mr: 2 }} />
                          <Box>
                            <Typography variant="subtitle1">Skip for now</Typography>
                            <Typography variant="body2" color="text.secondary">
                              Set up calendar integration later
                            </Typography>
                          </Box>
                          <Radio 
                            checked={values.calendarProvider === 'none'} 
                            value="none"
                            name="calendarProvider"
                            sx={{ ml: 'auto' }}
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </RadioGroup>
              </FormControl>
            </Box>
            
            {values.calendarProvider && values.calendarProvider !== 'none' && (
              <Alert severity="success" sx={{ mb: 4 }}>
                You'll be prompted to connect your {values.calendarProvider === 'google' ? 'Google' : values.calendarProvider === 'outlook' ? 'Microsoft' : 'Apple'} account after completing the setup.
              </Alert>
            )}
            
            <Divider sx={{ my: 4 }} />
            
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                You're almost done!
              </Typography>
              <Typography variant="body1" paragraph>
                Click "Complete Setup" to finish setting up your Sloane AI Phone Answering Service.
              </Typography>
            </Box>
          </Paper>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button
              variant="outlined"
              color="primary"
              onClick={onBack}
              sx={{ py: 1.5, px: 4 }}
              disabled={isSubmitting}
            >
              Back
            </Button>
            <Button
              // Remove type="submit" to prevent form validation
              variant="contained"
              color="primary"
              size="large"
              sx={{ py: 1.5, px: 4 }}
              disabled={isSubmitting}
              onClick={() => {
                console.log('Complete Setup button clicked directly');
                // Skip form validation entirely and just continue
                handleForceContinue(values);
              }}
            >
              Complete Setup
            </Button>
          </Box>
        </Form>
      )}
    </Formik>
  );
};

export default CalendarIntegrationForm;
