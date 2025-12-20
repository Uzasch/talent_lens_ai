import { Info, Users, UserMinus, TrendingDown, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

function WhyNotOthers({ stats, whyNotOthersText, commonGaps }) {
  const {
    total_in_pool,
    ranked_count,
    eliminated_count
  } = stats || {};

  // Calculate candidates ranked below top 6
  const topShown = Math.min(ranked_count || 0, 6);
  const belowTop6 = (ranked_count || 0) - topShown;

  // Edge case: all candidates shown (pool <= 6 and none eliminated)
  if (total_in_pool <= 6 && eliminated_count === 0) {
    return (
      <Card className="mt-8 bg-primary/5 border-primary/30">
        <CardContent className="p-6">
          <p className="text-sm text-primary flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            All {total_in_pool} candidate{total_in_pool !== 1 ? 's' : ''} in pool are shown above
          </p>
        </CardContent>
      </Card>
    );
  }

  // Edge case: nothing to explain
  if (!total_in_pool || (eliminated_count === 0 && belowTop6 === 0)) {
    return null;
  }

  return (
    <Card className="mt-8 bg-muted/30">
      <CardContent className="p-6">
        <div className="flex items-start gap-3">
          <Info className="h-5 w-5 text-muted-foreground mt-0.5 shrink-0" />
          <div className="space-y-4 flex-1">
            <h3 className="font-medium">Why Not Others?</h3>

            {/* Summary text from AI */}
            {whyNotOthersText && (
              <p className="text-sm text-muted-foreground leading-relaxed">
                {whyNotOthersText}
              </p>
            )}

            {/* Breakdown stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              {/* Total pool */}
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                <div>
                  <span className="font-medium">{total_in_pool}</span>
                  <span className="text-sm text-muted-foreground ml-1">
                    total in pool
                  </span>
                </div>
              </div>

              {/* Eliminated */}
              {eliminated_count > 0 && (
                <div className="flex items-center gap-2">
                  <UserMinus className="h-4 w-4 text-yellow-500" />
                  <div>
                    <span className="font-medium">{eliminated_count}</span>
                    <span className="text-sm text-muted-foreground ml-1">
                      eliminated by thresholds
                    </span>
                  </div>
                </div>
              )}

              {/* Below top 6 */}
              {belowTop6 > 0 && (
                <div className="flex items-center gap-2">
                  <TrendingDown className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <span className="font-medium">{belowTop6}</span>
                    <span className="text-sm text-muted-foreground ml-1">
                      ranked below top 6
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Common gaps analysis */}
            {commonGaps && commonGaps.length > 0 && (
              <div className="mt-3 pt-3 border-t border-border">
                <h4 className="text-sm font-medium mb-2">Common Gaps</h4>
                <ul className="space-y-1">
                  {commonGaps.map((gap, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-muted-foreground">•</span>
                      {gap}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Link to eliminated section */}
            {eliminated_count > 0 && (
              <p className="text-xs text-muted-foreground pt-1">
                See "Eliminated by Thresholds" section above for details.
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default WhyNotOthers;
