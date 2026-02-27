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

interface AppearanceSettingsProps {
  onChange: () => void;
}

export function AppearanceSettings({ onChange }: AppearanceSettingsProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Theme</CardTitle>
          <CardDescription>Customize the appearance</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Color Theme</Label>
              <p className="text-sm text-muted-foreground">Choose your preferred color scheme</p>
            </div>
            <Select defaultValue="system" onValueChange={onChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="system">System</SelectItem>
                <SelectItem value="light">Light</SelectItem>
                <SelectItem value="dark">Dark</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Accent Color</Label>
              <p className="text-sm text-muted-foreground">Primary color for the UI</p>
            </div>
            <Select defaultValue="indigo" onValueChange={onChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="indigo">Indigo</SelectItem>
                <SelectItem value="blue">Blue</SelectItem>
                <SelectItem value="green">Green</SelectItem>
                <SelectItem value="purple">Purple</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Compact Mode</Label>
              <p className="text-sm text-muted-foreground">Use smaller spacing</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Display</CardTitle>
          <CardDescription>Additional display options</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Show animations</Label>
              <p className="text-sm text-muted-foreground">Enable UI animations</p>
            </div>
            <Switch defaultChecked onCheckedChange={onChange} />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Reduce motion</Label>
              <p className="text-sm text-muted-foreground">Minimize animations for accessibility</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
