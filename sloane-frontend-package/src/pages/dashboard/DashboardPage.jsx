import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  Card, 
  CardContent,
  Button,
  CircularProgress,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import PhoneInTalkIcon from '@mui/icons-material/PhoneInTalk';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import EventNoteIcon from '@mui/icons-material/EventNote';
import PersonIcon from '@mui/icons-material/Person';
import { useAuth } from '../../contexts/AuthContext';
import callsApi from '../../api/calls';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const DashboardPage = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [callData, setCallData] = useState({
    recentCalls: [],
    callStats: {
      total: 0,
      answered: 0,
      missed: 0,
      appointments: 0
    }
  });
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // In a real implementation, we would fetch actual data from the backend
        const callHistory = await callsApi.getCallHistory({ limit: 5 });
        const analytics = await callsApi.getCallAnalytics();
        
        setCallData({
          recentCalls: callHistory.calls || [],
          callStats: {
            total: analytics.totalCalls || 0,
            answered: analytics.answeredCalls || 0,
            missed: analytics.missedCalls || 0,
            appointments: analytics.appointmentsScheduled || 0
          }
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Set some mock data for demonstration
        setCallData({
          recentCalls: [
            { 
              id: '1', 
              callerName: 'John Smith', 
              callerNumber: '(555) 123-4567', 
              timestamp: new Date().toISOString(),
              duration: '2:34',
              status: 'answered',
              message: 'Called about scheduling a consultation next week.'
            },
            { 
              id: '2', 
              callerName: 'Sarah Johnson', 
              callerNumber: '(555) 987-6543', 
              timestamp: new Date(Date.now() - 3600000).toISOString(),
              duration: '1:45',
              status: 'answered',
              message: 'Had questions about your services and pricing.'
            },
            { 
              id: '3', 
              callerName: 'Unknown Caller', 
              callerNumber: '(555) 555-5555', 
              timestamp: new Date(Date.now() - 7200000).toISOString(),
              duration: '0:58',
              status: 'missed',
              message: 'Left no message.'
            }
          ],
          callStats: {
            total: 24,
            answered: 18,
            missed: 6,
            appointments: 8
          }
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome back, {currentUser?.firstName || 'User'}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your Sloane AI Phone Service
        </Typography>
      </Box>

      {loading ? (
          <LoadingSpinner message="Loading dashboard data..." />
      ) : (
        <>
          {/* Dashboard content */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <PhoneInTalkIcon color="primary" sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" component="div">
                      {callData.callStats.total}
                    </Typography>
                  </Box>
                  <Typography color="text.secondary">
                    Total Calls
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AccessTimeIcon color="success" sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" component="div">
                      {callData.callStats.answered}
                    </Typography>
                  </Box>
                  <Typography color="text.secondary">
                    Answered Calls
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <EventNoteIcon color="info" sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" component="div">
                      {callData.callStats.appointments}
                    </Typography>
                  </Box>
                  <Typography color="text.secondary">
                    Appointments Scheduled
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <PersonIcon color="warning" sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" component="div">
                      {callData.callStats.missed}
                    </Typography>
                  </Box>
                  <Typography color="text.secondary">
                    Missed Calls
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Paper sx={{ mb: 4 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
                <Tab label="Recent Calls" />
                <Tab label="Upcoming Appointments" />
                <Tab label="Analytics" />
              </Tabs>
            </Box>
            
            <Box sx={{ p: 3 }}>
              {tabValue === 0 && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Recent Calls
                  </Typography>
                  
                  {callData.recentCalls.length === 0 ? (
                    <Typography variant="body1" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                      No recent calls to display.
                    </Typography>
                  ) : (
                    <Box>
                      {callData.recentCalls.map((call, index) => (
                        <React.Fragment key={call.id}>
                          {index > 0 && <Divider sx={{ my: 2 }} />}
                          <Grid container spacing={2}>
                            <Grid item xs={12} sm={4}>
                              <Typography variant="subtitle1">
                                {call.callerName || 'Unknown Caller'}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {call.callerNumber}
                              </Typography>
                            </Grid>
                            <Grid item xs={12} sm={3}>
                              <Typography variant="body2">
                                {formatDate(call.timestamp)}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                Duration: {call.duration}
                              </Typography>
                            </Grid>
                            <Grid item xs={12} sm={5}>
                              <Typography variant="body2">
                                <Box component="span" sx={{ 
                                  color: call.status === 'answered' ? 'success.main' : 'error.main',
                                  fontWeight: 'medium'
                                }}>
                                  {call.status === 'answered' ? 'Answered' : 'Missed'}
                                </Box>
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {call.message}
                              </Typography>
                            </Grid>
                          </Grid>
                        </React.Fragment>
                      ))}
                      
                      <Box sx={{ mt: 3, textAlign: 'center' }}>
                        <Button variant="outlined" color="primary">
                          View All Calls
                        </Button>
                      </Box>
                    </Box>
                  )}
                </>
              )}
              
              {tabValue === 1 && (
                <Typography variant="body1" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                  No upcoming appointments to display.
                </Typography>
              )}
              
              {tabValue === 2 && (
                <Typography variant="body1" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                  Call analytics will be displayed here.
                </Typography>
              )}
            </Box>
          </Paper>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Button variant="outlined" fullWidth sx={{ py: 1.5 }}>
                      Update Business Hours
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button variant="outlined" fullWidth sx={{ py: 1.5 }}>
                      Manage Services
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button variant="outlined" fullWidth sx={{ py: 1.5 }}>
                      Connect Calendar
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button variant="outlined" fullWidth sx={{ py: 1.5 }}>
                      Phone Settings
                    </Button>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  System Status
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Phone Number: <Box component="span" sx={{ fontWeight: 'medium' }}>(555) 123-4567</Box>
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Status: <Box component="span" sx={{ color: 'success.main', fontWeight: 'medium' }}>Active</Box>
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Minutes Used: <Box component="span" sx={{ fontWeight: 'medium' }}>45 / 100</Box>
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Current Plan: <Box component="span" sx={{ fontWeight: 'medium' }}>Basic</Box>
                  </Typography>
                </Box>
                <Button variant="contained" color="primary" sx={{ mt: 1 }}>
                  Upgrade Plan
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </>
      )}
    </Container>
  );
};

export default DashboardPage;
