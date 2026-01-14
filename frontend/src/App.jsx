import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import HistoryPage from './pages/HistoryPage';
import { Toaster } from '@/components/ui/toaster';

function App() {
  return (
    <ThemeProvider defaultTheme="dark">
      <BrowserRouter>
        <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
          <Navbar />
          <main className="container mx-auto px-4 pt-24 pb-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/dashboard/:sessionId" element={<DashboardPage />} />
              <Route path="/history" element={<HistoryPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
      <Toaster />
    </ThemeProvider>
  );
}

export default App;
