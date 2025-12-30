import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mdlApi } from '@/lib/api/mdl';
import { useToast } from '@/hooks/use-toast';

export function useManifests(dbConnectionId?: string) {
  return useQuery({
    queryKey: ['mdl-manifests', dbConnectionId],
    queryFn: () => mdlApi.list(dbConnectionId),
  });
}

export function useManifest(id: string | null) {
  return useQuery({
    queryKey: ['mdl-manifest', id],
    queryFn: () => mdlApi.get(id!),
    enabled: !!id,
  });
}

export function useBuildManifest() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: mdlApi.buildFromDatabase,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mdl-manifests'] });
      toast({ title: 'MDL manifest created successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to create manifest', description: error.message, variant: 'destructive' });
    },
  });
}

export function useDeleteManifest() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: mdlApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mdl-manifests'] });
      toast({ title: 'Manifest deleted' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to delete manifest', description: error.message, variant: 'destructive' });
    },
  });
}

export function useExportManifest() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (id: string) => {
      const json = await mdlApi.export(id);
      const blob = new Blob([JSON.stringify(json, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mdl-${id}.json`;
      a.click();
      URL.revokeObjectURL(url);
      return json;
    },
    onSuccess: () => {
      toast({ title: 'Manifest exported' });
    },
    onError: (error: Error) => {
      toast({ title: 'Export failed', description: error.message, variant: 'destructive' });
    },
  });
}
