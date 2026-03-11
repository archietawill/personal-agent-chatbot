import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'SYNCHRON - AI Scheduling Assistant',
  description: 'Intelligent constraint-satisfaction agent for scheduling and planning',
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
