import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Paper, 
  Divider,
  TextField,
  Button,
  CircularProgress
} from '@mui/material';

// Super simple dashboard with no external dependencies
const SuperSimpleDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState('2025-03-01');
  const [endDate, setEndDate] = useState('2025-04-01');

  // Mock data
  const stats = {
    totalCalls: 245,
    answeredCalls: 198,
    missedCalls: 47,
    answerRate: '80.8%',
    avgCallsPerDay: '8.2'
  };

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Call Analytics Dashboard
      </Typography>
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              label="Start Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              label="End Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button 
              variant="contained" 
              color="primary" 
              fullWidth
              onClick={handleRefresh}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Refresh Data'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Calls
              </Typography>
              <Typography variant="h4">
                {loading ? <CircularProgress size={24} /> : stats.totalCalls}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Answered Calls
              </Typography>
              <Typography variant="h4" color="primary">
                {loading ? <CircularProgress size={24} /> : stats.answeredCalls}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Missed Calls
              </Typography>
              <Typography variant="h4" color="error">
                {loading ? <CircularProgress size={24} /> : stats.missedCalls}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Answer Rate
              </Typography>
              <Typography variant="h4" color="success">
                {loading ? <CircularProgress size={24} /> : stats.answerRate}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg. Calls/Day
              </Typography>
              <Typography variant="h4">
                {loading ? <CircularProgress size={24} /> : stats.avgCallsPerDay}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Simple text-based data instead of charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Call Volume by Day
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1">Monday: 42 calls</Typography>
              <Typography variant="body1">Tuesday: 38 calls</Typography>
              <Typography variant="body1">Wednesday: 45 calls</Typography>
              <Typography variant="body1">Thursday: 51 calls</Typography>
              <Typography variant="body1">Friday: 39 calls</Typography>
              <Typography variant="body1">Saturday: 18 calls</Typography>
              <Typography variant="body1">Sunday: 12 calls</Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Call Type Distribution
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1">Appointment: 35%</Typography>
              <Typography variant="body1">Information: 25%</Typography>
              <Typography variant="body1">Support: 20%</Typography>
              <Typography variant="body1">Sales: 15%</Typography>
              <Typography variant="body1">Other: 5%</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SuperSimpleDashboard;
