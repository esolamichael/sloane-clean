import React from 'react';
import { Box, Typography, Container, Grid, Card, CardContent, Avatar, useTheme } from '@mui/material';
import FormatQuoteIcon from '@mui/icons-material/FormatQuote';

const TestimonialsSection = () => {
  const theme = useTheme();
  
  const testimonials = [
    {
      quote: "As someone with 50 years of business experience, I've had many live receptionists and used answering services over the years. After using Sloane AI, I fired my live answering service yesterday because Sloane provides more accuracy, faster responses, and 24/7 availability—all at a fraction of the cost.",
      name: "James Hanner",
      title: "Owner, Southern Indiana Driving School",
      avatar: "/avatars/testimonial1.jpg"
    },
    {
      quote: "Sloane has been a game-changer for my small business. I used to miss calls all the time when I was with clients, but now Sloane handles everything professionally. My clients love it, and I've seen a 30% increase in appointments since implementing it.",
      name: "Sarah Johnson",
      title: "Owner, Bright Smile Dental Care",
      avatar: "/avatars/testimonial2.jpg"
    },
    {
      quote: "The AI technology behind Sloane is incredible. Callers often don't realize they're talking to an AI assistant. It captures all the information I need and sends it directly to me. It's like having a full-time receptionist at a tiny fraction of the cost.",
      name: "Michael Chen",
      title: "Founder, Chen Legal Services",
      avatar: "/avatars/testimonial3.jpg"
    }
  ];

  return (
    <Box
      sx={{
        py: { xs: 8, md: 12 },
        backgroundColor: theme.palette.background.light,
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
            Some of our happy clients...
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {testimonials.map((testimonial, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 3,
                  boxShadow: theme.shadows[2],
                  position: 'relative',
                  overflow: 'visible',
                }}
              >
                <Box
                  sx={{
                    position: 'absolute',
                    top: -20,
                    left: 20,
                    backgroundColor: theme.palette.primary.main,
                    borderRadius: '50%',
                    width: 40,
                    height: 40,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <FormatQuoteIcon sx={{ color: 'white' }} />
                </Box>
                <CardContent sx={{ flexGrow: 1, p: 4, pt: 5 }}>
                  <Typography variant="body1" paragraph sx={{ fontStyle: 'italic', mb: 3 }}>
                    "{testimonial.quote}"
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar 
                      src={testimonial.avatar} 
                      alt={testimonial.name}
                      sx={{ width: 50, height: 50, mr: 2 }}
                    />
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {testimonial.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {testimonial.title}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default TestimonialsSection;
