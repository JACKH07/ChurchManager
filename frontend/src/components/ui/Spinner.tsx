import { cn } from '../../utils/cn';

interface SpinnerProps { size?: 'sm' | 'md' | 'lg'; className?: string; }

export const Spinner = ({ size = 'md', className }: SpinnerProps) => {
  const sizes = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' };
  return (
    <div className={cn('animate-spin rounded-full border-2 border-gray-200 border-t-primary-600', sizes[size], className)} />
  );
};

export const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="flex flex-col items-center gap-4">
      <Spinner size="lg" />
      <p className="text-gray-500 text-sm">Chargement...</p>
    </div>
  </div>
);
