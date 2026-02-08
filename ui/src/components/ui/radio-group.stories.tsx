import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import { RadioGroup, RadioGroupItem } from './radio-group';
import { Label } from './label';

const meta = {
  title: 'UI/RadioGroup',
  component: RadioGroup,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof RadioGroup>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <RadioGroup defaultValue="option1">
      <div className="flex items-center space-x-2">
        <RadioGroupItem value="option1" id="r1" />
        <Label htmlFor="r1">Option 1</Label>
      </div>
      <div className="flex items-center space-x-2">
        <RadioGroupItem value="option2" id="r2" />
        <Label htmlFor="r2">Option 2</Label>
      </div>
      <div className="flex items-center space-x-2">
        <RadioGroupItem value="option3" id="r3" />
        <Label htmlFor="r3">Option 3</Label>
      </div>
    </RadioGroup>
  ),
};

export const WithDescription: Story = {
  render: () => (
    <RadioGroup defaultValue="small">
      <div className="flex items-start space-x-2">
        <RadioGroupItem value="small" id="size-small" className="mt-1" />
        <div className="grid gap-1.5">
          <Label htmlFor="size-small">Small</Label>
          <p className="text-sm text-muted-foreground">
            For individuals or small teams
          </p>
        </div>
      </div>
      <div className="flex items-start space-x-2">
        <RadioGroupItem value="medium" id="size-medium" className="mt-1" />
        <div className="grid gap-1.5">
          <Label htmlFor="size-medium">Medium</Label>
          <p className="text-sm text-muted-foreground">
            For growing teams and organizations
          </p>
        </div>
      </div>
      <div className="flex items-start space-x-2">
        <RadioGroupItem value="large" id="size-large" className="mt-1" />
        <div className="grid gap-1.5">
          <Label htmlFor="size-large">Large</Label>
          <p className="text-sm text-muted-foreground">
            For enterprise-scale operations
          </p>
        </div>
      </div>
    </RadioGroup>
  ),
};

export const Disabled: Story = {
  render: () => (
    <RadioGroup defaultValue="option1">
      <div className="flex items-center space-x-2">
        <RadioGroupItem value="option1" id="d1" />
        <Label htmlFor="d1">Available</Label>
      </div>
      <div className="flex items-center space-x-2">
        <RadioGroupItem value="option2" id="d2" disabled />
        <Label htmlFor="d2" className="opacity-50">Sold Out</Label>
      </div>
      <div className="flex items-center space-x-2">
        <RadioGroupItem value="option3" id="d3" disabled />
        <Label htmlFor="d3" className="opacity-50">Coming Soon</Label>
      </div>
    </RadioGroup>
  ),
};

export const Vertical: Story = {
  render: () => (
    <div className="grid gap-4">
      <RadioGroup defaultValue="option1">
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="option1" id="v1" />
          <Label htmlFor="v1">Option 1</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="option2" id="v2" />
          <Label htmlFor="v2">Option 2</Label>
        </div>
      </RadioGroup>

      <RadioGroup defaultValue="option1" className="flex flex-row gap-4">
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="option1" id="h1" />
          <Label htmlFor="h1">Horizontal 1</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="option2" id="h2" />
          <Label htmlFor="h2">Horizontal 2</Label>
        </div>
      </RadioGroup>
    </div>
  ),
};
