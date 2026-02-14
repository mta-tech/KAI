'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight, Sparkles, CheckCircle2, Code, FileText, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { contextAssetApi } from '@/lib/api/context';
import type { MissionArtifact, ContextAssetType } from '@/lib/api/types';

interface ArtifactListProps {
  artifacts: MissionArtifact[];
  missionId: string;
  onPromoted?: (artifactId: string, assetId: string) => void;
}

function getArtifactIcon(type: MissionArtifact['type']) {
  switch (type) {
    case 'verified_sql':
      return <Code className="h-4 w-4 text-blue-500" />;
    case 'notebook':
      return <FileText className="h-4 w-4 text-purple-500" />;
    case 'summary':
      return <Sparkles className="h-4 w-4 text-emerald-500" />;
    case 'chart_config':
      return <BarChart3 className="h-4 w-4 text-orange-500" />;
    default:
      return <Sparkles className="h-4 w-4 text-gray-500" />;
  }
}

function getArtifactAssetType(artifactType: MissionArtifact['type']): ContextAssetType {
  switch (artifactType) {
    case 'verified_sql':
      return 'verified_sql';
    case 'notebook':
    case 'summary':
    case 'chart_config':
    default:
      return 'mission_template';
  }
}

export function ArtifactList({ artifacts, missionId, onPromoted }: ArtifactListProps) {
  const [expandedArtifact, setExpandedArtifact] = useState<string | null>(null);
  const [promoting, setPromoting] = useState<Set<string>>(new Set());

  const toggleExpand = (artifactId: string) => {
    setExpandedArtifact(expandedArtifact === artifactId ? null : artifactId);
  };

  const handlePromote = async (artifact: MissionArtifact) => {
    if (artifact.is_verified) return;

    setPromoting(prev => new Set(prev).add(artifact.id));

    try {
      const result = await contextAssetApi.promoteArtifact({
        artifact_id: artifact.id,
        asset_type: getArtifactAssetType(artifact.type),
        title: artifact.title,
        description: artifact.description,
        change_note: `Promoted from mission ${missionId}`,
      });

      onPromoted?.(artifact.id, result.asset_id);
    } catch (error) {
      console.error('Failed to promote artifact:', error);
    } finally {
      setPromoting(prev => {
        const next = new Set(prev);
        next.delete(artifact.id);
        return next;
      });
    }
  };

  if (artifacts.length === 0) {
    return (
      <div className="text-sm text-muted-foreground italic">
        No artifacts produced in this mission.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {artifacts.map((artifact) => {
        const isExpanded = expandedArtifact === artifact.id;
        const isPromoting = promoting.has(artifact.id);

        return (
          <div
            key={artifact.id}
            className="rounded-lg border bg-card/50 overflow-hidden"
          >
            <div
              className="flex items-center gap-2 p-3 cursor-pointer hover:bg-accent/50 transition-colors"
              onClick={() => toggleExpand(artifact.id)}
            >
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </Button>
              {getArtifactIcon(artifact.type)}
              <span className="flex-1 font-medium text-sm">{artifact.title}</span>
              {artifact.is_verified ? (
                <div className="flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>Verified</span>
                </div>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                  disabled={isPromoting}
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePromote(artifact);
                  }}
                >
                  {isPromoting ? 'Promoting...' : 'Promote'}
                </Button>
              )}
            </div>

            {isExpanded && (
              <div className="border-t p-3 space-y-2">
                {artifact.description && (
                  <div className="text-sm text-muted-foreground">
                    {artifact.description}
                  </div>
                )}
                <div className="text-xs text-muted-foreground font-mono bg-muted/50 rounded p-2">
                  <pre className="whitespace-pre-wrap break-words">{artifact.content}</pre>
                </div>
                <div className="text-xs text-muted-foreground">
                  <div>Stage: {artifact.provenance.stage}</div>
                  <div>Time: {new Date(artifact.provenance.timestamp).toLocaleString()}</div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
