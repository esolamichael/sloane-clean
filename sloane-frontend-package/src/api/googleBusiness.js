import { google } from 'googleapis';
import express from 'express';

const router = express.Router();

// Configure OAuth client with credentials
const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  process.env.GOOGLE_REDIRECT_URI
);

// Generate authorization URL
router.get('/auth/google', (req, res) => {
  const scopes = [
    'https://www.googleapis.com/auth/business.manage',
  ];

  const url = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: scopes,
    include_granted_scopes: true,
  });
  
  res.redirect(url);
});

// Handle OAuth callback
router.get('/auth/google/callback', async (req, res) => {
  const { code } = req.query;
  
  try {
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);
    
    // Store tokens securely for this user
    // Consider encrypting before storing in database
    await storeTokensForUser(req.user.id, tokens);
    
    res.redirect('/dashboard/profile');
  } catch (error) {
    console.error('Error authenticating with Google:', error);
    res.redirect('/error?message=Authentication failed');
  }
});

// Get business accounts
router.get('/api/business/accounts', async (req, res) => {
  try {
    // Retrieve tokens for this user
    const tokens = await getTokensForUser(req.user.id);
    oauth2Client.setCredentials(tokens);
    
    const mybusiness = google.mybusinessaccountmanagement({
      version: 'v1',
      auth: oauth2Client
    });
    
    const response = await mybusiness.accounts.list();
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching business accounts:', error);
    res.status(500).json({ error: 'Failed to fetch business accounts' });
  }
});

// Get business locations
router.get('/api/business/locations', async (req, res) => {
  try {
    const { accountId } = req.query;
    const tokens = await getTokensForUser(req.user.id);
    oauth2Client.setCredentials(tokens);
    
    const mybusiness = google.mybusiness({
      version: 'v4',
      auth: oauth2Client
    });
    
    const response = await mybusiness.accounts.locations.list({
      parent: `accounts/${accountId}`
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching business locations:', error);
    res.status(500).json({ error: 'Failed to fetch business locations' });
  }
});

// Get detailed business information
router.get('/api/business/details', async (req, res) => {
  try {
    const { locationId } = req.query;
    const tokens = await getTokensForUser(req.user.id);
    oauth2Client.setCredentials(tokens);
    
    const mybusiness = google.mybusiness({
      version: 'v4',
      auth: oauth2Client
    });
    
    // Get basic information
    const locationDetails = await mybusiness.accounts.locations.get({
      name: locationId
    });
    
    // Get additional metadata like business hours
    // Note: Multiple API calls may be needed for complete information
    
    res.json({
      profile: locationDetails.data
      // Include other fetched data here
    });
  } catch (error) {
    console.error('Error fetching business details:', error);
    res.status(500).json({ error: 'Failed to fetch business details' });
  }
});
