import { Container, Typography, Box, Paper } from '@mui/material';

export default function Home() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Bit-by-Bit Newsletter
          </Typography>
          <Typography variant="h5" component="h2" gutterBottom>
            Frontend V2
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome to the new frontend built with Next.js, TypeScript, and Material UI.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}

