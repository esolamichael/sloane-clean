import React from 'react';
import { Box, Typography, Button, Container, Grid, useTheme } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const HeroSection = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        background: `linear-gradient(135deg, ${theme.palette.background.light} 0%, ${theme.palette.background.default} 100%)`,
        pt: { xs: 8, md: 12 },
        pb: { xs: 8, md: 12 },
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
              <Typography
                variant="h1"
                component="h1"
                color="text.primary"
                sx={{
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  fontWeight: 700,
                  mb: 2,
                }}
              >
                AI answering service for your business calls.
              </Typography>
              
              <Typography
                variant="h5"
                component="p"
                color="text.secondary"
                sx={{ mb: 4, fontWeight: 400 }}
              >
                10x better than voicemail. 10x cheaper than an answering service. Grow your business while Sloane answers your calls, helps set appointments, and sends you the messages.
              </Typography>
              
              <Button
                component={RouterLink}
                to="/signup"
                variant="contained"
                color="primary"
                size="large"
                sx={{ 
                  py: 1.5, 
                  px: 4,
                  fontSize: '1.1rem',
                  boxShadow: theme.shadows[4],
                  mr: { xs: 0, md: 2 },
                  mb: { xs: 2, md: 0 },
                }}
              >
                Get Started for Free
              </Button>
              
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mt: 2 }}
              >
                First 25 minutes completely free. No credit card required.
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                position: 'relative',
              }}
            >
              <Box
                component="img"
                src="/dashboard-preview.png"
                alt="Sloane AI Phone Service Dashboard"
                sx={{
                  width: '100%',
                  maxWidth: 600,
                  height: 'auto',
                  borderRadius: 2,
                  boxShadow: theme.shadows[10],
                }}
              />
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default HeroSection;
