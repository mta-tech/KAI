import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { connectionsApi } from '@/lib/api/connections';
import type { CreateConnectionRequest } from '@/lib/api/types';
import { useToast } from '@/hooks/use-toast';

export function useConnections() {
  return useQuery({
    queryKey: ['connections'],
    queryFn: connectionsApi.list,
  });
}

export function useCreateConnection() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: CreateConnectionRequest) => connectionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast({ title: 'Connection created successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to create connection', description: error.message, variant: 'destructive' });
    },
  });
}

export function useUpdateConnection() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CreateConnectionRequest }) =>
      connectionsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast({ title: 'Connection updated successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to update connection', description: error.message, variant: 'destructive' });
    },
  });
}

export function useDeleteConnection() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => connectionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast({ title: 'Connection deleted successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to delete connection', description: error.message, variant: 'destructive' });
    },
  });
}
