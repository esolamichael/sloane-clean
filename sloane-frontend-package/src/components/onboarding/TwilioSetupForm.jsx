import React from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Grid, 
  Paper,
  TextField,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  Alert
} from '@mui/material';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';

const TwilioSetupSchema = Yup.object().shape({
  phoneSetupOption: Yup.string().default('new'),
  existingPhoneNumber: Yup.string().when('phoneSetupOption', {
    is: 'forward',
    then: Yup.string().nullable()
  }),
  callHandlingPreference: Yup.string().default('answer_all'),
  voicemailGreeting: Yup.string().max(500, 'Greeting must be 500 characters or less').nullable()
});

const TwilioSetupForm = ({ initialData = {}, businessInfo = {}, onSubmit, onBack }) => {
  // Extract phone number from business info if available
  const existingPhoneFromBusiness = businessInfo && businessInfo.phoneNumber ? businessInfo.phoneNumber : '';
  // Direct continuation function that bypasses form validation
  const handleForceContinue = (values) => {
    console.log('Force continuing with phone setup values:', values);
    
    // Process values to ensure they're valid
    const processedValues = { ...values };
    
    // Ensure values have defaults if they're missing
    if (!processedValues.phoneSetupOption) {
      processedValues.phoneSetupOption = 'new';
    }
    
    if (!processedValues.callHandlingPreference) {
      processedValues.callHandlingPreference = 'answer_all';
    }
    
    // If forward option is selected but no phone number is provided, use business phone
    if (processedValues.phoneSetupOption === 'forward' && 
        (!processedValues.existingPhoneNumber || processedValues.existingPhoneNumber.trim() === '')) {
      processedValues.existingPhoneNumber = existingPhoneFromBusiness;
    }
    
    // Call the parent component's onSubmit directly
    onSubmit(processedValues);
  };
  return (
    <Formik
      initialValues={{
        // Auto-select "forward" option if we have a business phone number
        phoneSetupOption: initialData.phoneSetupOption || (existingPhoneFromBusiness ? 'forward' : 'new'),
        existingPhoneNumber: initialData.existingPhoneNumber || existingPhoneFromBusiness || '',
        callHandlingPreference: initialData.callHandlingPreference || 'answer_all',
        voicemailGreeting: initialData.voicemailGreeting || ''
      }}
      validationSchema={TwilioSetupSchema}
      onSubmit={(values) => {
        onSubmit(values);
      }}
    >
      {({ errors, touched, values, handleChange }) => (
        <Form noValidate>
          {/* Hidden submit button that can be triggered programmatically if needed */}
          <button type="submit" style={{ display: 'none' }} />
          <Paper elevation={0} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Phone Setup
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Configure how Sloane will handle your business calls.
            </Typography>
            
            <Alert severity="info" sx={{ mb: 4 }}>
              Sloane uses Twilio to handle phone calls. We'll set up the integration for you after you complete this form.
            </Alert>
            
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Phone Number Options
              </Typography>
              
              <FormControl component="fieldset" fullWidth sx={{ mb: 3 }}>
                <RadioGroup
                  name="phoneSetupOption"
                  value={values.phoneSetupOption}
                  onChange={handleChange}
                >
                  <FormControlLabel 
                    value="new" 
                    control={<Radio />} 
                    label="Get a new phone number for my business" 
                  />
                  <FormControlLabel 
                    value="forward" 
                    control={<Radio />} 
                    label="Forward my existing business number to Sloane" 
                  />
                </RadioGroup>
                {touched.phoneSetupOption && errors.phoneSetupOption && (
                  <Typography color="error" variant="caption">
                    {errors.phoneSetupOption}
                  </Typography>
                )}
              </FormControl>
              
              {values.phoneSetupOption === 'forward' && (
                <>
                  {existingPhoneFromBusiness && (
                    <Alert severity="info" sx={{ mb: 2 }}>
                      We've retrieved your business phone number from your profile information.
                    </Alert>
                  )}
                  <Field name="existingPhoneNumber">
                    {({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Your Existing Business Phone Number"
                        variant="outlined"
                        placeholder="e.g. (555) 123-4567"
                        error={touched.existingPhoneNumber && Boolean(errors.existingPhoneNumber)}
                        helperText={
                          (touched.existingPhoneNumber && errors.existingPhoneNumber) ||
                          (existingPhoneFromBusiness && existingPhoneFromBusiness === field.value && 'Pre-filled from your business information')
                        }
                        sx={{ 
                          mb: 3,
                          backgroundColor: (existingPhoneFromBusiness && existingPhoneFromBusiness === field.value) ? 'rgba(25, 118, 210, 0.04)' : 'transparent' 
                        }}
                      />
                    )}
                  </Field>
                </>
              )}
            </Box>
            
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Call Handling Preferences
              </Typography>
              
              <FormControl component="fieldset" fullWidth sx={{ mb: 3 }}>
                <RadioGroup
                  name="callHandlingPreference"
                  value={values.callHandlingPreference}
                  onChange={handleChange}
                >
                  <FormControlLabel 
                    value="answer_all" 
                    control={<Radio />} 
                    label="Sloane answers all calls" 
                  />
                  <FormControlLabel 
                    value="after_hours" 
                    control={<Radio />} 
                    label="Sloane only answers calls outside business hours" 
                  />
                  <FormControlLabel 
                    value="overflow" 
                    control={<Radio />} 
                    label="Sloane answers calls when I don't pick up (after 3-4 rings)" 
                  />
                </RadioGroup>
                {touched.callHandlingPreference && errors.callHandlingPreference && (
                  <Typography color="error" variant="caption">
                    {errors.callHandlingPreference}
                  </Typography>
                )}
              </FormControl>
            </Box>
            
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Custom Voicemail Greeting (Optional)
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Sloane will use this greeting when taking messages. If left blank, we'll create a professional greeting based on your business information.
              </Typography>
              
              <Field name="voicemailGreeting">
                {({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    multiline
                    rows={4}
                    placeholder="Example: Thank you for calling [Your Business Name]. We're unable to take your call right now, but please leave a message with your name, number, and reason for calling, and we'll get back to you as soon as possible."
                    variant="outlined"
                    error={touched.voicemailGreeting && Boolean(errors.voicemailGreeting)}
                    helperText={
                      (touched.voicemailGreeting && errors.voicemailGreeting) || 
                      `${values.voicemailGreeting.length}/500 characters`
                    }
                  />
                )}
              </Field>
            </Box>
          </Paper>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button
              variant="outlined"
              color="primary"
              onClick={onBack}
              sx={{ py: 1.5, px: 4 }}
            >
              Back
            </Button>
            <Button
              // Remove type="submit" to prevent form validation
              variant="contained"
              color="primary"
              size="large"
              sx={{ py: 1.5, px: 4 }}
              onClick={() => {
                console.log('Continue button clicked directly');
                // Skip form validation entirely and just continue
                handleForceContinue(values);
              }}
            >
              Continue
            </Button>
          </Box>
        </Form>
      )}
    </Formik>
  );
};

export default TwilioSetupForm;
