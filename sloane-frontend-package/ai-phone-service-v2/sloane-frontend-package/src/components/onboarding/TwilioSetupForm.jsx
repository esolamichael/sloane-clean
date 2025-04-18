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
  phoneSetupOption: Yup.string().required('Please select a phone setup option'),
  existingPhoneNumber: Yup.string().when('phoneSetupOption', {
    is: 'forward',
    then: Yup.string().required('Your existing phone number is required')
  }),
  callHandlingPreference: Yup.string().required('Please select a call handling preference'),
  voicemailGreeting: Yup.string().max(500, 'Greeting must be 500 characters or less')
});

const TwilioSetupForm = ({ initialData = {}, onSubmit, onBack }) => {
  return (
    <Formik
      initialValues={{
        phoneSetupOption: initialData.phoneSetupOption || 'new',
        existingPhoneNumber: initialData.existingPhoneNumber || '',
        callHandlingPreference: initialData.callHandlingPreference || 'answer_all',
        voicemailGreeting: initialData.voicemailGreeting || ''
      }}
      validationSchema={TwilioSetupSchema}
      onSubmit={(values) => {
        onSubmit(values);
      }}
    >
      {({ errors, touched, values, handleChange }) => (
        <Form>
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
                <Field name="existingPhoneNumber">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Your Existing Business Phone Number"
                      variant="outlined"
                      placeholder="e.g. (555) 123-4567"
                      error={touched.existingPhoneNumber && Boolean(errors.existingPhoneNumber)}
                      helperText={touched.existingPhoneNumber && errors.existingPhoneNumber}
                      sx={{ mb: 3 }}
                    />
                  )}
                </Field>
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
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              sx={{ py: 1.5, px: 4 }}
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
