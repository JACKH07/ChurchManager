import logoUrl from '../../assets/image/logochuch.png';
import { cn } from '../../utils/cn';

type AppLogoProps = {
  className?: string;
};

export const AppLogo = ({ className }: AppLogoProps) => (
  <img src={logoUrl} alt="ChurchManager" className={cn('object-contain', className)} />
);
