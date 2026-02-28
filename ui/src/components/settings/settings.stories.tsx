import type { Meta, StoryObj } from '@storybook/react';
import { GeneralSettings } from './general-settings';
import { AppearanceSettings } from './appearance-settings';
import { NotificationSettings } from './notification-settings';
import { ShortcutSettings } from './shortcut-settings';

// --- GeneralSettings ---
const generalMeta: Meta<typeof GeneralSettings> = {
  title: 'Settings/GeneralSettings',
  component: GeneralSettings,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
  args: { onChange: () => {} },
};
export default generalMeta;
type GeneralStory = StoryObj<typeof GeneralSettings>;
export const General: GeneralStory = {};

// --- AppearanceSettings ---
const appearanceMeta: Meta<typeof AppearanceSettings> = {
  title: 'Settings/AppearanceSettings',
  component: AppearanceSettings,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
  args: { onChange: () => {} },
};
export { appearanceMeta };
type AppearanceStory = StoryObj<typeof AppearanceSettings>;
export const Appearance: AppearanceStory = {};

// --- NotificationSettings ---
const notificationMeta: Meta<typeof NotificationSettings> = {
  title: 'Settings/NotificationSettings',
  component: NotificationSettings,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
  args: { onChange: () => {} },
};
export { notificationMeta };
type NotificationStory = StoryObj<typeof NotificationSettings>;
export const Notifications: NotificationStory = {};

// --- ShortcutSettings ---
const shortcutMeta: Meta<typeof ShortcutSettings> = {
  title: 'Settings/ShortcutSettings',
  component: ShortcutSettings,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
};
export { shortcutMeta };
type ShortcutStory = StoryObj<typeof ShortcutSettings>;
export const Shortcuts: ShortcutStory = {};
