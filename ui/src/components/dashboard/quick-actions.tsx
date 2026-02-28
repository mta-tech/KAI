'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Database, MessageSquare, Table2, Layers } from 'lucide-react';

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Button asChild variant="outline" className="justify-start h-auto py-4 hover:bg-accent hover:text-accent-foreground transition-all duration-200 border-dashed hover:border-solid group">
          <Link href="/connections">
            <div className="flex items-center gap-3">
                <div className="bg-primary/10 p-2 rounded-md group-hover:bg-primary/20 transition-colors" aria-hidden="true">
                    <Database className="h-5 w-5 text-primary" />
                </div>
                <div className="flex flex-col items-start">
                    <span className="font-medium">Add Connection</span>
                    <span className="text-xs text-muted-foreground">Connect to new database</span>
                </div>
            </div>
          </Link>
        </Button>
        <Button asChild variant="outline" className="justify-start h-auto py-4 hover:bg-accent hover:text-accent-foreground transition-all duration-200 border-dashed hover:border-solid group">
          <Link href="/chat">
            <div className="flex items-center gap-3">
                <div className="bg-primary/10 p-2 rounded-md group-hover:bg-primary/20 transition-colors" aria-hidden="true">
                    <MessageSquare className="h-5 w-5 text-primary" />
                </div>
                <div className="flex flex-col items-start">
                    <span className="font-medium">Start Chat</span>
                    <span className="text-xs text-muted-foreground">New analysis session</span>
                </div>
            </div>
          </Link>
        </Button>
        <Button asChild variant="outline" className="justify-start h-auto py-4 hover:bg-accent hover:text-accent-foreground transition-all duration-200 border-dashed hover:border-solid group">
          <Link href="/schema">
            <div className="flex items-center gap-3">
                <div className="bg-primary/10 p-2 rounded-md group-hover:bg-primary/20 transition-colors" aria-hidden="true">
                     <Table2 className="h-5 w-5 text-primary" />
                </div>
                <div className="flex flex-col items-start">
                    <span className="font-medium">Browse Schema</span>
                    <span className="text-xs text-muted-foreground">Explore database tables</span>
                </div>
            </div>
          </Link>
        </Button>
        <Button asChild variant="outline" className="justify-start h-auto py-4 hover:bg-accent hover:text-accent-foreground transition-all duration-200 border-dashed hover:border-solid group">
          <Link href="/mdl">
            <div className="flex items-center gap-3">
                <div className="bg-primary/10 p-2 rounded-md group-hover:bg-primary/20 transition-colors" aria-hidden="true">
                    <Layers className="h-5 w-5 text-primary" />
                </div>
                <div className="flex flex-col items-start">
                    <span className="font-medium">Manage MDL</span>
                    <span className="text-xs text-muted-foreground">Edit semantic layer</span>
                </div>
            </div>
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
