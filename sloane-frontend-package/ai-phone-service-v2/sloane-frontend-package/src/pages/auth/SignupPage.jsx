import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Container, 
  Grid, 
  Link, 
  InputAdornment, 
  IconButton,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const SignupSchema = Yup.object().shape({
  firstName: Yup.string()
    .required('First name is required'),
  lastName: Yup.string()
    .required('Last name is required'),
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password'), null], 'Passwords must match')
    .required('Confirm password is required'),
  businessName: Yup.string()
    .required('Business name is required')
});

const SignupPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [activeStep, setActiveStep] = useState(0);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const steps = ['Account Information', 'Business Details'];

  const handleSubmit = async (values, { setSubmitting }) => {
    if (activeStep === 0) {
      setActiveStep(1);
      setSubmitting(false);
      return;
    }

    try {
      setError('');
      const userData = {
        firstName: values.firstName,
        lastName: values.lastName,
        email: values.email,
        password: values.password,
        businessName: values.businessName,
        businessType: values.businessType || '',
        phoneNumber: values.phoneNumber || ''
      };
      
      await signup(userData);
      navigate('/onboarding');
    } catch (err) {
      setError(err.message || 'Failed to create account. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    setActiveStep(0);
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Create your account
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Get started with Sloane AI Phone Answering Service
            </Typography>
          </Box>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Formik
            initialValues={{
              firstName: '',
              lastName: '',
              email: '',
              password: '',
              confirmPassword: '',
              businessName: '',
              businessType: '',
              phoneNumber: ''
            }}
            validationSchema={SignupSchema}
            onSubmit={handleSubmit}
          >
            {({ errors, touched, isSubmitting }) => (
              <Form>
                <Grid container spacing={3}>
                  {activeStep === 0 ? (
                    <>
                      <Grid item xs={12} sm={6}>
                        <Field name="firstName">
                          {({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="First Name"
                              variant="outlined"
                              error={touched.firstName && Boolean(errors.firstName)}
                              helperText={touched.firstName && errors.firstName}
                            />
                          )}
                        </Field>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Field name="lastName">
                          {({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Last Name"
                              variant="outlined"
                              error={touched.lastName && Boolean(errors.lastName)}
                              helperText={touched.lastName && errors.lastName}
                            />
                          )}
                        </Field>
                      </Grid>
                      <Grid item xs={12}>
                        <Field name="email">
                          {({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Email Address"
                              variant="outlined"
                              error={touched.email && Boolean(errors.email)}
                              helperText={touched.email && errors.email}
                            />
                          )}
                        </Field>
                      </Grid>
                      <Grid item xs={12}>
                        <Field name="password">
                          {({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Password"
                              type={showPassword ? 'text' : 'password'}
                              variant="outlined"
                              error={touched.password && Boolean(errors.password)}
                              helperText={touched.password && errors.password}
                              InputProps={{
                                endAdornment: (
                                  <InputAdornment position="end">
                                    <IconButton
                                      onClick={() => setShowPassword(!showPassword)}
                                      edge="end"
                                    >
                                      {showPassword ? <VisibilityOff /> : <Visibility />}
                                    </IconButton>
                                  </InputAdornment>
                                )
                              }}
                            />
                          )}
                        </Field>
                      </Grid>
                      <Grid item xs={12}>
                        <Field name="confirmPassword">
                          {({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Confirm Password"
                              type={showConfirmPassword ? 'text' : 'password'}
                              variant="outlined"
                              error={touched.confirmPassword && Boolean(errors.confirmPassword)}
                              helperText={touched.confirmPassword && errors.confirmPassword}
                              InputProps={{
                                endAdornment: (
                                  <InputAdornment position="end">
                                    <IconButton
                                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                      edge="end"
                                    >
                                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                                    </IconButton>
                                  </InputAdornment>
                                )
                              }}
                            />
                          )}
                        </Field>
                      </Grid>
                    </>
                  ) : (
                    <>
                      <Grid item xs={12}>
                        <Field name="businessName">
                          {({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Business Name"
                              variant="outlined"
                              error={touched.businessName && Boolean(errors.businessName)}
                              helperText={touched.businessName && errors.businessName}
                            />
                          )}
                        </Field>
                      </Grid>
                      <Grid item xs={12}>
                        <Field name="businessType">
                          {({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Business Type (Optional)"
                              variant="outlined"
                              error={touched.businessType && Boolean(errors.businessType)}
                              helperText={touched.businessType && errors.businessType}
                            />
                          )}
                        </Field>
                      </Grid>
                      <Grid item xs={12}>
                        <Field name="phoneNumber">
                          {({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Phone Number (Optional)"
                              variant="outlined"
                              error={touched.phoneNumber && Boolean(errors.phoneNumber)}
                              helperText={touched.phoneNumber && errors.phoneNumber}
                            />
                          )}
                        </Field>
                      </Grid>
                    </>
                  )}
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: activeStep === 0 ? 'flex-end' : 'space-between' }}>
                      {activeStep === 1 && (
                        <Button
                          onClick={handleBack}
                          variant="outlined"
                          sx={{ mr: 1 }}
                        >
                          Back
                        </Button>
                      )}
                      <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        size="large"
                        disabled={isSubmitting}
                        sx={{ py: 1.5, px: 4 }}
                      >
                        {isSubmitting ? (
                          <CircularProgress size={24} color="inherit" />
                        ) : activeStep === 0 ? (
                          'Continue'
                        ) : (
                          'Create Account'
                        )}
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </Form>
            )}
          </Formik>

          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Already have an account?{' '}
              <Link
                component={RouterLink}
                to="/login"
                variant="body2"
                color="primary"
                underline="hover"
              >
                Sign in
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default SignupPage;
