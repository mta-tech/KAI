import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from './collapsible';
import { Button } from './button';
import { ChevronDown } from 'lucide-react';

const meta = {
  title: 'UI/Collapsible',
  component: Collapsible,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Collapsible>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => {
    const [isOpen, setIsOpen] = React.useState(false);
    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen} className="w-[350px]">
        <CollapsibleTrigger asChild>
          <Button variant="ghost" className="w-full justify-between">
            Click to expand
            <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-2">
          <div className="rounded-md border p-4 text-sm">
            This is the collapsible content. It can contain any React component or text.
          </div>
        </CollapsibleContent>
      </Collapsible>
    );
  },
};

export const WithLongContent: Story = {
  render: () => {
    const [isOpen, setIsOpen] = React.useState(false);
    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen} className="w-[400px]">
        <CollapsibleTrigger asChild>
          <Button variant="outline" className="w-full justify-between">
            Read more details
            <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-2">
          <div className="rounded-md border p-4 text-sm space-y-2">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
            <p>Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco.</p>
          </div>
        </CollapsibleContent>
      </Collapsible>
    );
  },
};

export const NestedCollapsibles: Story = {
  render: () => {
    const [isOpen1, setIsOpen1] = React.useState(false);
    const [isOpen2, setIsOpen2] = React.useState(false);
    return (
      <div className="w-[350px] space-y-2">
        <Collapsible open={isOpen1} onOpenChange={setIsOpen1}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full justify-between">
              Section 1
              <ChevronDown className={`h-4 w-4 transition-transform ${isOpen1 ? 'rotate-180' : ''}`} />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-2">
            <div className="rounded-md border p-4 text-sm">
              Content for section 1
            </div>
          </CollapsibleContent>
        </Collapsible>
        <Collapsible open={isOpen2} onOpenChange={setIsOpen2}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full justify-between">
              Section 2
              <ChevronDown className={`h-4 w-4 transition-transform ${isOpen2 ? 'rotate-180' : ''}`} />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-2">
            <div className="rounded-md border p-4 text-sm">
              Content for section 2
            </div>
          </CollapsibleContent>
        </Collapsible>
      </div>
    );
  },
};

export const FAQStyle: Story = {
  render: () => {
    const faqs = [
      { q: 'What is this component?', a: 'A collapsible section for content that can be expanded and collapsed.' },
      { q: 'How do I use it?', a: 'Import the Collapsible components and wrap your content with them.' },
      { q: 'Is it accessible?', a: 'Yes, it uses Radix UI primitives for full keyboard and screen reader support.' },
    ];
    return (
      <div className="w-[400px] space-y-2">
        {faqs.map((faq, i) => {
          const [isOpen, setIsOpen] = React.useState(false);
          return (
            <Collapsible key={i} open={isOpen} onOpenChange={setIsOpen}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between font-medium">
                  {faq.q}
                  <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-2">
                <div className="rounded-md border bg-muted/50 p-4 text-sm">
                  {faq.a}
                </div>
              </CollapsibleContent>
            </Collapsible>
          );
        })}
      </div>
    );
  },
};
