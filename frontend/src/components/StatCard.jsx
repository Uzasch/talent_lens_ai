import { Card, CardContent } from '@/components/ui/card';

const variants = {
  default: 'text-foreground',
  success: 'text-primary',
  warning: 'text-yellow-500',
  muted: 'text-muted-foreground'
};

function StatCard({ label, value, subtext, icon: Icon, variant = 'default' }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className={`text-2xl font-bold ${variants[variant]}`}>
              {value}
            </p>
            {subtext && (
              <p className="text-xs text-muted-foreground mt-1">{subtext}</p>
            )}
          </div>
          {Icon && (
            <Icon className="h-8 w-8 text-muted-foreground" />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default StatCard;
