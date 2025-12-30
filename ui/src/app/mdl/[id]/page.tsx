'use client';

import { use } from 'react';
import { useManifest, useExportManifest } from '@/hooks/use-mdl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Download, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function MDLDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: manifest, isLoading } = useManifest(id);
  const exportMutation = useExportManifest();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!manifest) {
    return <div>Manifest not found</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/mdl">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Link>
          </Button>
          <div>
            <h2 className="text-xl font-semibold">
              {manifest.name || `Manifest ${manifest.id.slice(0, 8)}`}
            </h2>
            <p className="text-sm text-muted-foreground">
              {manifest.catalog}.{manifest.schema}
            </p>
          </div>
        </div>
        <Button variant="outline" onClick={() => exportMutation.mutate(manifest.id)}>
          <Download className="mr-2 h-4 w-4" />
          Export JSON
        </Button>
      </div>

      <Tabs defaultValue="models">
        <TabsList>
          <TabsTrigger value="models">Models ({manifest.models.length})</TabsTrigger>
          <TabsTrigger value="relationships">
            Relationships ({manifest.relationships.length})
          </TabsTrigger>
          <TabsTrigger value="metrics">Metrics ({manifest.metrics.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="models" className="space-y-4">
          {manifest.models.map((model) => (
            <Card key={model.name}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  {model.name}
                  {model.primary_key && (
                    <Badge variant="outline">PK: {model.primary_key}</Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Column</TableHead>
                      <TableHead>Type</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {model.columns.map((col) => (
                      <TableRow key={col.name}>
                        <TableCell className="font-mono">{col.name}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">{col.type}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="relationships">
          <Card>
            <CardContent className="pt-6">
              {manifest.relationships.length === 0 ? (
                <p className="text-muted-foreground">No relationships defined</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Models</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Condition</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {manifest.relationships.map((rel) => (
                      <TableRow key={rel.name}>
                        <TableCell className="font-medium">{rel.name}</TableCell>
                        <TableCell>{rel.models.join(' → ')}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{rel.join_type}</Badge>
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {rel.condition}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metrics">
          <Card>
            <CardContent className="pt-6">
              {manifest.metrics.length === 0 ? (
                <p className="text-muted-foreground">No metrics defined</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Base Object</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {manifest.metrics.map((metric) => (
                      <TableRow key={metric.name}>
                        <TableCell className="font-medium">{metric.name}</TableCell>
                        <TableCell>{metric.base_object}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
