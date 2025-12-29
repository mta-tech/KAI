import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { glossaryApi, instructionsApi } from '@/lib/api/knowledge';
import { useToast } from '@/hooks/use-toast';

export function useGlossary(dbConnectionId: string | null) {
  return useQuery({
    queryKey: ['glossary', dbConnectionId],
    queryFn: () => glossaryApi.list(dbConnectionId!),
    enabled: !!dbConnectionId,
  });
}

export function useCreateGlossary() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ dbConnectionId, data }: { 
      dbConnectionId: string; 
      data: { term: string; definition: string; synonyms?: string[]; related_tables?: string[] } 
    }) => glossaryApi.create(dbConnectionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['glossary'] });
      toast({ title: 'Term added to glossary' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to add term', description: error.message, variant: 'destructive' });
    },
  });
}

export function useUpdateGlossary() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { 
      id: string; 
      data: { term?: string; definition?: string; synonyms?: string[]; related_tables?: string[] } 
    }) => glossaryApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['glossary'] });
      toast({ title: 'Term updated' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to update term', description: error.message, variant: 'destructive' });
    },
  });
}

export function useDeleteGlossary() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => glossaryApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['glossary'] });
      toast({ title: 'Term deleted' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to delete term', description: error.message, variant: 'destructive' });
    },
  });
}

export function useInstructions(dbConnectionId: string | null) {
  return useQuery({
    queryKey: ['instructions', dbConnectionId],
    queryFn: () => instructionsApi.list(dbConnectionId!),
    enabled: !!dbConnectionId,
  });
}

export function useCreateInstruction() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: { db_connection_id: string; condition: string; rules: string; is_default?: boolean; metadata?: Record<string, unknown> }) =>
      instructionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructions'] });
      toast({ title: 'Instruction added' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to add instruction', description: error.message, variant: 'destructive' });
    },
  });
}

export function useUpdateInstruction() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { condition?: string; rules?: string; is_default?: boolean; metadata?: Record<string, unknown> } }) =>
      instructionsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructions'] });
      toast({ title: 'Instruction updated' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to update instruction', description: error.message, variant: 'destructive' });
    },
  });
}

export function useDeleteInstruction() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => instructionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructions'] });
      toast({ title: 'Instruction deleted' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to delete instruction', description: error.message, variant: 'destructive' });
    },
  });
}
