'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { GlossaryList } from '@/components/knowledge/glossary-list';
import { InstructionList } from '@/components/knowledge/instruction-list';
import { useConnections } from '@/hooks/use-connections';
import { useGlossary, useInstructions } from '@/hooks/use-knowledge';

export default function KnowledgePage() {
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const { data: connections = [], isLoading: connectionsLoading } = useConnections();
  const { data: glossary = [], isLoading: glossaryLoading } = useGlossary(connectionId);
  const { data: instructions = [], isLoading: instructionsLoading } = useInstructions(connectionId);

  useEffect(() => {
    if (!connectionId && connections.length > 0) {
      setConnectionId(connections[0].id);
    }
  }, [connections, connectionId]);

  if (connectionsLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (connections.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">No database connections available.</p>
          <p className="text-sm text-muted-foreground">
            Create a database connection first to manage knowledge base.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-muted-foreground">
          Define business terms and instructions for AI-powered queries.
        </p>
        <Select value={connectionId || ''} onValueChange={setConnectionId}>
          <SelectTrigger className="w-64">
            <SelectValue placeholder="Select connection" />
          </SelectTrigger>
          <SelectContent>
            {connections.map((conn) => (
              <SelectItem key={conn.id} value={conn.id}>
                {conn.alias || conn.id.slice(0, 8)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Tabs defaultValue="glossary">
        <TabsList>
          <TabsTrigger value="glossary">Business Glossary ({glossary.length})</TabsTrigger>
          <TabsTrigger value="instructions">Instructions ({instructions.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="glossary" className="mt-4">
          {glossaryLoading ? (
            <div className="grid gap-4 md:grid-cols-2">
              <Skeleton className="h-32" />
              <Skeleton className="h-32" />
            </div>
          ) : (
            <GlossaryList items={glossary} connectionId={connectionId || ''} />
          )}
        </TabsContent>

        <TabsContent value="instructions" className="mt-4">
          {instructionsLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
            </div>
          ) : (
            <InstructionList items={instructions} connectionId={connectionId || ''} />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
