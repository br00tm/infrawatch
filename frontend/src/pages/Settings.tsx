import { useState } from 'react'
import Card, { CardHeader } from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import { useThemeStore } from '../stores/themeStore'
import { useAuthStore } from '../stores/authStore'

export default function Settings() {
  const { user } = useAuthStore()
  const { theme, setTheme } = useThemeStore()
  const [notifications, setNotifications] = useState({
    telegram: false,
    discord: true,
    email: true,
  })

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Manage your account and application preferences
        </p>
      </div>

      {/* Profile Settings */}
      <Card>
        <CardHeader title="Profile" subtitle="Update your personal information" />
        <div className="space-y-4 max-w-md">
          <Input label="Email" type="email" value={user?.email || ''} disabled />
          <Input label="Username" value={user?.username || ''} disabled />
          <Input label="Full Name" value={user?.full_name || ''} placeholder="Enter your full name" />
          <Button>Save Changes</Button>
        </div>
      </Card>

      {/* Theme Settings */}
      <Card>
        <CardHeader title="Appearance" subtitle="Customize the look and feel" />
        <div className="flex gap-4">
          {(['light', 'dark', 'system'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={`px-6 py-3 rounded-lg text-sm font-medium capitalize transition-colors ${
                theme === t
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader title="Notifications" subtitle="Configure alert notifications" />
        <div className="space-y-4">
          {Object.entries(notifications).map(([channel, enabled]) => (
            <div key={channel} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900 dark:text-white capitalize">{channel}</p>
                <p className="text-sm text-gray-500">
                  Receive alerts via {channel}
                </p>
              </div>
              <button
                onClick={() =>
                  setNotifications((prev) => ({ ...prev, [channel]: !enabled }))
                }
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  enabled ? 'bg-primary-600' : 'bg-gray-300 dark:bg-dark-border'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    enabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </Card>

      {/* API Keys */}
      <Card>
        <CardHeader title="API Configuration" subtitle="Configure external service integrations" />
        <div className="space-y-4 max-w-md">
          <Input
            label="Telegram Bot Token"
            type="password"
            placeholder="Enter your Telegram bot token"
          />
          <Input
            label="Discord Webhook URL"
            type="password"
            placeholder="Enter your Discord webhook URL"
          />
          <Button>Save Configuration</Button>
        </div>
      </Card>
    </div>
  )
}
