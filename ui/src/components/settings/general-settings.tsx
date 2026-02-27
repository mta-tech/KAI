'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';

interface GeneralSettingsProps {
  onChange: () => void;
}

export function GeneralSettings({ onChange }: GeneralSettingsProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Application</CardTitle>
          <CardDescription>Basic application preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Language</Label>
              <p className="text-sm text-muted-foreground">Select your preferred language</p>
            </div>
            <Select defaultValue="en" onValueChange={onChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="id">Bahasa Indonesia</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Timezone</Label>
              <p className="text-sm text-muted-foreground">Set your timezone</p>
            </div>
            <Select defaultValue="auto" onValueChange={onChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto-detect</SelectItem>
                <SelectItem value="utc">UTC</SelectItem>
                <SelectItem value="est">Eastern Time</SelectItem>
                <SelectItem value="pst">Pacific Time</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Data & Storage</CardTitle>
          <CardDescription>Manage your data preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Auto-save drafts</Label>
              <p className="text-sm text-muted-foreground">Automatically save work in progress</p>
            </div>
            <Switch defaultChecked onCheckedChange={onChange} />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Clear cache on exit</Label>
              <p className="text-sm text-muted-foreground">Remove cached data when closing</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
