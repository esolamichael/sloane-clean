import React from 'react';
import { Box, Typography, Container, Grid, Card, CardContent, CardMedia, useTheme } from '@mui/material';

const HowItWorksSection = () => {
  const theme = useTheme();
  
  const steps = [
    {
      title: "Sign up and set up your profile",
      description: "Create your account, add your business information, and customize how Sloane should answer your calls.",
      image: "/images/setup-profile.png"
    },
    {
      title: "Connect your phone number",
      description: "Forward your existing business number to Sloane or get a new dedicated number for your business.",
      image: "/images/connect-phone.png"
    },
    {
      title: "Sloane answers your calls",
      description: "When you can't answer, Sloane steps in to professionally handle calls, collect information, and schedule appointments.",
      image: "/images/answer-calls.png"
    },
    {
      title: "Get notified instantly",
      description: "Receive real-time notifications with call details, transcripts, and scheduled appointments via email or text.",
      image: "/images/get-notified.png"
    }
  ];

  return (
    <Box
      sx={{
        py: { xs: 8, md: 12 },
        backgroundColor: theme.palette.background.default,
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography
            variant="h2"
            component="h2"
            color="text.primary"
            sx={{ mb: 2 }}
          >
            How it Works
          </Typography>
          <Typography
            variant="h5"
            component="p"
            color="text.secondary"
            sx={{ maxWidth: 700, mx: 'auto' }}
          >
            Powerful, yet super easy to set up and get started in minutes.
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {steps.map((step, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 3,
                  overflow: 'hidden',
                  boxShadow: theme.shadows[2],
                  transition: 'transform 0.3s, box-shadow 0.3s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: theme.shadows[8],
                  },
                }}
              >
                <Box sx={{ position: 'relative' }}>
                  <CardMedia
                    component="div"
                    sx={{
                      height: 200,
                      backgroundColor: theme.palette.primary.light,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography
                      variant="h1"
                      sx={{
                        color: 'white',
                        opacity: 0.3,
                        fontWeight: 700,
                        fontSize: '8rem',
                      }}
                    >
                      {index + 1}
                    </Typography>
                  </CardMedia>
                </Box>
                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                  <Typography variant="h5" component="h3" gutterBottom>
                    {step.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {step.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default HowItWorksSection;
