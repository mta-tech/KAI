import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import { Switch } from './switch';
import { Label } from './label';

const meta = {
  title: 'UI/Switch',
  component: Switch,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    checked: {
      control: 'boolean',
    },
  },
} satisfies Meta<typeof Switch>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <div className="flex items-center space-x-2">
      <Switch id="airplane-mode" />
      <Label htmlFor="airplane-mode">Airplane Mode</Label>
    </div>
  ),
};

export const Checked: Story = {
  render: () => (
    <div className="flex items-center space-x-2">
      <Switch id="notifications" defaultChecked />
      <Label htmlFor="notifications">Enable Notifications</Label>
    </div>
  ),
};

export const Disabled: Story = {
  render: () => (
    <div className="flex items-center space-x-2">
      <Switch id="disabled" disabled />
      <Label htmlFor="disabled" className="opacity-50">Disabled Switch</Label>
    </div>
  ),
};

export const FormExample: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <Label htmlFor="emails">Email Notifications</Label>
          <p className="text-sm text-muted-foreground">
            Receive emails about your activity
          </p>
        </div>
        <Switch id="emails" defaultChecked />
      </div>

      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <Label htmlFor="marketing">Marketing Emails</Label>
          <p className="text-sm text-muted-foreground">
            Receive emails about new features
          </p>
        </div>
        <Switch id="marketing" />
      </div>

      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <Label htmlFor="security">Security Alerts</Label>
          <p className="text-sm text-muted-foreground">
            Get notified of security events
          </p>
        </div>
        <Switch id="security" defaultChecked />
      </div>
    </div>
  ),
};

export const MultipleSwitches: Story = {
  render: () => (
    <div className="space-y-3">
      <div className="flex items-center space-x-2">
        <Switch id="wifi" defaultChecked />
        <Label htmlFor="wifi">Wi-Fi</Label>
      </div>
      <div className="flex items-center space-x-2">
        <Switch id="bluetooth" />
        <Label htmlFor="bluetooth">Bluetooth</Label>
      </div>
      <div className="flex items-center space-x-2">
        <Switch id="location" defaultChecked />
        <Label htmlFor="location">Location Services</Label>
      </div>
      <div className="flex items-center space-x-2">
        <Switch id="vpn" />
        <Label htmlFor="vpn">VPN</Label>
      </div>
    </div>
  ),
};
