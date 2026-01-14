import { Link, useLocation } from 'react-router-dom';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { Button } from '@/components/ui/button';

function Navbar() {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const linkClass = (path) =>
    `px-4 py-2 rounded-md transition-colors text-lg ${
      isActive(path)
        ? 'text-primary font-semibold'
        : 'text-muted-foreground hover:text-foreground'
    }`;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-card backdrop-blur supports-[backdrop-filter]:bg-card/95">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-2xl font-bold text-primary">
            TalentLens AI
          </Link>
          <div className="flex items-center space-x-2">
            <Link to="/" className={linkClass('/')}>
              Home
            </Link>
            <Link to="/history" className={linkClass('/history')}>
              History
            </Link>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="ml-2"
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
