import type {
  ContextAsset,
  ContextAssetLifecycle,
  ContextAssetType,
  ArtifactPromotionRequest,
  ArtifactPromotionResponse,
  SubmitFeedbackRequest,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Context Asset API client for managing context assets.
 */
export const contextAssetApi = {
  /**
   * List context assets for a connection.
   */
  async listAssets(
    dbConnectionId: string,
    assetType?: ContextAssetType,
    lifecycleState?: ContextAssetLifecycle,
    limit: number = 100
  ): Promise<ContextAsset[]> {
    const params = new URLSearchParams({
      db_connection_id: dbConnectionId,
      limit: limit.toString(),
    });

    if (assetType) params.append('asset_type', assetType);
    if (lifecycleState) params.append('lifecycle_state', lifecycleState);

    const response = await fetch(`${API_BASE}/api/v1/context-assets?${params.toString()}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to list assets: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get a specific context asset.
   */
  async getAsset(
    dbConnectionId: string,
    assetType: ContextAssetType,
    canonicalKey: string,
    version: string = 'latest'
  ): Promise<ContextAsset> {
    const params = new URLSearchParams({
      db_connection_id: dbConnectionId,
      asset_type: assetType,
      canonical_key: canonicalKey,
      version,
    });

    const response = await fetch(`${API_BASE}/api/v1/context-assets/by-key?${params.toString()}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to get asset: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Create a new context asset in DRAFT state.
   */
  async createAsset(asset: {
    db_connection_id: string;
    asset_type: ContextAssetType;
    canonical_key: string;
    name: string;
    content?: Record<string, unknown>;
    content_text?: string;
    description?: string;
    author: string;
    tags?: string[];
  }): Promise<ContextAsset> {
    const response = await fetch(`${API_BASE}/api/v1/context-assets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(asset),
    });

    if (!response.ok) {
      throw new Error(`Failed to create asset: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Promote an asset from DRAFT to VERIFIED.
   */
  async promoteToVerified(
    assetId: string,
    promotedBy: string,
    changeNote?: string
  ): Promise<ContextAsset> {
    const response = await fetch(`${API_BASE}/api/v1/context-assets/${assetId}/promote/verified`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        promoted_by: promotedBy,
        change_note: changeNote,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to promote asset: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Promote an asset from VERIFIED to PUBLISHED.
   */
  async promoteToPublished(
    assetId: string,
    promotedBy: string,
    changeNote?: string
  ): Promise<ContextAsset> {
    const response = await fetch(`${API_BASE}/api/v1/context-assets/${assetId}/promote/published`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        promoted_by: promotedBy,
        change_note: changeNote,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to publish asset: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Deprecate a published asset.
   */
  async deprecateAsset(
    assetId: string,
    promotedBy: string,
    reason: string
  ): Promise<ContextAsset> {
    const response = await fetch(`${API_BASE}/api/v1/context-assets/${assetId}/deprecate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        promoted_by: promotedBy,
        reason,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to deprecate asset: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Promote a mission artifact to a context asset.
   */
  async promoteArtifact(
    request: ArtifactPromotionRequest
  ): Promise<ArtifactPromotionResponse> {
    const response = await fetch(`${API_BASE}/api/v1/context-assets/promote-artifact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to promote artifact: ${response.statusText}`);
    }

    return response.json();
  },
};

/**
 * Feedback API client for submitting feedback on missions and assets.
 */
export const feedbackApi = {
  /**
   * Submit feedback for a mission run.
   */
  async submitFeedback(request: SubmitFeedbackRequest): Promise<void> {
    const response = await fetch(`${API_BASE}/api/v1/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit feedback: ${response.statusText}`);
    }
  },
};
