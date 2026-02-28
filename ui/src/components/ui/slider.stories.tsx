import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import { Slider } from './slider';
import { Label } from './label';

const meta = {
  title: 'UI/Slider',
  component: Slider,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    min: {
      control: 'number',
    },
    max: {
      control: 'number',
    },
    step: {
      control: 'number',
    },
    disabled: {
      control: 'boolean',
    },
  },
} satisfies Meta<typeof Slider>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    defaultValue: [50],
    max: 100,
    min: 0,
    step: 1,
  },
};

export const WithValue: Story = {
  render: () => {
    const [value, setValue] = React.useState([50]);
    return (
      <div className="w-[280px]">
        <Slider defaultValue={value} onValueChange={setValue} max={100} step={1} />
        <p className="text-sm text-muted-foreground mt-2">Value: {value[0]}</p>
      </div>
    );
  },
};

export const Range: Story = {
  render: () => {
    const [value, setValue] = React.useState([25, 75]);
    return (
      <div className="w-[280px]">
        <Slider defaultValue={value} onValueChange={setValue} max={100} step={1} />
        <p className="text-sm text-muted-foreground mt-2">
          Range: {value[0]} - {value[1]}
        </p>
      </div>
    );
  },
};

export const WithSteps: Story = {
  render: () => (
    <div className="w-[280px] space-y-8">
      <div>
        <Label htmlFor="step-5">Step: 5</Label>
        <Slider id="step-5" defaultValue={[40]} max={100} step={5} />
      </div>
      <div>
        <Label htmlFor="step-10">Step: 10</Label>
        <Slider id="step-10" defaultValue={[50]} max={100} step={10} />
      </div>
      <div>
        <Label htmlFor="step-25">Step: 25</Label>
        <Slider id="step-25" defaultValue={[75]} max={100} step={25} />
      </div>
    </div>
  ),
};

export const Disabled: Story = {
  args: {
    defaultValue: [50],
    max: 100,
    min: 0,
    step: 1,
    disabled: true,
  },
};

export const VolumeControl: Story = {
  render: () => {
    const [volume, setVolume] = React.useState([50]);
    return (
      <div className="w-[280px] space-y-2">
        <div className="flex justify-between">
          <Label htmlFor="volume">Volume</Label>
          <span className="text-sm text-muted-foreground">{volume[0]}%</span>
        </div>
        <Slider id="volume" defaultValue={volume} onValueChange={setVolume} max={100} step={1} />
      </div>
    );
  },
};

export const PriceRange: Story = {
  render: () => {
    const [price, setPrice] = React.useState([100, 500]);
    return (
      <div className="w-[320px] space-y-2">
        <Label>Price Range ($)</Label>
        <Slider defaultValue={price} onValueChange={setPrice} max={1000} step={10} />
        <p className="text-sm text-muted-foreground">
          ${price[0]} - ${price[1]}
        </p>
      </div>
    );
  },
};
