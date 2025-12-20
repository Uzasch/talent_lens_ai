import { Trophy } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDate } from '@/lib/utils';

function PoolCandidatesTable({ candidates, loading }) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (candidates.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No candidates in this pool yet.
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12">#</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Email</TableHead>
            <TableHead className="text-right">Match</TableHead>
            <TableHead>Added</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {candidates.map((candidate, index) => (
            <TableRow key={candidate.id}>
              <TableCell className="font-medium">
                {candidate.rank || index + 1}
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  {candidate.rank === 1 && (
                    <Trophy className="h-4 w-4 text-yellow-500" />
                  )}
                  {candidate.name}
                </div>
              </TableCell>
              <TableCell>
                <span className="text-muted-foreground text-sm">
                  {candidate.email || 'No email'}
                </span>
              </TableCell>
              <TableCell className="text-right">
                {candidate.match_score ? (
                  <span className={`font-medium ${
                    candidate.match_score >= 80
                      ? 'text-primary'
                      : candidate.match_score >= 60
                      ? 'text-yellow-500'
                      : 'text-muted-foreground'
                  }`}>
                    {candidate.match_score}%
                  </span>
                ) : (
                  <span className="text-muted-foreground">-</span>
                )}
              </TableCell>
              <TableCell>
                <span className="text-muted-foreground text-sm">
                  {formatDate(candidate.uploaded_at)}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export default PoolCandidatesTable;
