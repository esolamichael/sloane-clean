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
  CircularProgress,
  useTheme
} from '@mui/material';
import { Link as RouterLink, useParams, useNavigate } from 'react-router-dom';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';

const ResetPasswordSchema = Yup.object().shape({
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password'), null], 'Passwords must match')
    .required('Confirm password is required')
});

const ResetPasswordPage = () => {
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const { resetPassword } = useAuth();
  const { token } = useParams();
  const navigate = useNavigate();
  const theme = useTheme();

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      await resetPassword(token, values.password);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      setError(err.message || 'Failed to reset password. Please try again.');
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
              Reset Password
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Enter your new password below
            </Typography>
          </Box>

          {success ? (
            <Alert severity="success" sx={{ mb: 3 }}>
              Password reset successful! You will be redirected to the login page shortly.
            </Alert>
          ) : (
            <>
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {!token && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  Invalid or missing reset token. Please request a new password reset link.
                </Alert>
              )}

              {token && (
                <Formik
                  initialValues={{ password: '', confirmPassword: '' }}
                  validationSchema={ResetPasswordSchema}
                  onSubmit={handleSubmit}
                >
                  {({ errors, touched, isSubmitting }) => (
                    <Form>
                      <Grid container spacing={3}>
                        <Grid item xs={12}>
                          <Field name="password">
                            {({ field }) => (
                              <TextField
                                {...field}
                                fullWidth
                                label="New Password"
                                type="password"
                                variant="outlined"
                                error={touched.password && Boolean(errors.password)}
                                helperText={touched.password && errors.password}
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
                                label="Confirm New Password"
                                type="password"
                                variant="outlined"
                                error={touched.confirmPassword && Boolean(errors.confirmPassword)}
                                helperText={touched.confirmPassword && errors.confirmPassword}
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
                              'Reset Password'
                            )}
                          </Button>
                        </Grid>
                      </Grid>
                    </Form>
                  )}
                </Formik>
              )}
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

export default ResetPasswordPage;
