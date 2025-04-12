import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  CircularProgress,
  TextField,
  InputAdornment,
  IconButton
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import DownloadIcon from '@mui/icons-material/Download';
import callsApi from '../../api/calls';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { enhancedApiCall } from '../../utils/ErrorHandling';

const CallHistoryPage = () => {
  const [loading, setLoading] = useState(true);
  const [calls, setCalls] = useState([]);
  const [totalCalls, setTotalCalls] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all'
  });

  useEffect(() => {
    fetchCalls();
  }, [page, rowsPerPage, searchQuery, filters]);

const fetchCalls = async () => {
  try {
    setLoading(true);
    const params = {
      page: page + 1,
      limit: rowsPerPage,
      search: searchQuery || undefined,
      status: filters.status !== 'all' ? filters.status : undefined,
      dateRange: filters.dateRange !== 'all' ? filters.dateRange : undefined
    };
    
    const response = await enhancedApiCall(callsApi.getCallHistory, params);
    
    // In a real implementation, we would use the actual data from the backend
    // For now, we'll simulate some data
    const mockCalls = Array.from({ length: 25 }, (_, i) => ({
      id: `call-${i + 1}`,
      callerName: `Caller ${i + 1}`,
      callerNumber: `(555) ${100 + i}-${1000 + i}`,
      timestamp: new Date(Date.now() - (i * 3600000)).toISOString(),
      duration: `${Math.floor(Math.random() * 5)}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`,
      status: Math.random() > 0.3 ? 'answered' : 'missed',
      message: Math.random() > 0.2 ? 'Left a message about services and pricing.' : 'No message left.'
    }));
    
    setCalls(mockCalls.slice(page * rowsPerPage, (page + 1) * rowsPerPage));
    setTotalCalls(mockCalls.length);
  } catch (error) {
    console.error('Error fetching call history:', error);
    setCalls([]);
  } finally {
    setLoading(false);
  }
};

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
    setPage(0);
  };

  const handleExport = async (format) => {
    try {
      await callsApi.exportCallHistory(format, {
        search: searchQuery || undefined,
        status: filters.status !== 'all' ? filters.status : undefined,
        dateRange: filters.dateRange !== 'all' ? filters.dateRange : undefined
      });
      
      // In a real implementation, this would download a file
      alert(`Exporting call history as ${format.toUpperCase()}`);
    } catch (error) {
      console.error(`Error exporting call history as ${format}:`, error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Call History
        </Typography>
        <Typography variant="body1" color="text.secondary">
          View and manage all calls handled by Sloane
        </Typography>
      </Box>

      <Paper sx={{ mb: 4, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              placeholder="Search calls..."
              value={searchQuery}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              variant="outlined"
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={8}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
              <Button
                startIcon={<FilterListIcon />}
                variant="outlined"
                size="small"
              >
                Filter
              </Button>
              <Button
                startIcon={<DownloadIcon />}
                variant="outlined"
                size="small"
                onClick={() => handleExport('csv')}
              >
                Export CSV
              </Button>
              <Button
                startIcon={<DownloadIcon />}
                variant="outlined"
                size="small"
                onClick={() => handleExport('pdf')}
              >
                Export PDF
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Paper>
        {loading ? (
          <LoadingSpinner message="Loading call history..." />
        ) : (
          <>
            {/* Call history table content */}
          </>
        )}
              <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Caller</TableCell>
                    <TableCell>Phone Number</TableCell>
                    <TableCell>Date & Time</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Message</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {calls.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                        No calls found
                      </TableCell>
                    </TableRow>
                  ) : (
                    calls.map((call) => (
                      <TableRow key={call.id}>
                        <TableCell>{call.callerName}</TableCell>
                        <TableCell>{call.callerNumber}</TableCell>
                        <TableCell>{formatDate(call.timestamp)}</TableCell>
                        <TableCell>{call.duration}</TableCell>
                        <TableCell>
                          <Box component="span" sx={{ 
                            color: call.status === 'answered' ? 'success.main' : 'error.main',
                            fontWeight: 'medium'
                          }}>
                            {call.status === 'answered' ? 'Answered' : 'Missed'}
                          </Box>
                        </TableCell>
                        <TableCell>{call.message}</TableCell>
                        <TableCell>
                          <Button size="small" variant="text">
                            Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={totalCalls}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </>
        )}
      </Paper>
    </Container>
  );
};

export default CallHistoryPage;
