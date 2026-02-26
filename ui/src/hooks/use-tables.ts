import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tablesApi } from '@/lib/api/tables';
import { useToast } from '@/hooks/use-toast';

export function useTables(dbConnectionId: string | null) {
  return useQuery({
    queryKey: ['tables', dbConnectionId],
    queryFn: () => tablesApi.list(dbConnectionId!),
    enabled: !!dbConnectionId,
  });
}

export function useTable(id: string | null) {
  return useQuery({
    queryKey: ['table', id],
    queryFn: () => tablesApi.get(id!),
    enabled: !!id,
  });
}

export function useScanTables() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (tableIds: string[]) => tablesApi.scan(tableIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tables'] });
      toast({ title: 'Scan started', description: 'AI descriptions will be generated in the background' });
    },
    onError: (error: Error) => {
      toast({ title: 'Scan failed', description: error.message, variant: 'destructive' });
    },
  });
}
