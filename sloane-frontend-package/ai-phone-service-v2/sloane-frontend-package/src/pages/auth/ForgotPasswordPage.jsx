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
  Alert,
  CircularProgress
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';

const ForgotPasswordSchema = Yup.object().shape({
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required')
});

const ForgotPasswordPage = () => {
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const { forgotPassword } = useAuth();

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      await forgotPassword(values.email);
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to send password reset email. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Forgot Password
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Enter your email address and we'll send you a link to reset your password
            </Typography>
          </Box>

          {success ? (
            <Alert severity="success" sx={{ mb: 3 }}>
              Password reset email sent! Please check your inbox and follow the instructions.
            </Alert>
          ) : (
            <>
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              <Formik
                initialValues={{ email: '' }}
                validationSchema={ForgotPasswordSchema}
                onSubmit={handleSubmit}
              >
                {({ errors, touched, isSubmitting }) => (
                  <Form>
                    <Grid container spacing={3}>
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
                        <Button
                          type="submit"
                          fullWidth
                          variant="contained"
                          color="primary"
                          size="large"
                          disabled={isSubmitting}
                          sx={{ py: 1.5 }}
                        >
                          {isSubmitting ? (
                            <CircularProgress size={24} color="inherit" />
                          ) : (
                            'Send Reset Link'
                          )}
                        </Button>
                      </Grid>
                    </Grid>
                  </Form>
                )}
              </Formik>
            </>
          )}

          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Remember your password?{' '}
              <Link
                component={RouterLink}
                to="/login"
                variant="body2"
                color="primary"
                underline="hover"
              >
                Back to login
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default ForgotPasswordPage;
