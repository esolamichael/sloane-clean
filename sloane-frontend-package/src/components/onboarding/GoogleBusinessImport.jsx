import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  CircularProgress, 
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider 
} from '@mui/material';
import api from '../../api';

const GoogleBusinessImport = ({ onDataImported }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [accounts, setAccounts] = useState([]);
  const [locations, setLocations] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [businessData, setBusinessData] = useState(null);
  const [error, setError] = useState(null);

  // Fetch accounts after user authentication
  const fetchAccounts = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/api/business/accounts');
      setAccounts(response.data.accounts || []);
    } catch (err) {
      setError('Failed to fetch business accounts. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch locations for a selected account
  const fetchLocations = async (accountId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/api/business/locations?accountId=${accountId}`);
      setLocations(response.data.locations || []);
    } catch (err) {
      setError('Failed to fetch business locations. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch detailed business information
  const fetchBusinessDetails = async (locationId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/api/business/details?locationId=${locationId}`);
      setBusinessData(response.data.profile);
      
      // Pass data to parent component
      if (onDataImported && response.data.profile) {
        onDataImported(response.data.profile);
      }
    } catch (err) {
      setError('Failed to fetch business details. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle account selection
  const handleSelectAccount = (account) => {
    setSelectedAccount(account);
    fetchLocations(account.name);
  };

  // Handle location selection
  const handleSelectLocation = (location) => {
    setSelectedLocation(location);
    fetchBusinessDetails(location.name);
  };

  // Start the authentication process
  const handleConnectGoogle = () => {
    window.location.href = '/auth/google';
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Import from Google Business Profile
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {!accounts.length ? (
        <Button
          variant="contained"
          color="primary"
          onClick={handleConnectGoogle}
          startIcon={<img src="/google-icon.svg" alt="" width="18" height="18" />}
          disabled={isLoading}
        >
          {isLoading ? <CircularProgress size={24} /> : 'Connect Google Business Profile'}
        </Button>
      ) : (
        <Box>
          {!selectedAccount ? (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Select a business account:
              </Typography>
              <List>
                {accounts.map((account) => (
                  <React.Fragment key={account.name}>
                    <ListItem 
                      button 
                      onClick={() => handleSelectAccount(account)}
                    >
                      <ListItemText 
                        primary={account.accountName} 
                        secondary={account.type} 
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Box>
          ) : !selectedLocation ? (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Select a business location:
              </Typography>
              {isLoading ? (
                <CircularProgress size={24} />
              ) : (
                <List>
                  {locations.map((location) => (
                    <React.Fragment key={location.name}>
                      <ListItem 
                        button 
                        onClick={() => handleSelectLocation(location)}
                      >
                        <ListItemText 
                          primary={location.locationName} 
                          secondary={location.address?.addressLines?.join(', ')} 
                        />
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              )}
              <Button 
                variant="text" 
                onClick={() => setSelectedAccount(null)}
                sx={{ mt: 2 }}
              >
                Back to Accounts
              </Button>
            </Box>
          ) : (
            <Box>
              {businessData ? (
                <Card variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6">{businessData.locationName}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {businessData.address?.addressLines?.join(', ')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {businessData.primaryPhone}
                    </Typography>
                    <Alert severity="success" sx={{ mt: 2 }}>
                      Business profile imported successfully!
                    </Alert>
                  </CardContent>
                </Card>
              ) : isLoading ? (
                <CircularProgress size={24} />
              ) : null}
              
              <Button 
                variant="text" 
                onClick={() => {
                  setSelectedLocation(null);
                  setBusinessData(null);
                }}
                sx={{ mt: 2 }}
              >
                Select Different Location
              </Button>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default GoogleBusinessImport;
